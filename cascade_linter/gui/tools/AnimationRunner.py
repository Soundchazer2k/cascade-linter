# cascade_linter/gui/tools/AnimationRunner.py
"""
Animation Runner for Cascade Linter GUI

Manages simple animations and micro-interactions using PySide6.
Provides smooth transitions for progress indicators and UI feedback.

Usage:
    from cascade_linter.gui.tools.AnimationRunner import AnimationRunner
    
    # Create fade animation
    runner = AnimationRunner()
    runner.fade_in(widget, duration=300)
    
    # Create slide animation
    runner.slide_up(widget, distance=20, duration=200)
"""

from PySide6.QtCore import QObject, QPropertyAnimation, QEasingCurve, QRect, QTimer, Signal
from PySide6.QtWidgets import QWidget, QGraphicsEffect
from PySide6.QtGui import QColor
from typing import Optional, Callable
import weakref


class AnimationRunner(QObject):
    """
    Self-contained animation manager for GUI micro-interactions.
    
    Provides common animation patterns while following the Modern GUI Design Framework:
    - Keep animations subtle and fast (< 200ms)
    - Provide immediate feedback for user actions
    - Use eased transitions for natural feeling
    """
    
    # Signal emitted when animation completes
    animation_finished = Signal(str)  # animation_id
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._animations = {}  # Store active animations
        self._animation_counter = 0
        
    def fade_in(self, widget: QWidget, duration: int = 200, 
                start_opacity: float = 0.0, end_opacity: float = 1.0,
                callback: Optional[Callable] = None) -> str:
        """
        Fade in a widget smoothly.
        
        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            start_opacity: Starting opacity (0.0 = transparent)
            end_opacity: Ending opacity (1.0 = opaque)
            callback: Optional callback when animation finishes
            
        Returns:
            str: Animation ID for tracking
        """
        animation_id = self._get_next_id("fade_in")
        
        # Create opacity effect if needed
        effect = widget.graphicsEffect()
        if not hasattr(effect, 'setOpacity'):
            from PySide6.QtWidgets import QGraphicsOpacityEffect
            effect = QGraphicsOpacityEffect()
            widget.setGraphicsEffect(effect)
        
        # Create animation
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(start_opacity)
        animation.setEndValue(end_opacity)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Setup completion handling
        def on_finished():
            self._cleanup_animation(animation_id)
            if callback:
                callback()
            self.animation_finished.emit(animation_id)
        
        animation.finished.connect(on_finished)
        
        # Store and start animation
        self._animations[animation_id] = {
            'animation': animation,
            'widget': weakref.ref(widget),
            'type': 'fade_in'
        }
        
        animation.start()
        return animation_id
    
    def fade_out(self, widget: QWidget, duration: int = 200,
                 start_opacity: float = 1.0, end_opacity: float = 0.0,
                 callback: Optional[Callable] = None) -> str:
        """Fade out a widget smoothly."""
        return self.fade_in(widget, duration, start_opacity, end_opacity, callback)
    
    def slide_up(self, widget: QWidget, distance: int = 20, duration: int = 150,
                 callback: Optional[Callable] = None) -> str:
        """
        Slide widget up (useful for notifications, dialogs).
        
        Args:
            widget: Widget to animate
            distance: Distance to slide in pixels
            duration: Animation duration in milliseconds
            callback: Optional callback when animation finishes
            
        Returns:
            str: Animation ID for tracking
        """
        animation_id = self._get_next_id("slide_up")
        
        # Get current geometry
        current_geometry = widget.geometry()
        start_rect = QRect(current_geometry)
        end_rect = QRect(current_geometry)
        
        # Set start position (below final position)
        start_rect.moveTop(current_geometry.top() + distance)
        
        # Create animation
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setStartValue(start_rect)
        animation.setEndValue(end_rect)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Setup completion handling
        def on_finished():
            self._cleanup_animation(animation_id)
            if callback:
                callback()
            self.animation_finished.emit(animation_id)
        
        animation.finished.connect(on_finished)
        
        # Store and start animation
        self._animations[animation_id] = {
            'animation': animation,
            'widget': weakref.ref(widget),
            'type': 'slide_up'
        }
        
        # Set initial position and start
        widget.setGeometry(start_rect)
        animation.start()
        return animation_id
    
    def pulse_scale(self, widget: QWidget, scale_factor: float = 1.1, 
                    duration: int = 300, callback: Optional[Callable] = None) -> str:
        """
        Pulse animation that scales widget up and back down.
        
        Args:
            widget: Widget to animate
            scale_factor: Maximum scale (1.1 = 10% larger)
            duration: Total animation duration in milliseconds
            callback: Optional callback when animation finishes
            
        Returns:
            str: Animation ID for tracking
        """
        animation_id = self._get_next_id("pulse_scale")
        
        # Get current geometry
        original_geometry = widget.geometry()
        center = original_geometry.center()
        
        # Calculate scaled geometry
        scaled_width = int(original_geometry.width() * scale_factor)
        scaled_height = int(original_geometry.height() * scale_factor)
        scaled_geometry = QRect(0, 0, scaled_width, scaled_height)
        scaled_geometry.moveCenter(center)
        
        # Create scale up animation
        scale_up = QPropertyAnimation(widget, b"geometry")
        scale_up.setDuration(duration // 2)
        scale_up.setStartValue(original_geometry)
        scale_up.setEndValue(scaled_geometry)
        scale_up.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Create scale down animation
        scale_down = QPropertyAnimation(widget, b"geometry")
        scale_down.setDuration(duration // 2)
        scale_down.setStartValue(scaled_geometry)
        scale_down.setEndValue(original_geometry)
        scale_down.setEasingCurve(QEasingCurve.Type.InCubic)
        
        # Chain animations
        def start_scale_down():
            scale_down.start()
        
        def on_finished():
            self._cleanup_animation(animation_id)
            if callback:
                callback()
            self.animation_finished.emit(animation_id)
        
        scale_up.finished.connect(start_scale_down)
        scale_down.finished.connect(on_finished)
        
        # Store and start animation
        self._animations[animation_id] = {
            'animation': scale_up,  # Store first animation
            'animation2': scale_down,  # Store second animation
            'widget': weakref.ref(widget),
            'type': 'pulse_scale'
        }
        
        scale_up.start()
        return animation_id
    
    def progress_bounce(self, widget: QWidget, bounces: int = 3, 
                       distance: int = 5, duration: int = 400,
                       callback: Optional[Callable] = None) -> str:
        """
        Bounce animation for progress indicators.
        
        Args:
            widget: Widget to animate
            bounces: Number of bounces
            distance: Bounce distance in pixels
            duration: Total animation duration
            callback: Optional callback when animation finishes
            
        Returns:
            str: Animation ID for tracking
        """
        animation_id = self._get_next_id("progress_bounce")
        
        # Get current geometry
        original_geometry = widget.geometry()
        bounce_geometry = QRect(original_geometry)
        bounce_geometry.moveTop(original_geometry.top() - distance)
        
        # Create bounce animation
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setStartValue(original_geometry)
        animation.setEndValue(original_geometry)
        animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        
        # Set keyframes for bouncing effect
        animation.setKeyValueAt(0.25, bounce_geometry)
        animation.setKeyValueAt(0.5, original_geometry)
        animation.setKeyValueAt(0.75, bounce_geometry)
        
        # Setup completion handling
        def on_finished():
            self._cleanup_animation(animation_id)
            if callback:
                callback()
            self.animation_finished.emit(animation_id)
        
        animation.finished.connect(on_finished)
        
        # Store and start animation
        self._animations[animation_id] = {
            'animation': animation,
            'widget': weakref.ref(widget),
            'type': 'progress_bounce'
        }
        
        animation.start()
        return animation_id
    
    def hover_glow(self, widget: QWidget, glow_color: QColor, 
                   duration: int = 200, callback: Optional[Callable] = None) -> str:
        """
        Add a subtle glow effect on hover.
        
        Args:
            widget: Widget to animate
            glow_color: Color for the glow effect
            duration: Animation duration
            callback: Optional callback when animation finishes
            
        Returns:
            str: Animation ID for tracking
        """
        animation_id = self._get_next_id("hover_glow")
        
        # For now, implement as a simple border color change
        # In a full implementation, this could use QGraphicsDropShadowEffect
        
        original_style = widget.styleSheet()
        glow_style = f"""
            {original_style}
            border: 2px solid {glow_color.name()};
            border-radius: 4px;
        """
        
        # Create timer for style change (simple implementation)
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: widget.setStyleSheet(original_style))
        
        # Apply glow style
        widget.setStyleSheet(glow_style)
        
        # Setup completion handling
        def on_finished():
            self._cleanup_animation(animation_id)
            if callback:
                callback()
            self.animation_finished.emit(animation_id)
        
        timer.timeout.connect(on_finished)
        timer.start(duration)
        
        # Store animation info
        self._animations[animation_id] = {
            'timer': timer,
            'widget': weakref.ref(widget),
            'original_style': original_style,
            'type': 'hover_glow'
        }
        
        return animation_id
    
    def stop_animation(self, animation_id: str) -> bool:
        """
        Stop a specific animation.
        
        Args:
            animation_id: ID of animation to stop
            
        Returns:
            bool: True if animation was found and stopped
        """
        if animation_id in self._animations:
            anim_info = self._animations[animation_id]
            
            # Stop the animation
            if 'animation' in anim_info:
                anim_info['animation'].stop()
            if 'animation2' in anim_info:
                anim_info['animation2'].stop()
            if 'timer' in anim_info:
                anim_info['timer'].stop()
            
            self._cleanup_animation(animation_id)
            return True
        
        return False
    
    def stop_all_animations(self):
        """Stop all active animations."""
        animation_ids = list(self._animations.keys())
        for animation_id in animation_ids:
            self.stop_animation(animation_id)
    
    def is_animating(self, widget: QWidget = None) -> bool:
        """
        Check if animations are running.
        
        Args:
            widget: If provided, check only animations on this widget
            
        Returns:
            bool: True if animations are active
        """
        if widget is None:
            return len(self._animations) > 0
        
        # Check for animations on specific widget
        for anim_info in self._animations.values():
            widget_ref = anim_info.get('widget')
            if widget_ref and widget_ref() is widget:
                return True
        
        return False
    
    def _get_next_id(self, prefix: str) -> str:
        """Generate unique animation ID."""
        self._animation_counter += 1
        return f"{prefix}_{self._animation_counter}"
    
    def _cleanup_animation(self, animation_id: str):
        """Clean up completed animation."""
        if animation_id in self._animations:
            del self._animations[animation_id]


# Global animation runner instance for easy access
_global_animation_runner = None

def get_animation_runner() -> AnimationRunner:
    """Get global animation runner instance."""
    global _global_animation_runner
    if _global_animation_runner is None:
        _global_animation_runner = AnimationRunner()
    return _global_animation_runner


if __name__ == "__main__":
    # Test AnimationRunner functionality
    import sys
    from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
    
    app = QApplication(sys.argv)
    
    # Test window
    window = QWidget()
    window.setWindowTitle("AnimationRunner Test")
    window.resize(400, 300)
    window.setStyleSheet("background-color: #121212;")
    
    layout = QVBoxLayout(window)
    
    # Test buttons
    fade_btn = QPushButton("Test Fade Animation")
    slide_btn = QPushButton("Test Slide Animation")
    pulse_btn = QPushButton("Test Pulse Animation")
    bounce_btn = QPushButton("Test Bounce Animation")
    
    for btn in [fade_btn, slide_btn, pulse_btn, bounce_btn]:
        btn.setStyleSheet("""
            QPushButton {
                background-color: #357ABD;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4A90E2;
            }
        """)
        layout.addWidget(btn)
    
    # Create animation runner
    runner = AnimationRunner()
    
    # Connect button actions
    fade_btn.clicked.connect(lambda: runner.fade_out(fade_btn, 500, callback=lambda: runner.fade_in(fade_btn, 500)))
    slide_btn.clicked.connect(lambda: runner.slide_up(slide_btn, 30, 300))
    pulse_btn.clicked.connect(lambda: runner.pulse_scale(pulse_btn, 1.2, 400))
    bounce_btn.clicked.connect(lambda: runner.progress_bounce(bounce_btn, 2, 8, 600))
    
    # Show window
    window.show()
    
    print("AnimationRunner test window opened")
    print("Click buttons to test different animations")
    sys.exit(app.exec())
