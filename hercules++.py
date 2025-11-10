import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLineEdit, QTextEdit, QLabel, 
                             QSpinBox, QGroupBox, QGridLayout, QFrame,
                             QCheckBox, QMessageBox, QScrollArea, QTabWidget)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QTextCursor, QColor
import time
from sender_receiver import send_tcp_request

class NetworkThread(QThread):
    """Thread for handling network operations"""
    result_ready = pyqtSignal(str, str)
    command_sent = pyqtSignal(str)
    
    def __init__(self, ip, port, message):
        super().__init__()
        self.ip = ip
        self.port = port
        self.message = message
        
    def run(self):
        try:
            self.command_sent.emit(f"Command: {self.message.strip()}")
            
            # Use the external send_tcp_request function with minimal timeout
            result = send_tcp_request(self.ip, self.port, self.message, timeout=0.1)
            
            if result:
                self.result_ready.emit("success", result)
            else:
                # Command sent successfully but no response (normal for some commands)
                self.result_ready.emit("success", "")
        except Exception as e:
            self.result_ready.emit("error", str(e))

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class HerculesPlusPlus(QMainWindow):
    def __init__(self):
        super().__init__()
        self.commands_file = resource_path("COMMANDS.txt")
        self.network_thread = None
        self.send_buttons = []
        self.active_button = None  # Track which button is currently sending
        
        self.parse_commands()
        self.init_ui()
        
    def parse_commands(self):
        """Parse COMMANDS.txt file into sections dynamically"""
        self.sections = {}
        current_section = "GENERAL"
        in_section = False
        
        if not os.path.exists(self.commands_file):
            # If file doesn't exist, create default with one command
            self.sections = {"GENERAL": ["*IDN?"]}
            return
            
        try:
            with open(self.commands_file, 'r') as f:
                for line in f:
                    original_line = line.rstrip('\n\r')  # Keep spaces but remove line endings
                    stripped_line = line.strip()
                    
                    # Section header
                    if stripped_line.startswith('//'):
                        current_section = stripped_line[2:].strip()
                        if current_section not in self.sections:
                            self.sections[current_section] = []
                        in_section = True
                    # Empty line within a section - treat as UI spacing
                    elif in_section and not stripped_line:
                        if current_section not in self.sections:
                            self.sections[current_section] = []
                        self.sections[current_section].append("---UI_SPACE---")
                    # Actual command (not empty line)
                    elif stripped_line:
                        if current_section not in self.sections:
                            self.sections[current_section] = []
                        self.sections[current_section].append(stripped_line)
                        in_section = True
                    
        except Exception as e:
            print(f"Error parsing commands: {e}")
            self.sections = {"GENERAL": ["*IDN?"]}
    
    def init_ui(self):
        self.setWindowTitle("Hercules++")
        self.setGeometry(100, 100, 1800, 900)
        
        # Set application font size
        font = QFont()
        font.setPointSize(10)  # Increase from default (usually 8-9) to 10
        self.setFont(font)
        
        # Main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Connection settings
        conn_group = QGroupBox("TCP Connection Settings")
        conn_layout = QHBoxLayout(conn_group)
        
        conn_layout.addWidget(QLabel("IP Address:"))
        self.ip_input = QLineEdit("169.254.156.89")
        conn_layout.addWidget(self.ip_input)
        
        conn_layout.addWidget(QLabel("Port:"))
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(5025)
        conn_layout.addWidget(self.port_input)
        
        self.auto_newline = QCheckBox("Auto append \\n")
        self.auto_newline.setChecked(True)
        conn_layout.addWidget(self.auto_newline)
        
        conn_layout.addStretch()
        main_layout.addWidget(conn_group)
        
        # Split layout for commands and response
        split_layout = QHBoxLayout()
        
        # Left side: Commands tabs
        tabs = QTabWidget()
        tabs.setMinimumWidth(400)
        
        for section_name, commands in self.sections.items():
            tab_widget = self.create_section_tab(commands)
            tabs.addTab(tab_widget, section_name)
        
        split_layout.addWidget(tabs)
        
        # Right side: Response
        resp_group = QGroupBox("Response")
        resp_layout = QVBoxLayout(resp_group)
        
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)
        
        # Set larger font for response display
        response_font = QFont()
        response_font.setPointSize(14)  # Even larger for better readability
        response_font.setFamily("Consolas")  # Use monospace font for better formatting
        self.response_display.setFont(response_font)
        
        resp_layout.addWidget(self.response_display)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.response_display.clear)
        resp_layout.addWidget(clear_btn)
        
        split_layout.addWidget(resp_group)
        main_layout.addLayout(split_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_section_tab(self, commands):
        """Create a tab widget for a section with dynamic number of commands"""
        scroll = QScrollArea()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create rows for all commands in the section
        for i, cmd_text in enumerate(commands):
            # Check if this is a UI space
            if cmd_text == "---UI_SPACE---":
                # Create empty space instead of horizontal line
                spacer = QWidget()
                spacer.setFixedHeight(15)  # Adjustable spacing height
                layout.addWidget(spacer)
                continue
            
            row_layout = QHBoxLayout()
            
            cmd_input = QLineEdit(cmd_text)
            row_layout.addWidget(cmd_input)
            
            # Send button
            send_btn = QPushButton("Send")
            send_btn.setMaximumWidth(80)
            
            # Only enable button if there's a command
            if not cmd_text:
                send_btn.setEnabled(False)
                cmd_input.setPlaceholderText("(empty slot)")
            
            # Connect button to send function - use partial to avoid closure issues
            send_btn.clicked.connect(lambda checked, input_w=cmd_input, btn=send_btn: 
                                    self.send_command(input_w.text(), input_w, btn))
            
            # Connect text change to enable/disable button
            cmd_input.textChanged.connect(lambda text, btn=send_btn: 
                                         btn.setEnabled(bool(text.strip())))
            
            self.send_buttons.append(send_btn)
            row_layout.addWidget(send_btn)
            
            layout.addLayout(row_layout)
        
        layout.addStretch()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        return scroll
    
    def send_command(self, command, input_widget=None, button=None):
        """Send command via TCP"""
        if self.network_thread and self.network_thread.isRunning():
            QMessageBox.warning(self, "Warning", "Operation in progress!")
            return
        
        command = command.strip()
        if not command:
            return
            
        ip = self.ip_input.text().strip()
        port = self.port_input.value()
        
        if not ip:
            QMessageBox.warning(self, "Warning", "Please enter IP address!")
            return
        
        # Auto append newline
        if self.auto_newline.isChecked() and not command.endswith('\n'):
            command += '\n'
        
        # Select the text in the input widget that's being sent
        if input_widget:
            # Clear focus from any other widget first
            self.setFocus()
            # Now set focus and select the text in the correct widget
            input_widget.setFocus()
            input_widget.selectAll()
        
        # Store the button that was clicked to re-enable it later
        self.active_button = button
        
        # Only disable the clicked button
        if button:
            button.setEnabled(False)
        
        self.statusBar().showMessage(f"Sending to {ip}:{port}...")
        
        # Start thread
        self.network_thread = NetworkThread(ip, port, command)
        self.network_thread.result_ready.connect(self.handle_response)
        self.network_thread.command_sent.connect(self.display_sent)
        self.network_thread.start()
    
    def display_sent(self, text):
        """Display sent command in black"""
        timestamp = time.strftime('%H:%M:%S')
        cursor = self.response_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Black text for sent
        format = cursor.charFormat()
        format.setForeground(QColor(0, 0, 0))
        cursor.setCharFormat(format)
        cursor.insertText(f"[{timestamp}] {text}\n")
        
        self.response_display.setTextCursor(cursor)
    
    def handle_response(self, result_type, message):
        """Handle response from network thread"""
        timestamp = time.strftime('%H:%M:%S')
        cursor = self.response_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        if result_type == "success":
            # Green for "Response:"
            format = cursor.charFormat()
            format.setForeground(QColor(0, 150, 0))
            cursor.setCharFormat(format)
            cursor.insertText(f"[{timestamp}] TCP Response: ")
            
            # Pink for response content
            format.setForeground(QColor(255, 20, 147))
            cursor.setCharFormat(format)
            cursor.insertText(f"{message}\n")
        else:
            # Red for error
            format = cursor.charFormat()
            format.setForeground(QColor(200, 0, 0))
            cursor.setCharFormat(format)
            cursor.insertText(f"[{timestamp}] TCP Error: {message}\n")
        
        # Reset color to black
        format.setForeground(QColor(0, 0, 0))
        cursor.setCharFormat(format)
        
        self.response_display.setTextCursor(cursor)
        self.response_display.append("")  # New line
        
        # Re-enable only the button that was clicked
        if hasattr(self, 'active_button') and self.active_button:
            self.active_button.setEnabled(True)
        
        self.statusBar().showMessage("Ready")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = HerculesPlusPlus()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()