"""
About Dialog Module
Shows application information, credits, and usage tips.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextBrowser
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class AboutDialog(QDialog):
    """
    About dialog with app information and credits.
    """

    VERSION = "1.1.0"

    def __init__(self, parent=None):
        """
        Initialize the about dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("About ClipGuard")
        self.setMinimumSize(500, 600)
        
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # App icon/logo (text-based)
        icon_label = QLabel("🛡️")
        icon_font = QFont()
        icon_font.setPointSize(64)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # App name
        name_label = QLabel("<h1>ClipGuard</h1>")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        # Version
        version_label = QLabel(f"<b>Version {self.VERSION}</b>")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(version_label)

        # Tagline
        tagline = QLabel("Protecting Your Privacy, One Copy at a Time")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet("font-style: italic; color: #888; margin-bottom: 20px;")
        layout.addWidget(tagline)

        # Information text browser
        info_browser = QTextBrowser()
        info_browser.setOpenExternalLinks(True)
        info_browser.setHtml(self._get_info_html())
        layout.addWidget(info_browser)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.setMinimumWidth(100)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _get_info_html(self) -> str:
        """
        Get HTML content for the info section.
        
        Returns:
            HTML string with app information
        """
        return """
        <style>
            body { font-family: sans-serif; }
            h3 { color: #2c3e50; margin-top: 20px; margin-bottom: 10px; }
            p { margin: 5px 0; line-height: 1.6; }
            ul { margin: 10px 0; padding-left: 25px; }
            li { margin: 5px 0; }
            .feature { color: #27ae60; font-weight: bold; }
            .note { background: #f8f9fa; padding: 10px; border-left: 3px solid #3498db; margin: 10px 0; }
        </style>

        <h3>📋 What is ClipGuard?</h3>
        <p>ClipGuard is a lightweight system tray application that automatically masks sensitive 
        information in your clipboard, protecting your privacy when copying and pasting data.</p>

        <h3>✨ Key Features</h3>
        <ul>
            <li><span class="feature">🔒 Auto-masking</span> - Emails, phones, IPs, credit cards, SSNs</li>
            <li><span class="feature">🧠 Smart detection</span> - Won't mask single intentional copies</li>
            <li><span class="feature">🔗 Link cleaning</span> - Removes tracking parameters from URLs</li>
            <li><span class="feature">⚙️ Customizable</span> - Add your own regex patterns</li>
            <li><span class="feature">🔄 Restore</span> - Recover original unmasked content anytime</li>
        </ul>

        <h3>🚀 Quick Tips</h3>
        <div class="note">
            <b>Right-click the tray icon</b> to access all features:<br>
            • Toggle monitoring on/off<br>
            • Restore original content<br>
            • Clean tracking links<br>
            • Customize masking rules
        </div>

        <h3>🛠️ Built With</h3>
        <ul>
            <li>PyQt6 - Modern GUI framework</li>
            <li>pyperclip - Cross-platform clipboard access</li>
            <li>Python 3 - Powerful and elegant</li>
        </ul>

        <h3>📖 Learn More</h3>
        <p>Check out the <b>README.md</b> file in the installation directory 
        for detailed documentation and usage guides.</p>

        <h3>💝 Open Source</h3>
        <p>ClipGuard is free and open source software. Contributions, bug reports, and feature 
        requests are welcome!</p>

        <p style="margin-top: 30px; text-align: center; color: #999; font-size: 11px;">
            Made with ❤️ for privacy-conscious Linux users
        </p>
        """

