# Cascade Linter - Quick Reference

## 🚀 Essential Commands

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

| Command | Purpose |
|---------|---------|
| `--check-only` | No auto-fixes, just report issues |
| `--json-pretty` | Machine-readable output |
| `--dependency-analysis` | Analyze project architecture |
| `--export-csv analysis.csv` | Export results to spreadsheet |
| `--show-details` | Full module breakdown |
| `--debug` | Troubleshooting information |

## 🎯 Common Workflows

### Quick Health Check
```bash
python -m cascade_linter --ruff-only --simple-output
```

### Full Project Analysis
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

```bash
python -m cascade_linter --help
python -m cascade_linter.cli_enhanced --help
```

See `README.md` for complete documentation.
