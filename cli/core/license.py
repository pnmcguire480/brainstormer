"""License management for BrainStormer.

License tiers:
  - community: Free, 1 project, 10 agents, no vault sync
  - pro: $29-49/mo, unlimited projects/agents, vault sync, priority updates
  - team: $19-39/seat/mo, pro + shared configs
  - enterprise: Custom, SSO, audit, air-gapped

Key format: BS-{TIER}-{EXPIRY_YYYYMMDD}-{SIGNATURE}
Example:    BS-PRO-20270322-a1b2c3d4e5f6

Keys are validated locally via HMAC signature. No network call needed.
"""

import hashlib
import hmac
import json
from datetime import datetime, date
from pathlib import Path
from typing import Optional


# Tiers and their capabilities
TIERS = {
    "community": {
        "label": "Community (Free)",
        "max_projects": 1,
        "max_agents": 10,
        "vault_sync": False,
        "migrate": True,
        "priority_updates": False,
    },
    "pro": {
        "label": "Pro",
        "max_projects": -1,  # unlimited
        "max_agents": -1,
        "vault_sync": True,
        "migrate": True,
        "priority_updates": True,
    },
    "team": {
        "label": "Team",
        "max_projects": -1,
        "max_agents": -1,
        "vault_sync": True,
        "migrate": True,
        "priority_updates": True,
    },
    "enterprise": {
        "label": "Enterprise",
        "max_projects": -1,
        "max_agents": -1,
        "vault_sync": True,
        "migrate": True,
        "priority_updates": True,
    },
}


def get_license_path() -> Path:
    """Get the path to the license file."""
    return Path.home() / ".brainstormer" / "license.json"


def get_license() -> dict:
    """Load the current license. Returns community tier if none found."""
    license_path = get_license_path()
    if not license_path.exists():
        return {"tier": "community", "key": None, "activated": None}

    try:
        data = json.loads(license_path.read_text(encoding="utf-8"))
        # Validate the stored key
        if data.get("key"):
            parsed = parse_key(data["key"])
            if parsed and not is_expired(parsed):
                return data
            # Key expired or invalid — fall back to community
            return {"tier": "community", "key": data.get("key"), "activated": data.get("activated"),
                    "expired": True}
        return {"tier": "community", "key": None, "activated": None}
    except (json.JSONDecodeError, OSError):
        return {"tier": "community", "key": None, "activated": None}


def activate_license(key: str) -> dict:
    """Activate a license key. Returns result dict."""
    parsed = parse_key(key)
    if not parsed:
        return {"success": False, "error": "Invalid key format. Expected: BS-TIER-YYYYMMDD-SIGNATURE"}

    if is_expired(parsed):
        return {"success": False, "error": f"License expired on {parsed['expiry']}"}

    tier = parsed["tier"]
    if tier not in TIERS:
        return {"success": False, "error": f"Unknown tier: {tier}"}

    # Save license
    license_data = {
        "tier": tier,
        "key": key,
        "activated": datetime.now().isoformat(),
        "expiry": parsed["expiry"],
    }

    license_path = get_license_path()
    license_path.parent.mkdir(parents=True, exist_ok=True)
    license_path.write_text(json.dumps(license_data, indent=2), encoding="utf-8")

    return {"success": True, "tier": tier, "label": TIERS[tier]["label"],
            "expiry": parsed["expiry"]}


def deactivate_license() -> bool:
    """Remove the current license."""
    license_path = get_license_path()
    if license_path.exists():
        license_path.unlink()
        return True
    return False


def _get_signing_secret() -> str:
    """Load the HMAC signing secret for key validation."""
    import os
    secret = os.environ.get("BRAINSTORMER_SIGNING_KEY", "")
    if secret:
        return secret
    keyfile = Path.home() / ".brainstormer" / "signing.key"
    if keyfile.exists():
        try:
            return keyfile.read_text(encoding="utf-8").strip()
        except OSError:
            return ""
    return ""


