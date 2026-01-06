=====================================

                      CHAMELEON HW KEY - AUTOMATED TOOL

[ CORE CONCEPT: THE HARDWARE KEY ]
The main idea behind this project is to utilize the Chameleon device not just 
for RFID emulation, but as a physical security token for password management.

The software reads the text stored in the "Nickname" or "Name" field of the 
LF/HF tags within the Chameleon's slots. These fields can store up to 
20 characters. By saving your complex passwords, encryption keys, or access 
codes into these slots, the Chameleon becomes a "Hardware Key".

[ USE CASES ]
- Encrypted Containers: Use the stored string to unlock VeraCrypt volumes or 
  BitLocker drives.
- Access Codes: Quickly paste 20-character security tokens for login screens.
- Physical Security: The password exists physically on the device; if you 
  remove the device, the password is removed from your clipboard automatically.

[ DESCRIPTION ]
This application sits in your system tray and monitors for a Chameleon RFID 
emulation device. When the specific device is connected via USB, the application 
automatically reads the 20-char string from the selected Slot/Frequency 
and copies it to your clipboard.

When the device is disconnected, the application restores your clipboard to 
its previous state, ensuring you don't lose your work and the sensitive 
password doesn't stay in the memory.

[ FEATURES ]
- Hardware Key Functionality: Turns slot names into copy-pasteable passwords.
- Automatic Detection: Detects Chameleon devices based on VID/PID.
- Auto-Copy: Reads data immediately upon USB connection.
- Smart Clipboard: Restores original clipboard content after device removal.
- System Tray Control: Right-click menu for quick settings.
- Hardware ID Filtering: Distinguishes specific Chameleon devices via Serial Number.
- Persistent Settings: Remembers your Slot, Frequency, and Device choice.
- Diagnostics: Command-line output for troubleshooting.

=====================================

                           INSTRUCTIONS: WINDOWS 11 
                         (Compiled Executable Version)

1. LOCATE THE FILE:
   Download "Chameleon_HW_key.exe".

2. RUN THE APP:
   Double-click "Chameleon_HW_key.exe". 

3. SYSTEM TRAY:
   Look for the square icon in your system tray (near the clock).
   - GREEN Icon: Scanning/Idle (No device connected).
   - BLUE Icon: Device Connected & Active.

4. FIRST TIME SETUP:
   a. Plug in your Chameleon device via USB.
   b. Right-click the Tray Icon.
   c. Go to "Select Device".
   d. Click on your device (It will be marked with a star ★ and [CHAMELEON]).
   e. Select your desired "Slot" (1-8) and "Frequency" (HF/LF) where your
      password/string is stored.
   f. Click "Set as Default" to save these settings.

5. EXITING:
   To close the application properly, click into the black console window 
   and press the [ENTER] key. Alternatively, select "Exit" from the tray menu.
   
=====================================

                  HOW TO START AUTOMATICALLY ON WINDOWS LOGIN

To have the application start automatically when you log in, follow these steps:

1. CREATE A SHORTCUT:
   Right-click on "Chameleon_HW_key.exe" and select 
   "Create shortcut" (Show more options -> Create shortcut on Win 11).

2. OPEN STARTUP FOLDER:
   The easiest way to find the correct folder is:
   a. Press [Windows Key] + [R] on your keyboard.
   b. Type: shell:startup
   c. Press [ENTER].
   
   (Alternatively, manually browse to: 
   C:\Users\YOUR_USERNAME\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup)

3. MOVE THE SHORTCUT:
   Move (cut and paste) the newly created shortcut into the Startup folder 
   you just opened.

=====================================

                          INSTRUCTIONS: PYTHON VERSION
                          (Source Code)

[ PREREQUISITES ]
- Python 3.x installed.
- The Official Chameleon CLI python libraries must be present in the folder 
  (chameleon_com.py, chameleon_cmd.py, etc.).

[ INSTALLATION ]
1. Open a terminal/command prompt in the application folder.
2. Install the required dependencies:
   
   pip install pyserial pyperclip pystray pillow

[ RUNNING THE SCRIPT ]
1. Execute the script via python:
   
   python Chameleon_HW_key.py

2. Follow the usage instructions in the Windows 11 section above.

=====================================

                                TROUBLESHOOTING

[1] Application crashes on exit
    Make sure you exit by pressing ENTER in the console window or using the 
    "Exit" button in the tray menu. Do not force close the console window using 
    the "X" button.

[2] Device not found in "Select Device" menu
    Ensure the device is plugged in and recognized by Windows Device Manager 
    as a Serial Port (COM port).

[3] "Read Failed" or "Slot is Empty"
    - Ensure you have selected the correct Frequency (HF vs LF).
    - Check if the text/password is actually saved in the "Nickname" field of 
      that slot on the device.

[4] Settings not saving
    Ensure the application has permission to write to "chameleon_config.json" 
    in the same folder as the executable/script.

=====================================
