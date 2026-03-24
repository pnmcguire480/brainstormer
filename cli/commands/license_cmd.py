"""brainstormer license — Manage license activation."""

import webbrowser

try:
    from cli.core.license import (
        activate_license,
        deactivate_license,
        format_license_status,
        UPGRADE_URL,
    )
except ImportError:
    from core.license import (
        activate_license,
        deactivate_license,
        format_license_status,
        UPGRADE_URL,
    )


def cmd_license(opts: dict) -> int:
    """Handle license subcommands."""
    positional = opts.get("positional", [])

    if not positional:
        # Show current license status
        print()
        print("  BrainStormer License")
        print("  " + "=" * 50)
        print()
        print(format_license_status())
        print()
        return 0

    action = positional[0]

    if action == "activate" and len(positional) > 1:
        key = positional[1]
        print()
        print("  Validating license key...")
        result = activate_license(key)
        if result["success"]:
            print(f"  License activated: {result['label']}")
            if result.get("expiry"):
                print(f"  Expires: {result['expiry']}")
        else:
            print(f"  {result['error']}")
        print()
        return 0 if result["success"] else 1

    elif action == "deactivate":
        print()
        if deactivate_license():
            print("  License deactivated. Using Community (free) tier.")
        else:
            print("  No license to deactivate.")
        print()
        return 0

    elif action == "status":
        print()
        print("  BrainStormer License")
        print("  " + "=" * 50)
        print()
        print(format_license_status())
        print()
        return 0

    elif action == "buy":
        print()
        print(f"  Opening BrainStormer Pro checkout...")
        print(f"  {UPGRADE_URL}")
        print()
        try:
            webbrowser.open(UPGRADE_URL)
        except Exception:
            print("  Could not open browser. Visit the URL above.")
        return 0

    else:
        print()
        print("  Usage:")
        print("    brainstormer license                  Show current license")
        print("    brainstormer license activate <key>   Activate a license key")
        print("    brainstormer license deactivate       Remove license")
        print("    brainstormer license status           Show license details")
        print("    brainstormer license buy              Open Pro checkout page")
        print()
        return 1
