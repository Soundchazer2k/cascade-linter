from typing import Dict, Optional


class BeginnerFriendlyHelpers:
    """
    Helper functions to make linting more approachable for rookie to intermediate coders.
    Provides plain-English explanations and suggestions for common error codes.
    """

    # Common error codes with beginner-friendly explanations
    ERROR_EXPLANATIONS = {
        # Ruff/Flake8 style errors (most common for beginners)
        "E501": {
            "what": "Line too long",
            "why": "Long lines are hard to read",
            "fix": "Break into multiple lines or use shorter variable names",
            "priority": "low",
            "auto_fixable": True,
        },
        "F401": {
            "what": "Unused import",
            "why": "Clutters code and slows startup",
            "fix": "Remove the import or use it somewhere",
            "priority": "medium",
            "auto_fixable": True,
        },
        "W291": {
            "what": "Trailing whitespace",
            "why": "Invisible but causes version control noise",
            "fix": "Enable 'trim whitespace on save' in your editor",
            "priority": "low",
            "auto_fixable": True,
        },
        "F841": {
            "what": "Unused variable",
            "why": "Suggests incomplete code or bugs",
            "fix": "Use the variable or remove the assignment",
            "priority": "medium",
            "auto_fixable": False,
        },
        "E302": {
            "what": "Missing blank lines",
            "why": "Python style guide requires spacing",
            "fix": "Add one more blank line before functions/classes",
            "priority": "low",
            "auto_fixable": True,
        },
        "F821": {
            "what": "Undefined name",
            "why": "Variable doesn't exist - will crash!",
            "fix": "Check spelling or import the missing module",
            "priority": "high",
            "auto_fixable": False,
        },
        # Pylint convention errors (common for beginners)
        "C0114": {
            "what": "Missing module docstring",
            "why": "Helps others understand your code",
            "fix": "Add triple-quoted description at top of file",
            "priority": "low",
            "auto_fixable": False,
        },
        "C0115": {
            "what": "Missing class docstring",
            "why": "Explains what your class does",
            "fix": "Add docstring right after 'class ClassName:'",
            "priority": "low",
            "auto_fixable": False,
        },
        "C0116": {
            "what": "Missing function docstring",
            "why": "Explains what your function does",
            "fix": "Add docstring right after 'def function_name():'",
            "priority": "low",
            "auto_fixable": False,
        },
        "C0103": {
            "what": "Invalid name style",
            "why": "Python has naming conventions",
            "fix": "Use snake_case for variables/functions, PascalCase for classes",
            "priority": "low",
            "auto_fixable": False,
        },
        # Security issues (important for beginners to understand)
        "B101": {
            "what": "Using assert in production code",
            "why": "Asserts can be disabled, breaking security",
            "fix": "Use 'if not condition: raise ValueError()' instead",
            "priority": "high",
            "auto_fixable": False,
        },
        "B608": {
            "what": "SQL injection risk",
            "why": "Could allow hackers to access your database",
            "fix": "Use parameterized queries or an ORM",
            "priority": "high",
            "auto_fixable": False,
        },
    }

    @classmethod
    def get_beginner_explanation(cls, error_code: str) -> Optional[Dict[str, object]]:
        """Get a beginner-friendly explanation for an error code"""
        return cls.ERROR_EXPLANATIONS.get(error_code)

    @classmethod
    def format_friendly_error_line(
        cls, error_code: str, message: str, line: int, column: int
    ) -> str:
        """
        Format an error line with beginner-friendly explanation

        Returns: HTML formatted string with explanation
        """
        explanation = cls.get_beginner_explanation(error_code)

        if explanation:
            # Color based on priority
            priority_colors = {
                "high": "#FF5722",  # Red - fix immediately
                "medium": "#FF9800",  # Orange - fix soon
                "low": "#2196F3",  # Blue - improve when you can
            }

            priority = explanation["priority"]
            color = priority_colors.get(priority, "#FF9800")

            # Icon based on auto-fixable status
            icon = "🔧" if explanation["auto_fixable"] else "👨‍💻"

            # Priority indicator
            priority_badge = {
                "high": "🚨 URGENT",
                "medium": "⚠️ SOON",
                "low": "💡 IMPROVE",
            }.get(priority, "⚠️")

            formatted_line = f"""
            <div style="margin: 4px 0; padding: 8px; background: rgba(255,255,255,0.1); border-left: 3px solid {color};">
                <span style="color: {color}; font-weight: bold;">
                    {icon} Line {line}:{column} [{error_code}] {message}
                </span><br>
                <span style="color: #daffd4; font-size: 11px;">
                    <strong>{priority_badge}</strong> • <strong>What:</strong> {explanation['what']} • 
                    <strong>Fix:</strong> {explanation['fix']}
                </span>
            </div>
            """

            return formatted_line
        else:
            # Fallback for unknown error codes
            return f"""
            <div style="margin: 4px 0; padding: 8px; background: rgba(255,255,255,0.1);">
                <span style="color: #FF9800;">
                    ❓ Line {line}:{column} [{error_code}] {message}
                </span><br>
                <span style="color: #daffd4; font-size: 11px;">
                    💡 <em>Search "{error_code} Python" to learn more about this error</em>
                </span>
            </div>
            """

    @classmethod
    def get_priority_summary(cls, error_codes: list) -> Dict[str, int]:
        """
        Analyze a list of error codes and return priority breakdown

        Returns: Dict with counts like {"high": 2, "medium": 5, "low": 12}
        """
        priority_counts = {"high": 0, "medium": 0, "low": 0, "unknown": 0}

        for code in error_codes:
            explanation = cls.get_beginner_explanation(code)
            if explanation:
                priority = explanation["priority"]
                priority_counts[priority] += 1
            else:
                priority_counts["unknown"] += 1

        return priority_counts

    @classmethod
    def get_top_3_tips_for_codes(cls, error_codes: list) -> list:
        """
        Given a list of error codes, return top 3 actionable tips for beginners
        """
        # Count occurrences of each error type
        code_counts = {}
        for code in error_codes:
            code_counts[code] = code_counts.get(code, 0) + 1

        # Sort by frequency and get top 3
        top_codes = sorted(code_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        tips = []
        for code, count in top_codes:
            explanation = cls.get_beginner_explanation(code)
            if explanation:
                tip = f"**Fix {count}x {code}**: {explanation['fix']}"
                if explanation["auto_fixable"]:
                    tip += " (Use Auto-Fix tab!)"
                tips.append(tip)
            else:
                tips.append(
                    f"**Research {code}**: Google '{code} Python lint' for help"
                )

        return tips

    @classmethod
    def generate_encouragement_message(
        cls, total_issues: int, auto_fixable: int
    ) -> str:
        """Generate an encouraging message for beginners based on their results"""

        if total_issues == 0:
            return (
                "🎉 **Perfect!** Your code is clean and follows Python best practices!"
            )

        elif auto_fixable >= total_issues * 0.8:  # 80%+ auto-fixable
            return f"✨ **Great news!** {auto_fixable} out of {total_issues} issues can be auto-fixed. Click the Auto-Fix tab!"

        elif total_issues <= 10:
            return f"🚀 **Almost there!** Only {total_issues} issues to fix. You're doing great!"

        elif total_issues <= 50:
            return f"💪 **Making progress!** {total_issues} issues found. Focus on the high-priority ones first!"

        else:
            return f"🎯 **Don't panic!** {total_issues} issues seems like a lot, but start with auto-fixes and work your way up!"

    @classmethod
    def suggest_learning_resources(cls, error_codes: list) -> list:
        """Suggest learning resources based on the types of errors found"""
        resources = []

        # Check for common patterns
        has_style_errors = any(code.startswith(("E", "W")) for code in error_codes)
        has_logic_errors = any(code.startswith("F") for code in error_codes)
        has_convention_errors = any(code.startswith("C") for code in error_codes)
        has_security_errors = any(code.startswith("B") for code in error_codes)

        if has_style_errors:
            resources.append("📖 **Learn PEP 8**: The official Python style guide")
            resources.append(
                "🛠️ **Setup auto-formatting**: Use Black or autopep8 in your editor"
            )

        if has_logic_errors:
            resources.append(
                "🐍 **Python Basics**: Review variable scope and import statements"
            )
            resources.append(
                "🔍 **IDE Setup**: Use an IDE that highlights undefined variables"
            )

        if has_convention_errors:
            resources.append("📝 **Documentation**: Learn to write good docstrings")
            resources.append("🏗️ **Code Organization**: Study Python project structure")

        if has_security_errors:
            resources.append(
                "🔒 **Security Basics**: Learn about common Python security pitfalls"
            )
            resources.append("📚 **OWASP Python**: Check the OWASP security guidelines")

        return resources[:3]  # Limit to top 3 suggestions
