# Cascade Linter - Quick Reference

## 🚀 Essential Commands

### GUI Interface (Recommended)
```bash
# Launch professional GUI interface
python enhanced_launcher.py --gui

# Launch with automatic project detection
python enhanced_launcher.py
```

### Command Line Interface
```bash
# Basic linting (all stages)
python -m cascade_linter

# Lint specific directory  
python -m cascade_linter /path/to/project

# Quick check (Ruff only)
python -m cascade_linter --ruff-only

# Enhanced dependency analysis
python -m cascade_linter.cli_enhanced --dependency-analysis --show-details
```

## 📊 Most Useful Options

### GUI Features
| Feature | Purpose |
|---------|---------|
| **Run Analysis** | Full project linting with visual progress |
| **Auto Fix** | Safe automatic code corrections |
| **Analytics Dashboard** | Visual metrics and code quality stats |
| **Activity Log** | Real-time structured logging output |
| **Export Results** | Save reports in multiple formats |

### CLI Options
| Command | Purpose |
|---------|---------|
| `--check-only` | No auto-fixes, just report issues |
| `--json-pretty` | Machine-readable output |
| `--dependency-analysis` | Analyze project architecture |
| `--export-csv analysis.csv` | Export results to spreadsheet |
| `--show-details` | Full module breakdown |
| `--debug` | Troubleshooting information |

## 🎯 Common Workflows

### Quick GUI Health Check
```bash
python enhanced_launcher.py --gui
# Then click "Run Analysis" → view real-time results
```

### Quick CLI Health Check
```bash
python -m cascade_linter --ruff-only --simple-output
```

### Full Project Analysis (GUI)
```bash
python enhanced_launcher.py --gui
# Use Analytics tab → Export to CSV for reports
```

### Full Project Analysis (CLI)
```bash
python -m cascade_linter.cli_enhanced --dependency-analysis --show-details --export-csv report.csv
```

### CI/CD Integration
```bash
python -m cascade_linter --check-only --json-pretty > results.json
```

## 📈 Understanding Output

- **🔴 CRITICAL**: High-impact modules (6+ dependencies)
- **🟡 MEDIUM**: Moderate complexity (3+ dependencies)  
- **🟢 LOW**: Normal modules
- **Health Score**: 0-100 (higher = better)

## 🛟 Need Help?

### GUI Help
- **In-app tooltips**: Hover over buttons and widgets
- **Activity Log**: Check for detailed error messages
- **Settings**: Configure linter preferences

### CLI Help
```bash
python -m cascade_linter --help
python -m cascade_linter.cli_enhanced --help
python enhanced_launcher.py --help
```

See `README.md` for complete documentation.
