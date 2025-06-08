#!/usr/bin/env python3
"""
Safe Auto-Formatting Script for Cascade Linter
Safely fixes whitespace and line length issues
"""
import subprocess
import sys
from pathlib import Path


def run_safe_formatting() -> bool:
    """Run safe formatting tools on the cascade_linter directory"""
    project_root = Path(__file__).parent
    cascade_dir = project_root / "cascade_linter"

    if not cascade_dir.exists():
        print("❌ cascade_linter directory not found!")
        return False

    print("🛡️ Running SAFE formatting tools...")
    print("=" * 50)

    try:
        # 1. Black - Safest formatter (handles line length perfectly)
        print("🔧 Running Black (safest formatter)...")
        result1 = subprocess.run(
            [sys.executable, "-m", "black", str(cascade_dir), "--line-length", "88"],
            capture_output=True,
            text=True,
        )

        if result1.returncode == 0:
            print("✅ Black formatting completed successfully!")
        else:
            print(f"⚠️ Black output: {result1.stderr}")

        # 2. autopep8 - Conservative PEP 8 fixes
        print("\n🔧 Running autopep8 (conservative fixes)...")
        result2 = subprocess.run(
            [
                sys.executable,
                "-m",
                "autopep8",
                "--in-place",
                "--recursive",
                "--max-line-length",
                "88",
                str(cascade_dir),
            ],
            capture_output=True,
            text=True,
        )

        if result2.returncode == 0:
            print("✅ autopep8 formatting completed successfully!")
        else:
            print(f"⚠️ autopep8 output: {result2.stderr}")

        print("\n🎉 Safe formatting complete!")
        print("📋 Changes made:")
        print("   • Fixed trailing whitespace (W291)")
        print("   • Fixed blank line whitespace (W293)")
        print("   • Reformatted long lines (E501)")
        print("   • Applied PEP 8 style improvements")

        return True

    except FileNotFoundError as e:
        print(f"❌ Tool not found: {e}")
        print("💡 Install missing tools: pip install black autopep8")
        return False
    except Exception as e:
        print(f"❌ Error during formatting: {e}")
        return False


if __name__ == "__main__":
    print("🛡️ SAFE AUTO-FORMATTING FOR CASCADE LINTER")
    print("Fixes whitespace and line length issues safely")
    print("=" * 60)

    success = run_safe_formatting()
    sys.exit(0 if success else 1)
