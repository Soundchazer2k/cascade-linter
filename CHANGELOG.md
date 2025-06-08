# Changelog

All notable changes to the Cascade Linter project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive CLI usage documentation (README.md)
- Quick start guide (QUICK_START.md) for essential commands
- Command reference tables for all CLI options
- Performance optimization tips and common workflows
- Configuration examples and troubleshooting guide
- Package execution support via `__main__.py`

### Fixed
- Package can now be executed with `python -m cascade_linter`
- All documented CLI commands verified as functional

## [1.1.1] - 2025-06-08

### Fixed
- **Auto Fix tab cache issue**: Fixed discrepancy between Run Analysis and Auto Fix tabs where Auto Fix was using stale session data
- **GitIgnore support**: Implemented proper .gitignore exclusion support in core linting engine to respect backup/ and other excluded directories
- **Accurate fix counting**: Auto Fix now shows actual fixes applied (before/after analysis) instead of estimated counts
- **Safe auto-fixing**: Removed unsafe fixes from default auto-fix behavior - now only applies safe transformations unless explicitly enabled

### Changed
- **File exclusions**: Enhanced exclude patterns to properly exclude backup directories, temporary files, and development artifacts
- **Auto Fix behavior**: Made auto-fixing conservative by default - only safe formatting and obvious fixes applied
- **Fresh analysis**: Auto Fix tab now runs fresh analysis instead of relying on cached session data for accurate results

### Removed
- **Development files cleanup**: Removed setup-related .md files that were only needed for initial GitHub repository setup:
  - `GITHUB_SETUP.md` - One-time repository setup instructions
  - `BACKEND_INTEGRATION_COMPLETE.md` - Development milestone reports
  - `COMPLETE_FIX_SUMMARY.md`, `UI_IMPROVEMENTS_SUMMARY.md` - Completion summaries
  - `BEAUTIFUL_WIDGETS_INTEGRATION_PLAN.md`, `ENHANCED_WIDGETS_INTEGRATION_GUIDE.md` - Development planning docs
  - Various temporary integration guides and setup documentation

### Technical  
- Enhanced .gitignore patterns to prevent future inclusion of development artifacts
- Added `coding_instructions/` to .gitignore (internal development use only)
- Improved Auto Fix reliability and accuracy with before/after issue counting
- Fixed core-to-GUI integration issues with gitignore exclusion support

## [1.1.0] - 2025-06-01

### Added
- Intelligent path abbreviation in CSV exports for better readability
- Comprehensive timestamp metadata in all export formats (CSV and JSON)
- Enhanced docstring detection with improved heuristics based on module complexity
- Generation metadata headers in CSV exports showing analysis time and project path
- Enhanced JSON exports with `generated_at` and `project_analyzed` fields

### Changed
- Improved MEDIUM risk categorization algorithm with refined thresholds
- Risk categorization now uses: `imported_by_count >= 3 OR imports_count > 8 OR impact_score > 25`
- Better path abbreviation logic: paths >25 chars show as `first_part...last_part`
- Enhanced docstring estimation targeting modules with LOC>100 OR imports>5 OR imported_by>0

### Fixed
- Grammar consistency in all output messages (proper singular/plural agreement)
- Fixed "critical modules" text to correctly show "1 critical module needs" vs "2 critical modules need"
- More accurate MEDIUM module count with enhanced threshold logic

### Technical
- Maintained 10/10 excellence rating from user feedback
- All micro-improvements from user feedback successfully implemented
- Backward compatible - no breaking changes
- Production-ready quality with enhanced usability

## [1.0.0] - 2025-06-01

### Added
- **Initial stable release** - Production-ready Cascade Linter
- Complete CLI linting pipeline (Ruff → Flake8 → Pylint → Bandit → MyPy)
- Enhanced dependency analysis with professional output
- Cross-platform compatibility (Windows, macOS, Linux)
- Rich terminal UI with progress indicators and Unicode symbols
- Comprehensive configuration system with multiple output formats
- Interactive and non-interactive operation modes
- JSON, CSV, and DOT export formats for dependency analysis
- Advanced dependency analysis with risk categorization (CRITICAL/HIGH/MEDIUM/LOW)
- Professional-grade reporting with actionable insights
- Module breakdown with impact scoring and justifications
- Circular dependency detection and reporting
- MyPy integration for type checking analysis
- Configurable thresholds for risk assessment
- Quick-fix suggestions and architectural smell detection

### Changed
- Migrated from development version (0.x.x) to stable production release
- Established stable CLI API for consistent usage

### Technical
- Complete PySide6 GUI foundation (ready for Phase 2 GUI development)
- Modular architecture with clean separation of concerns
- Structured logging with Rich integration
- Professional output formatting with Unicode symbols
- Cross-platform testing completed

---

## Version History Summary

- **v1.1.1** (2025-06-08): Auto Fix improvements, gitignore support, development file cleanup
- **v1.1.0** (2025-06-01): Enhanced dependency analyzer with micro-improvements  
- **v1.0.0** (2025-06-01): Initial stable production release

## Migration Guide

### From v1.0.0 to v1.1.0
No migration required - fully backward compatible. Enhanced output quality with:
- Better grammar in all messages
- More accurate risk categorization
- Improved export formats with timestamps
- Smarter path abbreviation in exports

## Future Roadmap

- **v1.2.x**: Additional CLI enhancements and optimizations
- **v2.0.0**: Full desktop GUI implementation (PySide6-based interface)
- **v2.1.x**: Advanced GUI features and integrations

## Support

For issues and feature requests, please refer to the project documentation or contact the development team.
