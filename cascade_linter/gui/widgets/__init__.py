# cascade_linter/gui/widgets/__init__.py
"""
GUI Widgets Package

Custom widgets for the Cascade Linter GUI following modern design principles
and Nielsen's usability heuristics.

Available Widgets:
- MetricCard: Display key metrics with icon, title, and value
- ProgressDonut: Circular progress indicator for linter stages
- LogViewer: Enhanced log viewer with HTML support (coming next)
"""

from .MetricCard import MetricCard
from .ProgressDonut import ProgressDonut
from .LogViewer import LogViewer

__all__ = [
    "MetricCard",
    "ProgressDonut",
    "LogViewer",
]
