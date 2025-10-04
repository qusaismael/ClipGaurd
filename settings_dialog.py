"""
Settings Dialog Module
GUI for managing masking rules and preferences.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QMessageBox, QHeaderView, QCheckBox,
    QTabWidget, QWidget, QGroupBox, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import re


class SettingsDialog(QDialog):
    """
    Dialog window for managing masking rules.
    Allows users to enable/disable rules and add custom patterns.
    """

    def __init__(self, settings_manager, parent=None):
        """
        Initialize the settings dialog.
        
        Args:
            settings_manager: SettingsManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("ClipGuard Settings")
        self.setMinimumSize(800, 600)
        
        # Apply modern styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QTabWidget::pane {
                border: 1px solid #dcdde1;
                background: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #dcdde1;
                color: #2f3640;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: white;
                color: #2c3e50;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: #e1e2e6;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton#deleteButton {
                background-color: #e74c3c;
            }
            QPushButton#deleteButton:hover {
                background-color: #c0392b;
            }
            QPushButton#cancelButton {
                background-color: #95a5a6;
            }
            QPushButton#cancelButton:hover {
                background-color: #7f8c8d;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dcdde1;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #2c3e50;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        self.setup_ui()
        self.load_patterns()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Header
        header = QLabel("🛡️  <b>ClipGuard Settings</b>")
        header_font = QFont()
        header_font.setPointSize(16)
        header.setFont(header_font)
        header.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(header)

        # Create tab widget
        tabs = QTabWidget()
        
        # Tab 1: Masking Rules
        rules_tab = self._create_rules_tab()
        tabs.addTab(rules_tab, "🔒 Masking Rules")
        
        # Tab 2: Help & Info
        help_tab = self._create_help_tab()
        tabs.addTab(help_tab, "❓ Help")
        
        layout.addWidget(tabs)

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_button = QPushButton("💾 Save & Close")
        save_button.setMinimumWidth(150)
        save_button.clicked.connect(self.save_and_close)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("cancelButton")
        cancel_button.setMinimumWidth(100)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _create_rules_tab(self) -> QWidget:
        """Create the masking rules tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Instructions
        instructions = QLabel(
            "✓ Check boxes to enable rules  |  ✗ Uncheck to disable  |  "
            "Built-in rules cannot be deleted"
        )
        instructions.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Table for displaying rules
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "✓", "Rule Name", "Pattern", "Replacement", "Actions"
        ])
        
        # Configure table
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #dcdde1;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 8px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #3498db;
            }
        """)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)

        # Add custom rule section
        custom_group = QGroupBox("➕ Add Custom Masking Rule")
        custom_layout = QVBoxLayout()
        
        # Input fields
        fields_layout = QHBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Rule Name (e.g., 'API Key')")
        self.name_input.setToolTip("Give your rule a descriptive name")
        fields_layout.addWidget(QLabel("Name:"))
        fields_layout.addWidget(self.name_input, 2)
        
        self.pattern_input = QLineEdit()
        self.pattern_input.setPlaceholderText("Regex Pattern (e.g., 'sk-[A-Za-z0-9]{32}')")
        self.pattern_input.setToolTip("Regular expression to match the sensitive data")
        fields_layout.addWidget(QLabel("Pattern:"))
        fields_layout.addWidget(self.pattern_input, 3)
        
        self.replacement_input = QLineEdit()
        self.replacement_input.setPlaceholderText("Replacement (e.g., '[REDACTED_API_KEY]')")
        self.replacement_input.setToolTip("Text to replace matches with")
        fields_layout.addWidget(QLabel("Replacement:"))
        fields_layout.addWidget(self.replacement_input, 2)
        
        add_button = QPushButton("➕ Add Rule")
        add_button.clicked.connect(self.add_custom_rule)
        fields_layout.addWidget(add_button)
        
        custom_layout.addLayout(fields_layout)
        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)

        tab.setLayout(layout)
        return tab

    def _create_help_tab(self) -> QWidget:
        """Create the help/info tab."""
        tab = QWidget()
        layout = QVBoxLayout()

        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <style>
            body { font-family: sans-serif; line-height: 1.6; }
            h3 { color: #2c3e50; margin-top: 15px; }
            code { background: #ecf0f1; padding: 2px 5px; border-radius: 3px; }
            .example { background: #e8f5e9; padding: 10px; border-left: 3px solid #4caf50; margin: 10px 0; }
            .note { background: #fff3cd; padding: 10px; border-left: 3px solid #ffc107; margin: 10px 0; }
        </style>

        <h2>📚 How to Use ClipGuard</h2>

        <h3>🔒 Built-in Masking Rules</h3>
        <p>ClipGuard comes with pre-configured rules to mask common sensitive data:</p>
        <ul>
            <li><b>Emails</b> - Replaces email addresses with <code>[REDACTED_EMAIL]</code></li>
            <li><b>Phone Numbers</b> - Replaces US phone numbers with <code>[REDACTED_PHONE]</code></li>
            <li><b>IP Addresses</b> - Replaces IPv4 addresses with <code>[REDACTED_IP]</code></li>
            <li><b>Credit Cards</b> - Replaces card numbers with <code>[REDACTED_CC]</code></li>
            <li><b>SSN</b> - Replaces social security numbers with <code>[REDACTED_SSN]</code></li>
        </ul>

        <h3>🧠 Smart Detection</h3>
        <div class="note">
            <b>Important:</b> ClipGuard only masks sensitive data when it's part of larger text. 
            If you copy JUST an email address alone, it won't be masked (we assume you copied it intentionally).
        </div>

        <h3>➕ Custom Rules</h3>
        <p>You can add your own masking rules using regular expressions:</p>
        
        <div class="example">
            <b>Example 1: API Keys</b><br>
            <b>Name:</b> OpenAI API Key<br>
            <b>Pattern:</b> <code>sk-[A-Za-z0-9]{48}</code><br>
            <b>Replacement:</b> <code>[REDACTED_API_KEY]</code>
        </div>

        <div class="example">
            <b>Example 2: Bitcoin Addresses</b><br>
            <b>Name:</b> Bitcoin Address<br>
            <b>Pattern:</b> <code>\\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\\b</code><br>
            <b>Replacement:</b> <code>[REDACTED_BTC]</code>
        </div>

        <div class="example">
            <b>Example 3: Employee IDs</b><br>
            <b>Name:</b> Employee ID<br>
            <b>Pattern:</b> <code>EMP-\\d{6}</code><br>
            <b>Replacement:</b> <code>[REDACTED_EMP_ID]</code>
        </div>

        <h3>💡 Tips</h3>
        <ul>
            <li>Test your regex patterns online before adding them</li>
            <li>Use <code>\\b</code> for word boundaries to match complete words only</li>
            <li>Escape special characters with backslash: <code>\\.</code> <code>\\-</code> <code>\\[</code></li>
            <li>Disable rules you don't need to improve performance</li>
        </ul>

        <h3>🔄 Other Features</h3>
        <p><b>Restore:</b> Right-click tray icon → "Restore Last Content" to get back unmasked text</p>
        <p><b>Link Cleaning:</b> Right-click tray icon → "Clean Last Link" to remove tracking from URLs</p>
        <p><b>Toggle:</b> Right-click tray icon → "Stop/Start Monitoring" to pause/resume protection</p>
        """)
        layout.addWidget(help_text)
        
        tab.setLayout(layout)
        return tab

    def load_patterns(self):
        """Load all patterns (built-in and custom) into the table."""
        self.table.setRowCount(0)
        
        builtin_patterns = self.settings_manager.get("builtin_patterns", {})
        custom_patterns = self.settings_manager.get("custom_patterns", {})
        
        # Load built-in patterns
        for name, data in builtin_patterns.items():
            self._add_pattern_row(name, data, is_custom=False)
        
        # Load custom patterns
        for name, data in custom_patterns.items():
            self._add_pattern_row(name, data, is_custom=True)

    def _add_pattern_row(self, name: str, data: dict, is_custom: bool):
        """
        Add a pattern row to the table.
        
        Args:
            name: Pattern name
            data: Pattern configuration
            is_custom: Whether this is a custom pattern
        """
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Enabled checkbox
        checkbox = QCheckBox()
        checkbox.setChecked(data.get("enabled", True))
        checkbox.stateChanged.connect(
            lambda state, n=name, c=is_custom: self.toggle_pattern(n, state, c)
        )
        checkbox_widget = QTableWidgetItem()
        self.table.setItem(row, 0, checkbox_widget)
        self.table.setCellWidget(row, 0, checkbox)
        
        # Name
        name_item = QTableWidgetItem(name)
        name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 1, name_item)
        
        # Pattern
        pattern_item = QTableWidgetItem(data["pattern"])
        pattern_item.setFlags(pattern_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 2, pattern_item)
        
        # Replacement
        replacement_item = QTableWidgetItem(data["replacement"])
        replacement_item.setFlags(replacement_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 3, replacement_item)
        
        # Actions (Delete button for custom rules only)
        if is_custom:
            delete_button = QPushButton("🗑️ Delete")
            delete_button.setObjectName("deleteButton")
            delete_button.setToolTip(f"Remove the '{name}' rule")
            delete_button.clicked.connect(lambda: self.delete_pattern(name))
            self.table.setCellWidget(row, 4, delete_button)
        else:
            label = QLabel("🔒 Built-in")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #7f8c8d; font-style: italic;")
            label.setToolTip("Built-in rules cannot be deleted, but can be disabled")
            self.table.setCellWidget(row, 4, label)

    def toggle_pattern(self, name: str, state: int, is_custom: bool):
        """
        Toggle a pattern's enabled state.
        
        Args:
            name: Pattern name
            state: Checkbox state
            is_custom: Whether this is a custom pattern
        """
        enabled = state == Qt.CheckState.Checked.value
        
        if is_custom:
            patterns = self.settings_manager.get("custom_patterns", {})
        else:
            patterns = self.settings_manager.get("builtin_patterns", {})
        
        if name in patterns:
            patterns[name]["enabled"] = enabled

    def add_custom_rule(self):
        """Add a new custom rule from the input fields."""
        name = self.name_input.text().strip()
        pattern = self.pattern_input.text().strip()
        replacement = self.replacement_input.text().strip()
        
        # Validation
        if not name or not pattern or not replacement:
            QMessageBox.warning(
                self, "Invalid Input",
                "Please fill in all fields (Name, Pattern, Replacement)."
            )
            return
        
        # Check if name already exists
        all_patterns = self.settings_manager.get_all_patterns()
        if name in all_patterns:
            QMessageBox.warning(
                self, "Duplicate Name",
                f"A rule named '{name}' already exists. Please choose a different name."
            )
            return
        
        # Validate regex pattern
        try:
            re.compile(pattern)
        except re.error as e:
            QMessageBox.warning(
                self, "Invalid Regex",
                f"The regex pattern is invalid:\n{str(e)}"
            )
            return
        
        # Add the custom pattern
        self.settings_manager.add_custom_pattern(name, pattern, replacement)
        
        # Clear inputs
        self.name_input.clear()
        self.pattern_input.clear()
        self.replacement_input.clear()
        
        # Reload table
        self.load_patterns()
        
        QMessageBox.information(
            self, "Rule Added",
            f"Custom rule '{name}' has been added successfully."
        )

    def delete_pattern(self, name: str):
        """
        Delete a custom pattern.
        
        Args:
            name: Pattern name to delete
        """
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete the rule '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings_manager.delete_pattern(name)
            self.load_patterns()

    def save_and_close(self):
        """Save all changes and close the dialog."""
        self.settings_manager.save()
        QMessageBox.information(
            self, "Settings Saved",
            "Your settings have been saved successfully."
        )
        self.accept()


