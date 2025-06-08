#!/usr/bin/env python3
"""
Smart Unicode Logging Utilities for Cascade Linter
Cross-platform Unicode symbol support with Windows compatibility fallback

Implements the smart Unicode strategy from docs/Logging.md:
- Automatic detection and graceful degradation
- Beautiful Unicode on capable systems (✔ ⚠ ◉)
- Functional ASCII fallback for legacy Windows (+, !, *, X)
- Zero user configuration required
"""

import sys
import os
import subprocess


class SmartSymbols:
    """Smart Unicode symbols with automatic Windows compatibility fallback"""

    def __init__(self):
        self.unicode_supported = self._test_unicode_support()
        if self.unicode_supported:
            self._setup_utf8_environment()
            self._use_unicode_symbols()
        else:
            self._use_ascii_symbols()

    @property
    def symbol_type(self) -> str:
        """Get the current symbol type for debugging"""
        return "Unicode" if self.unicode_supported else "ASCII"

    def _test_unicode_support(self) -> bool:
        """Test if the current environment supports BMP Unicode symbols"""
        # Check environment override first
        if os.environ.get("CASCADE_FORCE_UNICODE") == "1":
            return True
        if os.environ.get("CASCADE_FORCE_ASCII") == "1":
            return False

        try:
            # Test BMP Unicode symbols (Windows-safe range)
            test_symbols = "✔ ⚠ ◉ ◦ ℹ ⏳ → ✖"

            # Try to encode using current stdout encoding
            encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
            test_symbols.encode(encoding)
            return True

        except (UnicodeEncodeError, UnicodeDecodeError, LookupError, AttributeError):
            return False

    def _setup_utf8_environment(self):
        """Configure UTF-8 environment for cross-platform Unicode support"""

        if sys.platform == "win32":
            try:
                # Try to set console to UTF-8 (Windows 10+ feature)
                subprocess.run(
                    ["chcp", "65001"],
                    shell=True,
                    capture_output=True,
                    check=False,
                    timeout=2,
                )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass  # Graceful failure - not critical

        # Configure Python UTF-8 mode
        if hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
                sys.stderr.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, OSError):
                pass  # Graceful failure

        # Set environment variable for subprocess calls
        os.environ["PYTHONUTF8"] = "1"

    def _use_unicode_symbols(self):
        """Use beautiful BMP Unicode symbols (cross-platform safe)"""
        self.CRITICAL = "✖"  # U+2716 Heavy Multiplication X
        self.HIGH = "⚠"  # U+26A0 Warning Sign
        self.MEDIUM = "◉"  # U+25C9 Fisheye
        self.LOW = "◦"  # U+25E6 White Bullet
        self.INFO = "ℹ"  # U+2139 Information Source
        self.SUCCESS = "✔"  # U+2714 Heavy Check Mark
        self.RUNNING = "⏳"  # U+23F3 Hourglass with Flowing Sand
        self.ARROW = "→"  # U+2192 Rightwards Arrow
        self.BULLET = "•"  # U+2022 Bullet
        self.INDENT = "  "  # Standard indent

        # Stage indicators
        self.STAGE_PENDING = "◦"  # Waiting
        self.STAGE_RUNNING = "⏳"  # In progress
        self.STAGE_SUCCESS = "✔"  # Completed successfully
        self.STAGE_ERROR = "✖"  # Failed
        self.STAGE_SKIPPED = "—"  # U+2014 Em Dash (skipped)

        # Dependency analysis specific symbols
        self.GRAPH = "🕸"  # U+1F578 Spider Web (or fallback to G)
        self.CYCLE = "🔄"  # U+1F504 Counterclockwise arrows (or fallback to C)

        # Try the emoji symbols, fallback to safe alternatives if encoding fails
        try:
            "🕸🔄".encode(getattr(sys.stdout, "encoding", "utf-8"))
        except (UnicodeEncodeError, UnicodeDecodeError):
            # Fallback to BMP symbols
            self.GRAPH = "⚭"  # U+26AD Marriage Symbol (graph-like)
            self.CYCLE = "↻"  # U+21BB Clockwise Open Circle Arrow

    def _use_ascii_symbols(self):
        """ASCII fallback symbols for legacy Windows systems"""
        self.CRITICAL = "X"
        self.HIGH = "!"
        self.MEDIUM = "*"
        self.LOW = "-"
        self.INFO = "i"
        self.SUCCESS = "+"
        self.RUNNING = "~"
        self.ARROW = "->"
        self.BULLET = "*"
        self.INDENT = "  "

        # Stage indicators
        self.STAGE_PENDING = "."
        self.STAGE_RUNNING = "~"
        self.STAGE_SUCCESS = "+"
        self.STAGE_ERROR = "X"
        self.STAGE_SKIPPED = "-"

        # Dependency analysis specific symbols
        self.GRAPH = "G"
        self.CYCLE = "C"


