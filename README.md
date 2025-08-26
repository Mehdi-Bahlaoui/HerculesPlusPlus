# Hercules ++ - TCP Network Testing Tool

A simplified PyQt-based TCP network testing utility with 30 command inputs, persistent settings, and colored response display.

## Features

- **TCP Client Only**: Send messages using TCP protocol (uses sender_receiver.py)
- **30 Command Inputs**: Individual input fields for 30 different commands
- **Individual Send Buttons**: Each command has its own send button
- **Colored Response Display**: 
  - Debug info (timestamps, "TCP Response:") in **green** for normal operations
  - Debug info in **red** for errors
  - Actual response content in **pink**
  - Sent commands displayed in **black**
- **Auto Newline**: Automatically append newline character to commands
- **Threaded Operations**: Non-blocking network operations
- **Scrollable Interface**: Commands area is scrollable to accommodate all 30 inputs

## Installation

1. Make sure Python 3.6+ is installed
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```
python hercules++.py
```

### Interface Layout

1. **TCP Connection Settings** (top)
   - IP Address and Port input
   - Auto newline checkbox

2. **Response Display** (middle)
   - Shows all responses from the server with color coding:
     - **Black**: Sent commands (e.g., "[10:04:33] Sent: *IDN?")
     - **Green**: Success timestamps and "TCP Response:" labels
     - **Pink**: Actual response content from the server
     - **Red**: Error messages and timestamps
   - Clear button to clear the response history

3. **Command Inputs** (bottom - scrollable)
   - 30 input fields labeled "Command 1:" through "Command 30:"
   - Individual "Send" button for each command
   - Commands are automatically saved when you exit the program

### Default Commands

The application starts with 30 **blank** command inputs. You can enter any commands you want in each field. Common SCPI commands you might use include:

- `*IDN?` - Device Identification
- `*TST?` - Self Test  
- `*RST` - Reset Device
- `SYST:ERR?` - System Error
- `*OPC?` - Operation Complete
- `SYST:VER?` - System Version
- `*CLS` - Clear Status
- `MEAS:VOLT?` - Measure Voltage
- `MEAS:CURR?` - Measure Current
- And many more...

All changes to command inputs are automatically saved when you exit the program.

## Response Display Colors

The response area uses color coding for easy identification:

- **[HH:MM:SS] Sent: command** - Black text for sent commands
- **[HH:MM:SS] TCP Response:** - Green text for successful operations
- **actual response content** - Pink text for server responses  
- **[HH:MM:SS] TCP Error: error message** - Red text for errors

## Default Settings

- **IP Address**: 169.254.156.89
- **Port**: 5025
- **Protocol**: TCP only
- **Auto Newline**: Enabled
- **Commands**: All 30 fields start blank



## Files

- `dist/hercules++.exe` - Executable for immediate access
- `hercules++.py` - Main PyQt application
- `sender_receiver.py` - Original TCP client function (reference)
- `requirements.txt` - Python dependencies
- `README.md` - This file

## Based On

This application uses the `sender_receiver.py` TCP client function as a reference and extends it with a PyQt GUI.
