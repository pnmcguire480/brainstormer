"""Opt-in telemetry for BrainStormer.

Telemetry is OFF by default. Users must explicitly opt in.
When enabled, sends anonymous usage events (command names, error types).
NEVER sends: code content, file contents, file paths, API keys, or project names.

Events are batched locally and flushed periodically.
"""

import json
import hashlib
import platform
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional


TELEMETRY_ENDPOINT = "https://telemetry.brainstormer.dev/v1/events"

# What we collect (when opted in):
#   - command name (e.g., "init", "status", "doctor")
#   - success/failure
#   - error type (class name only, no message)
#   - OS and Python version
#   - BrainStormer version
#   - anonymous machine ID (hashed)
#
# What we NEVER collect:
#   - file contents or paths
#   - code or project names
#   - API keys or secrets
#   - personal information


def get_telemetry_path() -> Path:
    """Get the telemetry data directory."""
    return Path.home() / ".brainstormer" / "telemetry"


def get_config_path() -> Path:
    """Get user config path."""
    return Path.home() / ".brainstormer" / "config.json"


def _load_config() -> dict:
    """Load user config."""
    path = get_config_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_config(config: dict):
    """Save user config."""
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")


def is_enabled() -> bool:
    """Check if telemetry is enabled. OFF by default."""
    config = _load_config()
    return config.get("telemetry", False) is True


def opt_in():
    """Enable telemetry."""
    config = _load_config()
    config["telemetry"] = True
    config["telemetry_opted_at"] = datetime.now().isoformat()
    _save_config(config)


def opt_out():
    """Disable telemetry and delete any stored events."""
    config = _load_config()
    config["telemetry"] = False
    config.pop("telemetry_opted_at", None)
    _save_config(config)

    # Delete stored events
    telemetry_dir = get_telemetry_path()
    if telemetry_dir.exists():
        for f in telemetry_dir.glob("*.jsonl"):
            f.unlink()


def get_machine_id() -> str:
    """Get an anonymous, stable machine identifier.

    Uses a locally-generated UUID (not hardware-derived).
    Stored in config so it persists across sessions.
    """
    config = _load_config()
    mid = config.get("machine_id")
    if not mid:
        mid = hashlib.sha256(uuid.uuid4().bytes).hexdigest()[:16]
        config["machine_id"] = mid
        _save_config(config)
    return mid


def record_event(command: str, success: bool = True,
                 error_type: Optional[str] = None):
    """Record a telemetry event (stored locally, flushed later).

    Only records if telemetry is opted in.
    """
    if not is_enabled():
        return

    try:
        from core.channels import get_current_version
    except ImportError:
        try:
            from cli.core.channels import get_current_version
        except ImportError:
            def get_current_version():
                return "unknown"

    event = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "mid": get_machine_id(),
        "cmd": command,
        "ok": success,
        "v": get_current_version(),
        "os": platform.system().lower(),
        "py": platform.python_version(),
    }

    if error_type:
        event["err"] = error_type

    # Append to daily file
    telemetry_dir = get_telemetry_path()
    telemetry_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.utcnow().strftime("%Y%m%d")
    event_file = telemetry_dir / f"{today}.jsonl"

    try:
        with open(event_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except OSError:
        pass  # Silently fail — telemetry must never break the CLI


def flush_events() -> int:
    """Send stored events to the telemetry endpoint. Returns count sent.

    Silently fails if offline or endpoint is unreachable.
    Deletes events after successful send.
    """
    if not is_enabled():
        return 0

    telemetry_dir = get_telemetry_path()
    if not telemetry_dir.exists():
        return 0

    event_files = list(telemetry_dir.glob("*.jsonl"))
    if not event_files:
        return 0

    # Collect all events
    events = []
    for f in event_files:
        try:
            for line in f.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        except (json.JSONDecodeError, OSError):
            continue

    if not events:
        return 0

    # Send batch
    try:
        import urllib.request

        payload = json.dumps({"events": events}).encode("utf-8")
        req = urllib.request.Request(
            TELEMETRY_ENDPOINT,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "brainstormer-cli",
            },
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)

        # Success — delete sent files
        for f in event_files:
            try:
                f.unlink()
            except OSError:
                pass

        return len(events)
    except Exception:
        return 0  # Silently fail


def format_telemetry_status() -> str:
    """Format telemetry status for display."""
    enabled = is_enabled()
    lines = [
        f"  Telemetry: {'enabled' if enabled else 'disabled (default)'}",
    ]

    if enabled:
        # Count pending events
        telemetry_dir = get_telemetry_path()
        pending = 0
        if telemetry_dir.exists():
            for f in telemetry_dir.glob("*.jsonl"):
                pending += sum(1 for _ in f.read_text(encoding="utf-8").splitlines() if _.strip())
        lines.append(f"  Pending events: {pending}")
        lines.append("  Collects: command names, success/failure, OS, version")
        lines.append("  Never collects: code, files, paths, keys, project names")
    else:
        lines.append("  Enable: brainstormer telemetry on")
        lines.append("  Anonymous usage data helps improve BrainStormer.")

    return "\n".join(lines)
