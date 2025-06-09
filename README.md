# Cascade Linter - Usage Guide

[![Version](https://img.shields.io/badge/version-1.1.1-blue.svg)](./VERSION.txt)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

Professional Python code quality toolkit with enhanced dependency analysis and modern GUI interface.

## 🚀 Quick Start

### GUI Interface (Recommended)

```bash
# Launch the professional GUI interface
python enhanced_launcher.py --gui

# Alternative: Command line argument
python enhanced_launcher.py
```

### Command Line Interface

```bash
# Lint current directory with all stages
python -m cascade_linter

# Lint specific directory
python -m cascade_linter /path/to/your/project

# Quick lint (Ruff only)
python -m cascade_linter --ruff-only

# Full analysis with dependency insights
python -m cascade_linter --dependency-analysis
```

### Enhanced CLI

```bash
# Use the enhanced CLI for advanced features
python -m cascade_linter.cli_enhanced

# Enhanced dependency analysis with details
python -m cascade_linter.cli_enhanced --dependency-analysis --show-details

# Export dependency analysis
python -m cascade_linter.cli_enhanced --dependency-analysis --export-csv analysis.csv
```

## 📋 Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)

### Install Dependencies
```bash
cd cascade-linter
pip install -r requirements.txt
pip install -r requirements-gui.txt  # For GUI interface
```

### Verify Installation
```bash
python -m cascade_linter --help
python enhanced_launcher.py --help  # GUI launcher
```

## 🖥️ GUI Interface Features

The professional GUI interface provides:

- **🎨 Material Design**: Modern dark theme with beautiful widgets
- **📊 Real-time Progress**: Live progress tracking with animated donuts
- **📈 Analytics Dashboard**: Comprehensive code quality metrics
- **🔧 Auto Fix**: Safe automatic code fixes with preview
- **📋 Activity Logs**: Structured, colorized logging output
- **⚙️ Settings Management**: Configurable linter preferences
- **🎯 Export Options**: Results export in multiple formats

### GUI Quick Start

1. **Launch**: `python enhanced_launcher.py --gui`
2. **Add Directory**: Click "Add Directory" to select your Python project
3. **Run Analysis**: Choose "Run Analysis" for comprehensive linting
4. **View Results**: Check the Analytics tab for detailed metrics
5. **Auto Fix**: Use "Auto Fix" tab for safe automatic corrections

## �� Command Reference

### Basic Linting Commands

| Command | Description | Example |
|---------|-------------|---------|
| `python -m cascade_linter` | Lint current directory (all stages) | `python -m cascade_linter` |
| `python -m cascade_linter <path>` | Lint specific directory | `python -m cascade_linter /home/user/project` |
| `--ruff-only` | Run only Ruff linter | `python -m cascade_linter --ruff-only` |
| `--flake8-only` | Run only Flake8 linter | `python -m cascade_linter --flake8-only` |
| `--pylint-only` | Run only Pylint linter | `python -m cascade_linter --pylint-only` |
| `--bandit-only` | Run only Bandit security linter | `python -m cascade_linter --bandit-only` |
| `--mypy-only` | Run only MyPy type checker | `python -m cascade_linter --mypy-only` |

### Configuration Options

| Option | Description | Example |
|--------|-------------|---------|
| `--check-only` | Check-only mode (no auto-fixes) | `python -m cascade_linter --check-only` |
| `--unsafe-fixes` | Apply potentially unsafe fixes | `python -m cascade_linter --unsafe-fixes` |
| `--no-gitignore` | Don't respect .gitignore files | `python -m cascade_linter --no-gitignore` |
| `--config <file>` | Use custom config file | `python -m cascade_linter --config myconfig.toml` |
| `--debug` | Enable debug output | `python -m cascade_linter --debug` |
| `--verbose` | Enable verbose output | `python -m cascade_linter --verbose` |

### Output Formats

| Option | Description | Example |
|--------|-------------|---------|
| `--json` | Output in JSON format | `python -m cascade_linter --json` |
| `--json-pretty` | Pretty-printed JSON output | `python -m cascade_linter --json-pretty` |
| `--simple-output` | Simplified text output | `python -m cascade_linter --simple-output` |
| `--save-log <file>` | Save log to file | `python -m cascade_linter --save-log lint.log` |

## 🔍 Enhanced Dependency Analysis

### Basic Dependency Analysis

```bash
# Analyze project dependencies
python -m cascade_linter.cli_enhanced --dependency-analysis

# With detailed module breakdown
python -m cascade_linter.cli_enhanced --dependency-analysis --show-details
```

### Export Options

```bash
# Export to CSV
python -m cascade_linter.cli_enhanced --dependency-analysis --export-csv deps.csv

# Export dependency graph (DOT format)
python -m cascade_linter.cli_enhanced --dependency-analysis --export-graph deps.dot

# Pretty JSON output
python -m cascade_linter.cli_enhanced --dependency-analysis --json-pretty > analysis.json
```

### Advanced Features

```bash
# List missing docstrings
python -m cascade_linter.cli_enhanced --dependency-analysis --list-missing-docstrings

# Custom risk thresholds
python -m cascade_linter.cli_enhanced --dependency-analysis --config-thresholds config.json

# Disable MyPy analysis
python -m cascade_linter.cli_enhanced --dependency-analysis --no-mypy-analysis
```

## 📊 Understanding Output

### Risk Categories

- **🔴 CRITICAL**: Modules with high impact (imported by 6+ modules)
- **🟠 HIGH**: Complex modules (15+ dependencies) or high impact score
- **🟡 MEDIUM**: Modules with moderate complexity (3+ importers OR 8+ imports)
- **🟢 LOW**: Standard modules with normal dependencies

### Health Score

The health score (0-100) is calculated based on:
- Critical modules: -20 points each
- High-risk modules: -10 points each  
- Medium-risk modules: -5 points each
- MyPy errors: Additional penalty

### Example Output

```
✓ ENHANCED DEPENDENCY ANALYSIS REPORT
============================================================
Project: /home/user/my-project    Analysis time: 0.85s
Files: 42    Import relationships: 187    Local modules: 38
Modules by risk: ✗ 2 | ⚠ 4 | ℹ 8 | ✓ 24
✓ PROJECT HEALTH SCORE: 65/100 (2 critical modules, 3 MyPy errors)

ℹ PRIORITY ACTION ITEMS:
  • ✓ No circular dependencies detected
  • ⚠ 3 MyPy errors in auth_module (run with --show-errors)
  • ✗ 2 critical modules need refactoring (core, database)
  • ℹ Quick Win: ~5 modules likely missing docstrings
```

## 🎯 Common Use Cases

### 1. Pre-Commit Hook Setup

```bash
# Quick validation before commit
python -m cascade_linter --check-only --simple-output
```

### 2. CI/CD Integration

```bash
# Full analysis for CI pipeline
python -m cascade_linter --json-pretty > lint-results.json
python -m cascade_linter.cli_enhanced --dependency-analysis --export-csv deps.csv
```

### 3. Project Health Assessment

```bash
# Comprehensive project analysis
python -m cascade_linter.cli_enhanced --dependency-analysis --show-details --export-csv health-report.csv
```

### 4. Security Audit

```bash
# Focus on security issues
python -m cascade_linter --bandit-only --verbose
```

### 5. Code Quality Report

```bash
# Generate comprehensive quality report
python -m cascade_linter --json-pretty > quality-report.json
python -m cascade_linter.cli_enhanced --dependency-analysis --export-graph deps.dot
```

## ⚡ Performance Tips

### Speed Optimization

```bash
# Skip slow linters for quick checks
python -m cascade_linter --ruff-only

# Parallel processing (when available)
python -m cascade_linter --parallel

# Skip MyPy for faster analysis
python -m cascade_linter.cli_enhanced --dependency-analysis --no-mypy-analysis
```

### Large Projects

```bash
# Use timing information
python -m cascade_linter --timing

# Save logs for later analysis
python -m cascade_linter --save-log detailed-analysis.log
```

## 🛠️ Configuration

### Config File Example (cascade-linter.toml)

```toml
[tool.cascade-linter]
check_only = false
unsafe_fixes = false
respect_gitignore = true

[tool.cascade-linter.stages]
ruff = true
flake8 = true
pylint = true
bandit = true
mypy = true

[tool.cascade-linter.thresholds]
min_imported_by_for_high_risk = 6
min_impact_score_critical = 75
max_god_module_dependencies = 15
```

### Environment Variables

```bash
# Set default path
export CASCADE_LINTER_PATH="/path/to/default/project"

# Enable debug mode
export CASCADE_LINTER_DEBUG=1

# Set custom config
export CASCADE_LINTER_CONFIG="/path/to/config.toml"
```

## 🚨 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   # Ensure you're in the project directory
   cd /path/to/cascade-linter
   python -m cascade_linter
   ```

2. **Permission errors**
   ```bash
   # Check file permissions
   chmod +r your-project-files
   ```

3. **Large project timeouts**
   ```bash
   # Use selective linting
   python -m cascade_linter --ruff-only --flake8-only
   ```

4. **Missing dependencies**
   ```bash
   # Reinstall requirements
   pip install -r requirements.txt
   ```

### Debug Mode

```bash
# Enable verbose debugging
python -m cascade_linter --debug --verbose

# Check configuration
python -m cascade_linter.cli_enhanced --dependency-analysis --debug
```

## 📚 Additional Resources

- **Configuration Guide**: See `docs/CONFIGURATION.md`
- **Integration Examples**: See `docs/INTEGRATIONS.md`
- **Changelog**: See `CHANGELOG.md`
- **Contributing**: See `CONTRIBUTING.md`

## 💡 Tips & Best Practices

1. **Start Simple**: Begin with `--ruff-only` for quick feedback
2. **Use Dependencies**: Run `--dependency-analysis` for architecture insights
3. **Check Health**: Monitor the health score to track code quality trends
4. **Export Data**: Use CSV exports for spreadsheet analysis
5. **Integrate Early**: Add to pre-commit hooks and CI/CD pipelines

## 🎯 Next Steps

After running analysis:
1. **Address Critical Issues**: Fix modules marked as CRITICAL first
2. **Review Dependencies**: Look for circular dependencies and complex modules
3. **Improve Health Score**: Target medium-risk modules for refactoring
4. **Add Documentation**: Use `--list-missing-docstrings` to find undocumented modules
5. **Monitor Progress**: Run regularly to track improvements

---

## 🖥️ GUI vs CLI Decision Guide

**Use GUI when you want:**
- Visual progress tracking and real-time feedback
- Interactive analytics dashboard and metrics
- Point-and-click project management
- Export capabilities with visual previews

**Use CLI when you want:**
- Automation and scripting integration
- CI/CD pipeline integration
- Batch processing of multiple projects
- Lightweight operation without GUI dependencies

**For developers**: Both interfaces use the same core engine, so results are identical.
