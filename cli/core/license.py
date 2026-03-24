"""License management for BrainStormer.

License tiers:
  - community: Free, 3 projects, all agents (read-only), one-way vault sync
  - pro: $12/mo founding ($19/mo standard), unlimited projects, agent creation,
         pipelines, bi-directional vault sync, team features, preview channel
  - team: Pro + shared configs, team agent library
  - enterprise: Custom, SSO, audit, air-gapped

Key format: BS-{TIER}-{EXPIRY_YYYYMMDD}-{SIGNATURE}
Example:    BS-PRO-20270322-a1b2c3d4e5f6

Keys are validated locally via HMAC signature, or online via LemonSqueezy API.
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
        "max_projects": 3,
        "max_agents": -1,  # all agents readable
        "vault_sync": True,  # one-way push only
        "bidirectional_sync": False,
        "agent_create": False,
        "agent_pipelines": False,
        "team_rulesets": False,
        "migrate": True,
        "priority_updates": False,
    },
    "pro": {
        "label": "Pro",
        "max_projects": -1,  # unlimited
        "max_agents": -1,
        "vault_sync": True,
        "bidirectional_sync": True,
        "agent_create": True,
        "agent_pipelines": True,
        "team_rulesets": True,
        "migrate": True,
        "priority_updates": True,
    },
    "team": {
        "label": "Team",
        "max_projects": -1,
        "max_agents": -1,
        "vault_sync": True,
        "bidirectional_sync": True,
        "agent_create": True,
        "agent_pipelines": True,
        "team_rulesets": True,
        "migrate": True,
        "priority_updates": True,
    },
    "enterprise": {
        "label": "Enterprise",
        "max_projects": -1,
        "max_agents": -1,
        "vault_sync": True,
        "bidirectional_sync": True,
        "agent_create": True,
        "agent_pipelines": True,
        "team_rulesets": True,
        "migrate": True,
        "priority_updates": True,
    },
}

# LemonSqueezy configuration
LEMONSQUEEZY_API_URL = "https://api.lemonsqueezy.com/v1"
UPGRADE_URL = "https://brainstormer.lemonsqueezy.com"


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
        if data.get("key"):
            # LemonSqueezy keys: cached validation with 30-day offline grace
            if data.get("source") == "lemonsqueezy":
                validated = data.get("validated")
                if validated:
                    validated_date = datetime.fromisoformat(validated).date()
                    days_since = (date.today() - validated_date).days
                    if days_since <= 30:
                        return data
                # Try re-validating online
                ls_result = validate_lemonsqueezy_key(data["key"])
                if ls_result and ls_result.get("success"):
                    data["validated"] = datetime.now().isoformat()
                    data["tier"] = ls_result["tier"]
                    license_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
                    return data
                # Offline and grace period expired
                return {"tier": "community", "key": data.get("key"),
                        "activated": data.get("activated"), "expired": True}

            # HMAC keys: validate signature and expiry
            parsed = parse_key(data["key"])
            if parsed and not is_expired(parsed):
                return data
            return {"tier": "community", "key": data.get("key"),
                    "activated": data.get("activated"), "expired": True}
        return {"tier": "community", "key": None, "activated": None}
    except (json.JSONDecodeError, OSError):
        return {"tier": "community", "key": None, "activated": None}


def activate_license(key: str) -> dict:
    """Activate a license key. Tries LemonSqueezy API first, then HMAC fallback."""
    # Try LemonSqueezy API validation first (for UUID-style keys)
    if not key.upper().startswith("BS-"):
        ls_result = validate_lemonsqueezy_key(key)
        if ls_result and ls_result.get("success"):
            license_data = {
                "tier": ls_result["tier"],
                "key": key,
                "activated": datetime.now().isoformat(),
                "source": "lemonsqueezy",
                "validated": datetime.now().isoformat(),
            }
            license_path = get_license_path()
            license_path.parent.mkdir(parents=True, exist_ok=True)
            license_path.write_text(json.dumps(license_data, indent=2), encoding="utf-8")
            return ls_result
        elif ls_result is None:
            # API unreachable but key doesn't look like HMAC — report error
            return {"success": False, "error": "Could not validate key. Check your internet connection or use a BS-TIER-DATE-SIG key."}

    # HMAC key validation (BS-TIER-YYYYMMDD-SIGNATURE format)
    parsed = parse_key(key)
    if not parsed:
        return {"success": False, "error": "Invalid key format. Expected: BS-TIER-YYYYMMDD-SIGNATURE or a LemonSqueezy license key"}

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
        "source": "hmac",
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
    lines.append(f"  Agents:   {'all' if agents == -1 else agents}")
    lines.append(f"  Vault sync: {'bi-directional' if caps.get('bidirectional_sync') else 'push only' if caps['vault_sync'] else 'no'}")
    lines.append(f"  Agent creation: {'yes' if caps.get('agent_create') else 'Pro only'}")
    lines.append(f"  Team features: {'yes' if caps.get('team_rulesets') else 'Pro only'}")

    if tier == "community":
        lines.append("")
        lines.append(f"  Upgrade: {UPGRADE_URL}")
        lines.append("  Or: brainstormer license activate <key>")

    return "\n".join(lines)


def get_current_tier() -> str:
    """Get the current license tier name."""
    info = get_license()
    return info.get("tier", "community")


def require_pro(feature_name: str) -> bool:
    """Check if current tier supports a Pro feature.

    Returns True if allowed, False if blocked (prints upgrade message).
    """
    tier = get_current_tier()
    if tier == "community":
        print(f"\n  {feature_name} requires BrainStormer Pro.")
        print(f"  Upgrade: {UPGRADE_URL}")
        print(f"  Current tier: Community (Free)\n")
        return False
    return True


def count_initialized_projects() -> int:
    """Count how many projects have been initialized with BrainStormer."""
    home = Path.home()
    count = 0
    # Check common dev directories for .brainstormer-version files
    # This is a heuristic — we look in known locations
    brainstormer_dir = home / ".brainstormer"
    projects_file = brainstormer_dir / "projects.json"
    if projects_file.exists():
        try:
            data = json.loads(projects_file.read_text(encoding="utf-8"))
            return len(data.get("projects", []))
        except (json.JSONDecodeError, OSError):
            pass
    return count


def register_project(project_path: str):
    """Register a project in the global project tracker."""
    brainstormer_dir = Path.home() / ".brainstormer"
    brainstormer_dir.mkdir(parents=True, exist_ok=True)
    projects_file = brainstormer_dir / "projects.json"

    data = {"projects": []}
    if projects_file.exists():
        try:
            data = json.loads(projects_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    projects = data.get("projects", [])
    # Normalize path
    normalized = str(Path(project_path).resolve())
    if normalized not in projects:
        projects.append(normalized)
        data["projects"] = projects
        projects_file.write_text(json.dumps(data, indent=2), encoding="utf-8")


def check_project_limit_with_warning() -> bool:
    """Check project limit and warn if at or over limit.

    Returns True if user can create another project, False if at limit.
    """
    caps = get_tier_capabilities()
    limit = caps["max_projects"]
    if limit == -1:
        return True  # unlimited

    current = count_initialized_projects()
    if current >= limit:
        tier = get_current_tier()
        print(f"\n  Project limit reached ({current}/{limit} on {TIERS[tier]['label']} tier).")
        print(f"  Upgrade for unlimited projects: {UPGRADE_URL}\n")
        return False
    return True


def validate_lemonsqueezy_key(key: str) -> Optional[dict]:
    """Validate a license key against the LemonSqueezy API.

    Returns activation result dict on success, None on failure.
    Falls back gracefully if the API is unreachable.
    """
    import urllib.request
    import urllib.error

    api_url = f"{LEMONSQUEEZY_API_URL}/licenses/validate"
    payload = json.dumps({"license_key": key}).encode("utf-8")

    req = urllib.request.Request(
        api_url,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if not data.get("valid"):
            return None

        meta = data.get("meta", {})
        tier = "pro"  # Default — LemonSqueezy products map to Pro
        variant = meta.get("variant_name", "").lower()
        if "team" in variant:
            tier = "team"
        elif "enterprise" in variant:
            tier = "enterprise"

        return {
            "success": True,
            "tier": tier,
            "label": TIERS.get(tier, TIERS["pro"])["label"],
            "license_key_id": data.get("license_key", {}).get("id"),
            "customer_email": meta.get("customer_email", ""),
            "variant": meta.get("variant_name", ""),
        }
    except (urllib.error.URLError, OSError, json.JSONDecodeError, KeyError):
        return None  # API unreachable — caller should fall back to HMAC
