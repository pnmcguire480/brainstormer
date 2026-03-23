"""Release channel management for BrainStormer.

Channels:
  - stable: Weekly GA releases (default)
  - preview: Opt-in next-week builds, may have rough edges

Channel preference is stored in ~/.brainstormer/config.json.
Update checks use GitHub API to find the latest release for the channel.
"""

import json
from pathlib import Path
from typing import Optional

CHANNELS = {
    "stable": {
        "label": "Stable",
        "description": "Weekly GA releases — tested and verified",
        "tag_filter": lambda t: not t.endswith("-preview"),
    },
    "preview": {
        "label": "Preview",
        "description": "Next-week builds — opt-in, may have rough edges",
        "tag_filter": lambda t: True,  # preview users get everything
    },
}

DEFAULT_CHANNEL = "stable"


def get_user_config_path() -> Path:
    """Get the user-level BrainStormer config path."""
    return Path.home() / ".brainstormer" / "config.json"


def load_user_config() -> dict:
    """Load user-level config (channel, telemetry, etc.)."""
    config_path = get_user_config_path()
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_user_config(config: dict):
    """Save user-level config."""
    config_path = get_user_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")


def get_channel() -> str:
    """Get the current release channel."""
    config = load_user_config()
    channel = config.get("channel", DEFAULT_CHANNEL)
    return channel if channel in CHANNELS else DEFAULT_CHANNEL


def set_channel(channel: str) -> bool:
    """Set the release channel. Returns True if valid."""
    if channel not in CHANNELS:
        return False
    config = load_user_config()
    config["channel"] = channel
    save_user_config(config)
    return True


def get_current_version() -> str:
    """Get the currently installed version."""
    try:
        from importlib.metadata import version
        return version("brainstormer")
    except Exception:
        pass

    # Fallback: read pyproject.toml
    pyproject = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
    if pyproject.exists():
        for line in pyproject.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("version"):
                return line.split("=")[1].strip().strip('"')
    return "unknown"


def check_for_update(channel: Optional[str] = None) -> Optional[dict]:
    """Check GitHub for newer releases on the configured channel.

    Returns dict with update info, or None if up-to-date or offline.
    Does NOT make network calls if urllib is unavailable.
    """
    if channel is None:
        channel = get_channel()

    current = get_current_version()
    if current == "unknown":
        return None

    try:
        import urllib.request
        import ssl

        # GitHub API: list recent releases
        url = "https://api.github.com/repos/pnmcguire480/brainstormer/releases?per_page=10"
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={"User-Agent": "brainstormer-cli"})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
            releases = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None  # Offline or API error — silently skip

    tag_filter = CHANNELS[channel]["tag_filter"]

    for release in releases:
        tag = release.get("tag_name", "")
        if not tag.startswith("v"):
            continue
        version = tag[1:]  # strip 'v'

        if not tag_filter(tag):
            continue

        # Simple version comparison (works for YYYY.WW.patch)
        if version > current:
            return {
                "current": current,
                "latest": version,
                "tag": tag,
                "channel": channel,
                "url": release.get("html_url", ""),
                "body": release.get("body", "")[:500],
            }

    return None  # Up to date


def format_channel_status() -> str:
    """Format channel info for display."""
    channel = get_channel()
    info = CHANNELS[channel]
    current = get_current_version()
    lines = [
        f"  Channel: {info['label']}",
        f"  Version: {current}",
        f"  {info['description']}",
    ]
    return "\n".join(lines)
