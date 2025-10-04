"""
Clipboard Monitor Module
Monitors clipboard changes across all applications using polling.
"""

from PyQt6.QtCore import QThread, pyqtSignal
import pyperclip
import time


class ClipboardMonitor(QThread):
    """
    Background thread that monitors clipboard changes using polling.
    This approach works reliably across all applications in X11 and Wayland.
    """

    # Signal emitted when new text is copied
    new_text_copied = pyqtSignal(str)

    def __init__(self):
        """Initialize the clipboard monitor thread."""
        super().__init__()
        self.running = False
        self.last_text = ""
        self.poll_interval = 0.25  # Check every 250ms (reasonable balance)

    def run(self):
        """Main thread loop - polls clipboard for changes."""
        self.running = True
        
        # Get initial clipboard content
        try:
            self.last_text = pyperclip.paste()
        except Exception:
            self.last_text = ""
        
        while self.running:
            try:
                # Get current clipboard content
                current_text = pyperclip.paste()
                
                # Check if it changed and is not empty
                if current_text and current_text != self.last_text:
                    self.last_text = current_text
                    # Emit signal to main application
                    self.new_text_copied.emit(current_text)
                    
            except Exception as e:
                # Clipboard access can sometimes fail, just continue
                pass
            
            # Sleep to prevent CPU spinning
            time.sleep(self.poll_interval)

    def stop(self):
        """Stop the monitoring thread gracefully."""
        self.running = False
        self.wait()  # Wait for thread to finish