def _verify_signature(tier: str, expiry_str: str, provided_sig: str) -> bool:
    """Verify the HMAC signature on a license key.

    If no signing key is available, signature check is skipped (offline mode).
    """
    secret = _get_signing_secret()
    if not secret:
        # No signing key available — accept any well-formed key
        # This allows offline activation without the signing secret
        return len(provided_sig) >= 8

    message = f"BS-{tier.upper()}-{expiry_str}"
    expected = hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:12].upper()

    return hmac.compare_digest(provided_sig, expected)


def parse_key(key: str) -> Optional[dict]:
    """Parse a license key into its components.

    Format: BS-{TIER}-{YYYYMMDD}-{SIGNATURE}
    Signature is verified via HMAC when a signing key is available.
    """
    parts = key.strip().upper().split("-")
    if len(parts) != 4:
        return None
    if parts[0] != "BS":
        return None

    tier = parts[1].lower()
    expiry_str = parts[2]
    signature = parts[3]

    # Validate expiry date
    try:
        expiry = datetime.strptime(expiry_str, "%Y%m%d").strftime("%Y-%m-%d")
    except ValueError:
        return None

    # Verify HMAC signature
    if not _verify_signature(tier, expiry_str, signature):
        return None

    return {
        "tier": tier,
        "expiry": expiry,
        "signature": signature,
        "raw": key.strip(),
    }


def is_expired(parsed: dict) -> bool:
    """Check if a parsed key is expired."""
    try:
        expiry_date = datetime.strptime(parsed["expiry"], "%Y-%m-%d").date()
        return date.today() > expiry_date
    except (ValueError, KeyError):
        return True


def get_tier_capabilities(tier: str = None) -> dict:
    """Get capabilities for a tier."""
    if tier is None:
        license_info = get_license()
        tier = license_info.get("tier", "community")
    return TIERS.get(tier, TIERS["community"])


def check_capability(capability: str) -> bool:
    """Check if the current license has a specific capability."""
    caps = get_tier_capabilities()
    value = caps.get(capability)
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0  # -1 = unlimited, 0 = disabled
    return False


def check_agent_limit() -> tuple[bool, int]:
    """Check if the user can access more agents.

    Returns (allowed, limit). limit=-1 means unlimited.
    """
    caps = get_tier_capabilities()
    limit = caps["max_agents"]
    return (True, limit) if limit == -1 else (True, limit)


def check_project_limit() -> tuple[bool, int]:
    """Check if the user can create more projects.

    Returns (allowed, limit). limit=-1 means unlimited.
    """
    caps = get_tier_capabilities()
    limit = caps["max_projects"]
    return (True, limit) if limit == -1 else (True, limit)


def format_license_status() -> str:
    """Format the current license status for display."""
    info = get_license()
    tier = info.get("tier", "community")
    caps = TIERS.get(tier, TIERS["community"])
    lines = []

    lines.append(f"  License: {caps['label']}")

    if info.get("key"):
        # Mask the key for display
        key = info["key"]
        masked = key[:7] + "..." + key[-4:] if len(key) > 11 else key
        lines.append(f"  Key:     {masked}")

    if info.get("expiry"):
        lines.append(f"  Expires: {info['expiry']}")

    if info.get("expired"):
        lines.append("  Status:  EXPIRED — using Community features")
    elif info.get("activated"):
        lines.append(f"  Active since: {info['activated'][:10]}")

    # Show limits
    projects = caps["max_projects"]
    agents = caps["max_agents"]
    lines.append(f"  Projects: {'unlimited' if projects == -1 else projects}")
    lines.append(f"  Agents:   {'unlimited' if agents == -1 else agents}")
    lines.append(f"  Vault sync: {'yes' if caps['vault_sync'] else 'no'}")

    if tier == "community":
        lines.append("")
        lines.append("  Upgrade: brainstormer license activate <key>")

    return "\n".join(lines)
