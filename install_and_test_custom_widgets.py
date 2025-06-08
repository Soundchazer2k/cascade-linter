#!/usr/bin/env python3
"""
Install and Test Custom Widgets - Cascade Linter Enhancement

This script:
1. Installs QT-PyQt-PySide-Custom-Widgets
2. Tests the installation
3. Runs the enhanced widgets demo
4. Provides feedback on integration status

Run: python install_and_test_custom_widgets.py
"""

import subprocess
import sys
import os


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()[:200]}...")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {e}")
        return False


def check_python_version() -> bool:
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"🐍 Python Version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 9:
        print("✅ Python version is compatible (3.9+)")
        return True
    else:
        print("❌ Python version too old. Need Python 3.9 or higher.")
        return False


def check_pyside6() -> bool:
    """Check if PySide6 is installed"""
    try:
        import PySide6

        print(f"✅ PySide6 is installed: {PySide6.__version__}")
        return True
    except ImportError:
        print("❌ PySide6 not found. Installing...")
        return run_command(
            "pip install --user PySide6>=6.5.0", "Installing PySide6 (user)"
        )


def install_custom_widgets() -> bool:
    """Install the QT-PyQt-PySide-Custom-Widgets library"""
    return run_command(
        "pip install --user --upgrade QT-PyQt-PySide-Custom-Widgets",
        "Installing QT-PyQt-PySide-Custom-Widgets (user)",
    )


def test_custom_widgets_import() -> bool:
    """Test if custom widgets can be imported"""
    print("\n🧪 Testing Custom Widgets Import...")

    test_imports = [
        "Custom_Widgets.QCustomArcLoader",
        "Custom_Widgets.QCustomSpinner",
        "Custom_Widgets.QCustom3CirclesLoader",
        "Custom_Widgets.QCustomModals",
        "Custom_Widgets.QCustomQDialog",
    ]

    success_count = 0
    for import_name in test_imports:
        try:
            module_parts = import_name.split(".")
            module = __import__(module_parts[0])
            for part in module_parts[1:]:
                module = getattr(module, part)
            print(f"   ✅ {import_name}")
            success_count += 1
        except ImportError as e:
            print(f"   ❌ {import_name} - {e}")
        except Exception as e:
            print(f"   ⚠️ {import_name} - {e}")

    print(
        f"\n📊 Import Test Results: {success_count}/{len(test_imports)} widgets available"
    )
    return success_count > 0


def test_enhanced_loaders() -> bool:
    """Test if our enhanced loaders work"""
    print("\n🔧 Testing Enhanced Loaders...")

    try:
        from cascade_linter.gui.widgets.enhanced_loaders import (
            EnhancedLoadingWidget,
            LinterStageLoader,
            CUSTOM_WIDGETS_AVAILABLE,
        )

        print("✅ Enhanced loaders imported successfully")
        print(f"   Custom widgets available: {CUSTOM_WIDGETS_AVAILABLE}")
        return True
    except ImportError as e:
        print(f"❌ Enhanced loaders import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Enhanced loaders error: {e}")
        return False


def run_demo() -> bool:
    """Run the enhanced widgets demo"""
    print("\n🎬 Launching Enhanced Widgets Demo...")

    demo_file = "test_enhanced_widgets_demo.py"
    if not os.path.exists(demo_file):
        print(f"❌ Demo file not found: {demo_file}")
        return False

    try:
        # Try to run the demo (non-blocking)
        import subprocess

        process = subprocess.Popen([sys.executable, demo_file])
        print(f"✅ Demo launched successfully (PID: {process.pid})")
        print("   The demo window should open shortly...")
        return True
    except Exception as e:
        print(f"❌ Failed to launch demo: {e}")
        return False


def main() -> bool:
    """Main installation and testing procedure"""
    print("=" * 70)
    print("🚀 ENHANCED WIDGETS INSTALLATION & TESTING")
    print("   QT-PyQt-PySide-Custom-Widgets for Cascade Linter")
    print("=" * 70)

    # Step 1: Check Python version
    if not check_python_version():
        return False

    # Step 2: Check/Install PySide6
    if not check_pyside6():
        return False

    # Step 3: Install Custom Widgets
    if not install_custom_widgets():
        print("\n❌ INSTALLATION FAILED")
        print("   Trying alternative installation methods...")

        # Try alternative installation methods
        alt_methods = [
            "pip install --user --no-cache-dir QT-PyQt-PySide-Custom-Widgets",
            "python -m pip install --user QT-PyQt-PySide-Custom-Widgets",
            "py -m pip install --user QT-PyQt-PySide-Custom-Widgets",
        ]

        success = False
        for method in alt_methods:
            print(f"\n🔄 Trying: {method}")
            if run_command(method, "Alternative installation"):
                success = True
                break

        if not success:
            print("\n❌ ALL INSTALLATION METHODS FAILED")
            print("   Please try manual installation:")
            print("   1. Open Command Prompt as Administrator")
            print("   2. Run: pip install --user QT-PyQt-PySide-Custom-Widgets")
            print(
                "   3. Or try: python -m pip install --user QT-PyQt-PySide-Custom-Widgets"
            )
            return False

    # Step 4: Test Custom Widgets Import
    widgets_available = test_custom_widgets_import()

    # Step 5: Test Enhanced Loaders
    loaders_working = test_enhanced_loaders()

    # Step 6: Run Demo
    demo_launched = run_demo()

    # Final Status Report
    print("\n" + "=" * 70)
    print("📋 INSTALLATION & TESTING REPORT")
    print("=" * 70)

    print("✅ Python Version:        Compatible")
    print("✅ PySide6:              Installed")
    print(
        f"{'✅' if widgets_available else '❌'} Custom Widgets:      {'Available' if widgets_available else 'Failed'}"
    )
    print(
        f"{'✅' if loaders_working else '❌'} Enhanced Loaders:    {'Working' if loaders_working else 'Failed'}"
    )
    print(
        f"{'✅' if demo_launched else '❌'} Demo Launch:         {'Success' if demo_launched else 'Failed'}"
    )

    if widgets_available and loaders_working:
        print("\n🎉 SUCCESS! Custom Widgets Integration Complete!")
        print("\n📋 NEXT STEPS:")
        print("   1. The demo window should be open - explore the enhanced widgets")
        print("   2. Check the 'Installation Guide' tab for integration instructions")
        print("   3. Review the 'Integration Example' tab for code examples")
        print("   4. Your cascade-linter GUI can now use enhanced widgets!")
        print("\n💡 BENEFITS:")
        print("   ✨ Professional loading animations")
        print("   ✨ Advanced modal dialogs")
        print("   ✨ Responsive layout components")
        print("   ✨ Modern UI elements")
        print("   ✨ Graceful fallback if widgets unavailable")

    else:
        print("\n⚠️ PARTIAL SUCCESS - Some components may not be available")
        print(
            "   Your cascade-linter GUI will still work with fallback implementations"
        )

    print("\n🔗 RESOURCES:")
    print(
        "   📖 Documentation: https://khamisikibet.github.io/Docs-QT-PyQt-PySide-Custom-Widgets/"
    )
    print("   📦 GitHub: https://github.com/KhamisiKibet/QT-PyQt-PySide-Custom-Widgets")
    print("   🎥 Tutorials: Available on GitHub documentation")

    return widgets_available and loaders_working


if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)