def setup_logging_environment() -> bool:
    """
    Setup logging environment and return Unicode support status

    Returns:
        bool: True if Unicode symbols are supported, False if using ASCII fallback
    """
    # Initialize symbols if not already done
    if not hasattr(setup_logging_environment, "_symbols_initialized"):
        global symbols
        symbols = SmartSymbols()
        setup_logging_environment._symbols_initialized = True

    # Enable debug output if requested
    if os.environ.get("CASCADE_DEBUG_UNICODE") == "1":
        print(f"Unicode support: {symbols.unicode_supported}", file=sys.stderr)
        print(f"Symbol type: {symbols.symbol_type}", file=sys.stderr)
        print(
            f"Test symbols: {symbols.SUCCESS} {symbols.CRITICAL} {symbols.HIGH}",
            file=sys.stderr,
        )

    return symbols.unicode_supported


# Global instance for easy access
symbols = SmartSymbols()


# Additional utility functions for dependency analysis
def format_dependency_chain(modules: list, max_length: int = 4) -> str:
    """Format a dependency chain with smart Unicode arrows"""
    if not modules:
        return ""

    # Truncate if too long
    if len(modules) > max_length:
        display_modules = modules[: max_length - 1] + ["..."]
    else:
        display_modules = modules

    return f" {symbols.ARROW} ".join(display_modules)


def format_impact_score(score: float) -> str:
    """Format an impact score with appropriate symbol"""
    if score >= 75:
        return f"{symbols.CRITICAL} {score:.1f}"
    elif score >= 50:
        return f"{symbols.HIGH} {score:.1f}"
    elif score >= 25:
        return f"{symbols.MEDIUM} {score:.1f}"
    else:
        return f"{symbols.LOW} {score:.1f}"


def format_progress_bar(current: int, total: int, width: int = 25) -> str:
    """Create a text progress bar using smart Unicode symbols"""
    if total == 0:
        return "[" + " " * width + "]"

    progress = current / total
    filled = int(progress * width)

    if symbols.unicode_supported:
        # Use Unicode block characters for smooth progress
        bar = "█" * filled + "░" * (width - filled)
    else:
        # ASCII fallback
        bar = "=" * filled + "-" * (width - filled)

    return f"[{bar}]"


def format_circular_dependency(cycle: list) -> str:
    """Format a circular dependency with appropriate symbols"""
    if not cycle:
        return ""

    # Show the cycle with arrows
    cycle_str = format_dependency_chain(cycle)

    # Add the closing arrow to show it's circular
    return f"{symbols.CYCLE} {cycle_str} {symbols.ARROW} {cycle[0]}"


def format_module_metrics(
    module: str, imports: int, imported_by: int, impact: float
) -> str:
    """Format module metrics in a consistent way"""
    return (
        f"{module}\n"
        f"{symbols.INDENT}Uses: {imports} modules | "
        f"Used by: {imported_by} modules | "
        f"Impact: {format_impact_score(impact)}"
    )


# Example usage and testing
if __name__ == "__main__":
    """Test the smart Unicode system"""

    print("=== Smart Unicode System Test ===")
    print(f"Unicode supported: {symbols.unicode_supported}")
    print(f"Symbol type: {symbols.symbol_type}")
    print()

    print("Basic symbols:")
    print(f"Success: {symbols.SUCCESS}")
    print(f"Error: {symbols.CRITICAL}")
    print(f"Warning: {symbols.HIGH}")
    print(f"Info: {symbols.INFO}")
    print(f"Running: {symbols.RUNNING}")
    print()

    print("Dependency analysis symbols:")
    print(f"Graph: {symbols.GRAPH}")
    print(f"Cycle: {symbols.CYCLE}")
    print(f"Arrow: {symbols.ARROW}")
    print()

    print("Formatting examples:")
    print(
        f"Dependency chain: {format_dependency_chain(['moduleA', 'moduleB', 'moduleC'])}"
    )
    print(f"Impact score: {format_impact_score(87.5)}")
    print(f"Progress bar: {format_progress_bar(7, 10)}")
    print(f"Circular dependency: {format_circular_dependency(['A', 'B', 'C'])}")
    print()

    print("Module metrics example:")
    print(format_module_metrics("myproject.models.user", 5, 12, 78.3))
