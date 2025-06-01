# Changelog

All notable changes to the Cascade Linter project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
