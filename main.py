#!/usr/bin/env python3
"""
ClipGuard - Linux Clipboard Privacy Tool
Main application entry point with system tray integration.
"""

import sys
import pyperclip
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSlot, QObject

from clipboard_monitor import ClipboardMonitor
from masking_engine import MaskingEngine
from settings_manager import SettingsManager
from settings_dialog import SettingsDialog
from about_dialog import AboutDialog


class ClipGuardApp(QObject):
    """
    Main application class for ClipGuard.
    Manages system tray, clipboard monitoring, and masking logic.
    """

    def __init__(self):
        """Initialize the ClipGuard application."""
        super().__init__()
        
        # Initialize core components
        self.settings_manager = SettingsManager()
        self.masking_engine = MaskingEngine()
        self.clipboard_monitor = ClipboardMonitor()
        
        # State
        self.monitoring_active = self.settings_manager.get("monitoring_active", True)
        self.last_original_content = ""
        self.ignore_next_change = False  # Flag to prevent processing our own changes
        
        # Update masking engine with saved patterns
        self._update_masking_patterns()
        
        # Set up system tray
        self.setup_tray()
        
        # Connect signals (use decorator to ensure proper connection)
        self.clipboard_monitor.new_text_copied.connect(self._on_clipboard_change)
        
        # Start monitoring if enabled
        if self.monitoring_active:
            self.start_monitoring()

    def setup_tray(self):
        """Set up the system tray icon and menu."""
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon()
        self.update_tray_icon()
        
        # Create menu
        self.menu = QMenu()
        
        # Add styled menu
        self.menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 5px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 25px 8px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background: #ecf0f1;
                margin: 5px 10px;
            }
        """)
        
        # Status section
        status_action = QAction("📊 Status", self.menu)
        status_action.setEnabled(False)
        self.menu.addAction(status_action)
        
        # Start/Stop Monitoring action (toggleable)
        self.monitoring_action = QAction("⏸️  Stop Monitoring", self.menu)
        self.monitoring_action.triggered.connect(self.toggle_monitoring)
        self.menu.addAction(self.monitoring_action)
        
        self.menu.addSeparator()
        
        # Actions section
        actions_action = QAction("⚡ Quick Actions", self.menu)
        actions_action.setEnabled(False)
        self.menu.addAction(actions_action)
        
        # Restore Last Content action
        restore_action = QAction("🔄  Restore Last Content", self.menu)
        restore_action.triggered.connect(self.restore_last_content)
        self.menu.addAction(restore_action)
        
        # Clean Last Link action
        clean_link_action = QAction("🔗  Clean Last Link", self.menu)
        clean_link_action.triggered.connect(self.clean_last_link)
        self.menu.addAction(clean_link_action)
        
        self.menu.addSeparator()
        
        # Settings action
        settings_action = QAction("⚙️  Settings", self.menu)
        settings_action.triggered.connect(self.open_settings)
        self.menu.addAction(settings_action)
        
        # About action
        about_action = QAction("ℹ️  About ClipGuard", self.menu)
        about_action.triggered.connect(self.open_about)
        self.menu.addAction(about_action)
        
        self.menu.addSeparator()
        
        # Quit action
        quit_action = QAction("❌  Quit", self.menu)
        quit_action.triggered.connect(self.quit_app)
        self.menu.addAction(quit_action)
        
        # Set menu and show tray icon
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()

    def update_tray_icon(self):
        """Update the tray icon based on monitoring status."""
        # Create a simple colored icon to indicate status
        # Green = monitoring active, Gray = inactive
        from PyQt6.QtGui import QPixmap, QPainter, QColor
        from PyQt6.QtCore import Qt
        
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw circle
        if self.monitoring_active:
            color = QColor(46, 204, 113)  # Green
        else:
            color = QColor(149, 165, 166)  # Gray
        
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(8, 8, 48, 48)
        
        # Draw shield symbol
        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(QColor(255, 255, 255))
        shield_points = [
            (32, 16),
            (44, 22),
            (44, 36),
            (32, 48),
            (20, 36),
            (20, 22)
        ]
        from PyQt6.QtGui import QPolygon
        from PyQt6.QtCore import QPoint
        polygon = QPolygon([QPoint(x, y) for x, y in shield_points])
        painter.drawPolygon(polygon)
        
        painter.end()
        
        icon = QIcon(pixmap)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip(
            f"ClipGuard - {'Active' if self.monitoring_active else 'Inactive'}"
        )

    def start_monitoring(self):
        """Start clipboard monitoring."""
        if not self.clipboard_monitor.isRunning():
            self.clipboard_monitor.start()
        self.monitoring_active = True
        self.monitoring_action.setText("⏸️  Stop Monitoring")
        self.update_tray_icon()

    def stop_monitoring(self):
        """Stop clipboard monitoring."""
        self.monitoring_active = False
        self.monitoring_action.setText("▶️  Start Monitoring")
        self.update_tray_icon()

    def toggle_monitoring(self):
        """Toggle clipboard monitoring on/off."""
        if self.monitoring_active:
            self.stop_monitoring()
        else:
            self.start_monitoring()
        
        # Save state
        self.settings_manager.set("monitoring_active", self.monitoring_active)
        self.settings_manager.save()

    @pyqtSlot(str)
    def _on_clipboard_change(self, text: str):
        """
        Handle clipboard change events.
        
        Args:
            text: New clipboard content
        """
        if not self.monitoring_active:
            return
        
        # Check if we should ignore this change (we made it ourselves)
        if self.ignore_next_change:
            self.ignore_next_change = False
            return
        
        # Store original content for restore feature
        self.last_original_content = text
        
        # Apply masking
        masked_text, was_modified = self.masking_engine.mask_text(text)
        
        # Update clipboard if text was modified
        if was_modified:
            try:
                # Set flag to ignore the change we're about to make
                self.ignore_next_change = True
                pyperclip.copy(masked_text)
            except Exception as e:
                self.ignore_next_change = False  # Reset on error
                print(f"Error updating clipboard: {e}")

    def restore_last_content(self):
        """Restore the last original (unmasked) clipboard content."""
        if self.last_original_content:
            try:
                # Set flag to ignore the change we're about to make
                self.ignore_next_change = True
                pyperclip.copy(self.last_original_content)
                
                # Show preview in notification
                preview = self.last_original_content[:50]
                if len(self.last_original_content) > 50:
                    preview += "..."
                
                self.tray_icon.showMessage(
                    "🔄 Content Restored",
                    f"Original content restored:\n{preview}",
                    QSystemTrayIcon.MessageIcon.Information,
                    3000
                )
            except Exception as e:
                self.ignore_next_change = False  # Reset on error
                print(f"Error restoring clipboard: {e}")
        else:
            self.tray_icon.showMessage(
                "⚠️  No Content",
                "No content available to restore.\nCopy something with sensitive data first.",
                QSystemTrayIcon.MessageIcon.Warning,
                2500
            )

    def clean_last_link(self):
        """Clean tracking parameters from the current clipboard content."""
        try:
            current_text = pyperclip.paste()
            
            if not current_text or not current_text.strip():
                self.tray_icon.showMessage(
                    "ClipGuard",
                    "Clipboard is empty.",
                    QSystemTrayIcon.MessageIcon.Warning,
                    2000
                )
                return
            
            # Store original before cleaning
            self.last_original_content = current_text
            
            # Clean the link
            cleaned_url, was_modified = self.masking_engine.clean_link(current_text)
            
            if was_modified:
                # Set flag to ignore the change we're about to make
                self.ignore_next_change = True
                pyperclip.copy(cleaned_url)
                
                # Show preview of cleaned URL
                preview = cleaned_url[:60]
                if len(cleaned_url) > 60:
                    preview += "..."
                
                self.tray_icon.showMessage(
                    "🔗 Link Cleaned",
                    f"Tracking parameters removed!\n{preview}",
                    QSystemTrayIcon.MessageIcon.Information,
                    3000
                )
            else:
                self.tray_icon.showMessage(
                    "ℹ️  No Changes",
                    "No tracking parameters found in the URL.",
                    QSystemTrayIcon.MessageIcon.Information,
                    2500
                )
        except Exception as e:
            print(f"Error cleaning link: {e}")

    def open_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self.settings_manager)
        if dialog.exec():
            # Settings were saved, update masking engine
            self._update_masking_patterns()
            self.tray_icon.showMessage(
                "✅ Settings Saved",
                "Your masking rules have been updated.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )

    def open_about(self):
        """Open the about dialog."""
        dialog = AboutDialog()
        dialog.exec()

    def _update_masking_patterns(self):
        """Update the masking engine with current patterns from settings."""
        all_patterns = self.settings_manager.get_all_patterns()
        self.masking_engine.set_patterns(all_patterns)

    def quit_app(self):
        """Quit the application gracefully."""
        # Stop monitoring thread
        if self.clipboard_monitor.isRunning():
            self.clipboard_monitor.stop()
        
        # Quit application
        QApplication.quit()


def main():
    """Main entry point."""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running when windows are closed
    
    # Create and run ClipGuard
    clipguard = ClipGuardApp()
    
    # Show startup message
    clipguard.tray_icon.showMessage(
        "🛡️ ClipGuard Started",
        "Your clipboard is now protected!\nRight-click the icon for options.",
        QSystemTrayIcon.MessageIcon.Information,
        3000
    )
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

