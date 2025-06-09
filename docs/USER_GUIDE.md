# 🚀 Cascade Linter GUI - User Guide

**Professional Code Quality Tool with Advanced GUI Interface**

---

## 📋 **Table of Contents**

1. [Quick Start](#quick-start)
2. [Interface Overview](#interface-overview)
3. [Run Analysis Tab](#run-analysis-tab)
4. [Analytics Tab](#analytics-tab)
5. [Settings & Themes](#settings--themes)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 **Quick Start**

### **First Launch**
1. **Launch the application**: `python enhanced_launcher.py --gui`
2. **Add directories**: Click "📂 Add Directory" or use **Ctrl+D**
3. **Select linters**: Choose from Ruff, Flake8, Pylint, Bandit, MyPy
4. **Run analysis**: Click "🚀 Run Analysis" or press **F5**
5. **View results**: Monitor progress and review activity log

### **5-Minute Tutorial**
```bash
# 1. Quick setup for your first project
cd "your-python-project"
python enhanced_launcher.py --gui

# 2. In the GUI:
#    - Add current directory (Ctrl+D)
#    - Use "⚡ Quick" preset (F1) for fastest results
#    - Click "🚀 Run Analysis" (F5)
#    - Watch progress donuts and activity log
```

---

## 🖥️ **Interface Overview**

### **Main Window Layout**
```
┌─── Menu Bar ────────────────────────────────────────┐
│ File | Tools | Settings | Help                      │
├─── Tab Bar ────────────────────────────────────────┤
│ [Run Analysis] [Analytics]                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ◀── Tab Content (varies by selection) ──▶          │
│                                                     │
├─── Status Bar ──────────────────────────────────────┤
│ Ready                                               │
└─────────────────────────────────────────────────────┘
```

### **Two Main Tabs**
- **Run Analysis**: Execute linting operations, view real-time progress
- **Analytics**: Explore dependency graphs, module breakdown, action items

---

## 🔍 **Run Analysis Tab**

### **Directory Management**
- **Add Directory**: Click "📂 Add Directory" or **Ctrl+D**
- **Remove Selected**: Select directory, click "🗑️ Remove Selected" or **Del**
- **Clear All**: Click "🧹 Clear All" or **Ctrl+Shift+C**

### **Linter Selection**
Choose which linters to run:
- **🦀 Ruff**: Fast Python linter and formatter (recommended)
- **🐍 Flake8**: Style guide enforcement
- **🔍 Pylint**: Deep code analysis (slower)
- **🛡️ Bandit**: Security vulnerability scanner
- **📝 MyPy**: Static type checker

### **Quick Presets**
- **⚡ Quick (F1)**: Ruff only - fastest analysis
- **🎯 Standard (F2)**: Ruff + Flake8 - good balance
- **🔍 Full (F3)**: All linters - comprehensive

### **Mode Selection**
- **🔧 Auto-Fix Mode**: Automatically fix issues where possible
- **🔍 Check-Only Mode**: Only report issues, don't fix them
- **⚡ Apply Unsafe Fixes**: Apply more aggressive fixes (use with caution)

### **Real-Time Progress**
- **Progress Bars**: Track each linter's progress (0-100%)
- **Metric Cards**: Live updates for Total Files, Issues Found, Auto-Fixed
- **Activity Log**: Detailed logging of all operations

---

## 📊 **Analytics Tab**

### **Dependency Risk Panel**
- **Visual Graph**: Dependency relationships and risk levels
- **Risk Levels**: 🔴 CRITICAL, 🟠 MEDIUM, 🟢 LOW
- **Interactive**: Click elements for detailed information

### **Module Breakdown Table**
- **Module Name**: All analyzed Python modules
- **Risk Assessment**: Color-coded risk levels
- **Sortable**: Click headers to sort by name or risk

### **Action Items Checklist**
- **Prioritized Tasks**: Based on analysis results
- **Checkboxes**: Track completion of improvements
- **Impact Scores**: Understand which items matter most

### **Export Options**
- **CSV Export**: Tabular data for spreadsheets
- **JSON Export**: Structured data for further analysis
- **DOT Export**: Dependency graph for visualization tools

---

## ⚙️ **Settings & Themes**

### **Opening Settings**
- **Menu**: Settings → Preferences
- **Keyboard**: No default shortcut (you can set one)

### **Theme System (9 Themes)**
1. **System Default**: Use OS theme
2. **Light**: Clean light theme
3. **Dark**: Professional dark theme
4. **Solarized Light**: Easy on eyes, light variant
5. **Solarized Dark**: Easy on eyes, dark variant  
6. **Dracula**: Popular purple-pink theme
7. **Dweeb**: Warm sepia/brown theme
8. **Retro Green**: Game Boy-inspired green
9. **Corps**: Teal and yellow theme

### **Settings Categories**

#### **General Tab**
- ☐ Check-only mode (no auto-fix)
- ☐ Apply unsafe fixes
- ☐ Respect .gitignore files
- Keep logs for [30] days
- Max log files [100]

#### **Linters Tab**
- ☐ Enable Ruff
- ☐ Enable Flake8
- ☐ Enable Pylint
- ☐ Enable Bandit
- ☐ Enable MyPy
- Max line length: [88]

#### **Interface Tab**
- Theme selection dropdown
- ☐ Enable animations
- Log font size: [10]
- ☐ Show line numbers
- ☐ Auto-scroll log

---

## ⌨️ **Keyboard Shortcuts**

### **File Operations**
- **Ctrl+O**: Open directory dialog
- **Ctrl+Q**: Exit application
- **Ctrl+D**: Add directory
- **Del**: Remove selected directory
- **Ctrl+Shift+C**: Clear all directories

### **Linting Operations**
- **F5**: Run analysis
- **F1**: Quick preset (Ruff only)
- **F2**: Standard preset (Ruff + Flake8)
- **F3**: Full preset (All linters)

### **Navigation**
- **Shift+F5**: Refresh analytics
- **Ctrl+E**: Export (context-dependent)
- **F1**: Switch to Issues Tab (when available)

### **General**
- **Esc**: Cancel current operation / Close dialogs

---

## 🔧 **Advanced Features**

### **Backend Integration**
- **Real Linter Execution**: Calls actual linter binaries
- **Progress Tracking**: Real-time updates from linter output
- **Error Handling**: Graceful handling of linter failures
- **Cancellation**: Stop long-running operations safely

### **Animation System**
- **Smooth Transitions**: 300ms easing curves for value changes
- **Progress Pulses**: Active linters show pulse animations
- **Hover Effects**: Interactive feedback on all UI elements
- **Theme Transitions**: Smooth switching between themes

### **Settings Persistence**
- **QSettings Integration**: Platform-native settings storage
- **Window State**: Remembers size, position, tab selection
- **Theme Preferences**: Persists selected theme across restarts
- **Linter Defaults**: Remembers your preferred linter combinations

### **Professional UX Features**
- **Status Bar**: Real-time operation feedback
- **Tooltips**: Helpful descriptions for all controls
- **Error Dialogs**: Clear error messages with suggested actions
- **Confirmation Dialogs**: Prevent accidental destructive operations

---

## 🐛 **Troubleshooting**

### **Common Issues**

#### **"Backend Not Available" Error**
**Problem**: Backend integration not working
**Solution**: 
1. Ensure all linters are installed: `pip install ruff flake8 pylint bandit mypy`
2. Check that linter binaries are in PATH
3. Restart the application

#### **Themes Not Loading**
**Problem**: Themes appear broken or don't apply
**Solution**:
1. Check that `assets/themes/` directory exists
2. Verify theme files are present (`.qss` extensions)
3. Try "System Default" theme as fallback

#### **Performance Issues**
**Problem**: GUI feels sluggish or unresponsive
**Solution**:
1. Disable animations in Settings → Interface
2. Use smaller directories for testing
3. Close other resource-intensive applications

#### **Linter Errors**
**Problem**: Specific linters fail to run
**Solution**:
1. Check Activity Log for specific error messages
2. Verify linter installation: `python -m ruff --version`
3. Try running linters individually in Quick presets

### **Debug Mode**
```bash
# Run with verbose logging
python enhanced_launcher.py --gui --debug

# Check linter installations
python -c "import subprocess; [print(f'{tool}: {subprocess.run([tool, \"--version\"], capture_output=True, text=True).stdout.strip()}') for tool in ['ruff', 'flake8', 'pylint', 'bandit', 'mypy']]"
```

### **Reset Settings**
If settings become corrupted:
```bash
# Remove settings (Windows)
reg delete "HKEY_CURRENT_USER\\Software\\CascadeLinter" /f

# Remove settings (Linux/Mac)  
rm -rf ~/.config/CascadeLinter/

# Or use the ConfigManager
python -c "from cascade_linter.gui.tools.ConfigManager import ConfigManager; ConfigManager.clear_all()"
```

### **Getting Help**
- **Activity Log**: Check for detailed error messages
- **About Dialog**: Help → About for version information
- **GitHub Issues**: Report bugs at project repository
- **Documentation**: Full developer guide in `docs/`

---

## 🎉 **Congratulations!**

You're now ready to use the Cascade Linter GUI effectively! This professional tool will help you maintain high code quality across all your Python projects.

**Pro Tips:**
- Start with Quick preset for daily use
- Use Full preset for important releases
- Check Analytics tab for architectural insights
- Experiment with themes to find your favorite
- Set up keyboard shortcuts for your workflow

Happy linting! ✨
