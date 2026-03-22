#!/usr/bin/env python3
"""BrainStormer License Key Generator.

Admin-only tool for generating HMAC-signed license keys.
NOT distributed with the product — kept server-side.

Usage:
    python -m cli.tools.keygen --tier pro --months 12
    python -m cli.tools.keygen --tier team --expires 2027-03-22
    python -m cli.tools.keygen --tier enterprise --months 12 --seats 50
    python -m cli.tools.keygen --tier pro --months 12 --batch 10

Key format: BS-{TIER}-{EXPIRY_YYYYMMDD}-{SIGNATURE}
Signature: first 12 chars of HMAC-SHA256(secret, "BS-{TIER}-{EXPIRY}")
"""

import argparse
import hashlib
import hmac
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Secret key for signing — loaded from env or keyfile
DEFAULT_KEYFILE = Path.home() / ".brainstormer" / "signing.key"


def get_signing_secret() -> str:
    """Load the HMAC signing secret from environment or keyfile."""
    # 1. Environment variable (preferred for CI/automation)
    secret = os.environ.get("BRAINSTORMER_SIGNING_KEY")
    if secret:
        return secret

    # 2. Keyfile on disk
    if DEFAULT_KEYFILE.exists():
        return DEFAULT_KEYFILE.read_text(encoding="utf-8").strip()

    return ""


def init_signing_key() -> str:
    """Generate and store a new signing key if none exists."""
    secret = get_signing_secret()
    if secret:
        return secret

    # Generate a new 64-char hex key
    secret = os.urandom(32).hex()
    DEFAULT_KEYFILE.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_KEYFILE.write_text(secret, encoding="utf-8")

    # Restrict permissions on Unix
    try:
        DEFAULT_KEYFILE.chmod(0o600)
    except OSError:
        pass  # Windows doesn't support Unix permissions

    print(f"  Generated new signing key: {DEFAULT_KEYFILE}")
    print(f"  BACK THIS UP — lost keys cannot regenerate existing licenses.")
    print()
    return secret


def generate_signature(secret: str, tier: str, expiry: str) -> str:
    """Generate HMAC-SHA256 signature for a license key."""
    message = f"BS-{tier.upper()}-{expiry}"
    sig = hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    # Return first 12 chars (sufficient for offline validation, compact for users)
    return sig[:12].upper()


def generate_key(secret: str, tier: str, expiry_date: datetime) -> str:
    """Generate a complete license key."""
    expiry = expiry_date.strftime("%Y%m%d")
    signature = generate_signature(secret, tier, expiry)
    return f"BS-{tier.upper()}-{expiry}-{signature}"


def validate_key(secret: str, key: str) -> dict:
    """Validate a license key against the signing secret."""
    parts = key.strip().upper().split("-")
    if len(parts) != 4 or parts[0] != "BS":
        return {"valid": False, "error": "Invalid format"}

    tier = parts[1]
    expiry = parts[2]
    provided_sig = parts[3]

    expected_sig = generate_signature(secret, tier, expiry)
    if not hmac.compare_digest(provided_sig, expected_sig):
        return {"valid": False, "error": "Invalid signature"}

    try:
        expiry_date = datetime.strptime(expiry, "%Y%m%d")
    except ValueError:
        return {"valid": False, "error": "Invalid date"}

    expired = datetime.now() > expiry_date

    return {
        "valid": True,
        "tier": tier.lower(),
        "expiry": expiry_date.strftime("%Y-%m-%d"),
        "expired": expired,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate BrainStormer license keys (admin tool)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --tier pro --months 12
  %(prog)s --tier team --expires 2027-03-22
  %(prog)s --tier pro --months 12 --batch 5
  %(prog)s --validate BS-PRO-20270322-A1B2C3D4E5F6
  %(prog)s --init-key
        """,
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--tier", choices=["pro", "team", "enterprise"],
                       help="License tier to generate")
    group.add_argument("--validate", metavar="KEY",
                       help="Validate an existing license key")
    group.add_argument("--init-key", action="store_true",
                       help="Generate a new signing key (first-time setup)")

    parser.add_argument("--months", type=int, default=12,
                        help="License duration in months (default: 12)")
    parser.add_argument("--expires", metavar="YYYY-MM-DD",
                        help="Explicit expiry date (overrides --months)")
    parser.add_argument("--batch", type=int, default=1,
                        help="Number of keys to generate (default: 1)")
    parser.add_argument("--json", action="store_true",
                        help="Output in JSON format")

    args = parser.parse_args()

    # -- Init signing key --
    if args.init_key:
        secret = init_signing_key()
        if args.json:
            print(json.dumps({"keyfile": str(DEFAULT_KEYFILE), "exists": bool(secret)}))
        return 0

    # -- Validate a key --
    if args.validate:
        secret = get_signing_secret()
        if not secret:
            print("Error: No signing key found. Run --init-key first or set BRAINSTORMER_SIGNING_KEY.", file=sys.stderr)
            return 1

        result = validate_key(secret, args.validate)
        if args.json:
            print(json.dumps(result, indent=2))
        elif result["valid"]:
            status = "EXPIRED" if result["expired"] else "ACTIVE"
            print(f"  Key:     {args.validate}")
            print(f"  Status:  {status}")
            print(f"  Tier:    {result['tier']}")
            print(f"  Expires: {result['expiry']}")
        else:
            print(f"  INVALID: {result['error']}")
        return 0 if result["valid"] else 1

    # -- Generate keys --
    if not args.tier:
        parser.print_help()
        return 1

    secret = get_signing_secret()
    if not secret:
        print("No signing key found. Generating one now...")
        print()
        secret = init_signing_key()

    # Calculate expiry
    if args.expires:
        try:
            expiry_date = datetime.strptime(args.expires, "%Y-%m-%d")
        except ValueError:
            print(f"Error: Invalid date format '{args.expires}'. Use YYYY-MM-DD.", file=sys.stderr)
            return 1
    else:
        expiry_date = datetime.now() + timedelta(days=args.months * 30)

    keys = []
    for _ in range(args.batch):
        key = generate_key(secret, args.tier, expiry_date)
        keys.append(key)

    if args.json:
        output = {
            "tier": args.tier,
            "expiry": expiry_date.strftime("%Y-%m-%d"),
            "count": len(keys),
            "keys": keys,
        }
        print(json.dumps(output, indent=2))
    else:
        print()
        print(f"  BrainStormer License Keys")
        print(f"  {'=' * 50}")
        print(f"  Tier:    {args.tier.capitalize()}")
        print(f"  Expires: {expiry_date.strftime('%Y-%m-%d')}")
        print(f"  Count:   {len(keys)}")
        print()
        for key in keys:
            print(f"  {key}")
        print()
        if args.batch > 1:
            print(f"  Distribute these keys to customers.")
            print(f"  Activate: brainstormer license activate <key>")
            print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
