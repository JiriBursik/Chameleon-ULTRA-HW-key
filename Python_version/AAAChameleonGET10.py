import sys
import time
import json
import os
import serial.tools.list_ports
import pyperclip
import threading
from datetime import datetime
from pystray import Icon, Menu, MenuItem as item
from PIL import Image, ImageDraw

# --- IMPORT YOUR LIBRARIES ---
try:
    from chameleon_com import ChameleonCom
    from chameleon_cmd import ChameleonCMD
    from chameleon_enum import SlotNumber, TagSenseType
except ImportError as e:
    print("Error: Chameleon libraries not found!")
    sys.exit(1)

# --- CONFIGURATION ---
CHAMELEON_VID = 0x6868
CHAMELEON_PID = 0x8686
CONFIG_FILE = "chameleon_config.json"

# --- GLOBAL STATE ---
TARGET_SLOT = SlotNumber.SLOT_1 
TARGET_SENSE = TagSenseType.HF
NOTIFICATIONS_ENABLED = True
TARGET_SERIAL = None 

force_read_event = threading.Event()
tray_icon = None

# --- HELPER FUNCTION FOR LOGGING & NOTIFICATIONS ---

def log(icon, message, level="INFO", notify=False):
    """
    Prints a message to the console with a timestamp and optionally sends a notification.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    console_msg = f"[{timestamp}] [{level}] {message}"
    print(console_msg)  # Always print to command line

    if notify and NOTIFICATIONS_ENABLED and icon:
        clean_msg = message.split('\n')[0] 
        icon.notify(message, f"Chameleon - {level}")

# --- CONFIGURATION HANDLING ---

def load_config():
    global TARGET_SLOT, TARGET_SENSE, NOTIFICATIONS_ENABLED, TARGET_SERIAL
    if not os.path.exists(CONFIG_FILE):
        return
    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            if 'slot' in data and hasattr(SlotNumber, data['slot']):
                TARGET_SLOT = getattr(SlotNumber, data['slot'])
            if 'sense' in data and hasattr(TagSenseType, data['sense']):
                TARGET_SENSE = getattr(TagSenseType, data['sense'])
            if 'notifications' in data:
                NOTIFICATIONS_ENABLED = data['notifications']
            if 'target_serial' in data:
                TARGET_SERIAL = data['target_serial']
        print(f"Configuration loaded. Target S/N: {TARGET_SERIAL}")
    except Exception as e:
        print(f"Configuration error: {e}")

def save_config_action(icon, item):
    data = {
        'slot': TARGET_SLOT.name if hasattr(TARGET_SLOT, 'name') else str(TARGET_SLOT),
        'sense': TARGET_SENSE.name if hasattr(TARGET_SENSE, 'name') else str(TARGET_SENSE),
        'notifications': NOTIFICATIONS_ENABLED,
        'target_serial': TARGET_SERIAL
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f)
        log(icon, "Settings saved as default.", notify=True)
    except Exception as e:
        log(icon, f"Error saving settings: {e}", level="ERROR", notify=True)

# --- GRAPHICS ---

def create_image(color):
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color)
    dc = ImageDraw.Draw(image)
    return image

# --- MENU LOGIC ---

def select_device_handler(serial_number, vid, pid):
    def inner(icon, item):
        global TARGET_SERIAL
        TARGET_SERIAL = serial_number
        
        v_str = f"{vid:04X}" if vid else "????"
        p_str = f"{pid:04X}" if pid else "????"
        
        log(icon, f"New device selected:\nVID: {v_str}, PID: {p_str}\nS/N: {serial_number}", notify=True)
        
        force_read_event.set()
        update_icon_menu(icon)
    return inner

def is_device_checked(serial_number):
    return lambda item: TARGET_SERIAL == serial_number

def set_slot(slot_enum):
    def inner(icon, item):
        global TARGET_SLOT
        TARGET_SLOT = slot_enum
        print(f"Slot changed to: {slot_enum.name}")
    return inner

def set_sense(sense_enum):
    def inner(icon, item):
        global TARGET_SENSE
        TARGET_SENSE = sense_enum
        print(f"Frequency changed to: {sense_enum.name}")
    return inner

def toggle_notifications(icon, item):
    global NOTIFICATIONS_ENABLED
    NOTIFICATIONS_ENABLED = not NOTIFICATIONS_ENABLED
    print(f"Notifications: {'ON' if NOTIFICATIONS_ENABLED else 'OFF'}")

def trigger_manual_copy(icon, item):
    print("Manual copy requested...")
    force_read_event.set()

def on_exit(icon, item):
    print("Exiting application via menu...")
    icon.stop()

# --- MENU CONSTRUCTION ---

def build_menu():
    all_ports = serial.tools.list_ports.comports()
    device_items = []
    
    if not all_ports:
        device_items.append(item("No devices found", lambda i, It: None, enabled=False))
    else:
        for p in all_ports:
            s_num = p.serial_number if p.serial_number else "Unknown"
            vid_str = f"{p.vid:04X}" if p.vid else "N/A"
            pid_str = f"{p.pid:04X}" if p.pid else "N/A"
            
            is_chameleon = (p.vid == CHAMELEON_VID and p.pid == CHAMELEON_PID)
            
            if is_chameleon:
                label = f"★ {p.device} [CHAMELEON] (VID:{vid_str} PID:{pid_str})"
            else:
                desc = p.description if len(p.description) < 15 else p.description[:15]
                label = f"{p.device} ({desc}) VID:{vid_str} PID:{pid_str}"
            
            device_items.append(
                item(label, select_device_handler(s_num, p.vid, p.pid), checked=is_device_checked(s_num), radio=True)
            )

    device_menu = Menu(*device_items)

    slot_items = []
    slots_map = [
        (SlotNumber.SLOT_1, 'Slot 1'), (SlotNumber.SLOT_2, 'Slot 2'),
        (SlotNumber.SLOT_3, 'Slot 3'), (SlotNumber.SLOT_4, 'Slot 4'),
        (SlotNumber.SLOT_5, 'Slot 5'), (SlotNumber.SLOT_6, 'Slot 6'),
        (SlotNumber.SLOT_7, 'Slot 7'), (SlotNumber.SLOT_8, 'Slot 8')
    ]
    for s_enum, s_label in slots_map:
        slot_items.append(item(s_label, set_slot(s_enum), checked=lambda i, s=s_enum: TARGET_SLOT == s, radio=True))
    slot_menu = Menu(*slot_items)

    sense_menu = Menu(
        item('HF (High Freq)', set_sense(TagSenseType.HF), checked=lambda i: TARGET_SENSE == TagSenseType.HF, radio=True),
        item('LF (Low Freq)',  set_sense(TagSenseType.LF), checked=lambda i: TARGET_SENSE == TagSenseType.LF, radio=True),
    )

    return Menu(
        item('COPY NOW', trigger_manual_copy),
        Menu.SEPARATOR,
        item('Select Device', device_menu),
        Menu.SEPARATOR,
        item('Select Slot', slot_menu),
        item('Select Frequency', sense_menu),
        Menu.SEPARATOR,
        item('Show Notifications', toggle_notifications, checked=lambda i: NOTIFICATIONS_ENABLED),
        Menu.SEPARATOR,
        item('Set as Default', save_config_action),
        item('Exit', on_exit)
    )

def update_icon_menu(icon):
    if icon:
        icon.menu = build_menu()

# --- WORKER: PORT MONITOR ---

def monitor_ports_and_state(icon):
    global TARGET_SERIAL
    last_port_list_signature = None
    last_connected_device_sn = None
    
    # State tracking for clipboard restoration
    original_clipboard_content = None
    last_pasted_content = None  # To check if we should restore

    log(icon, "Starting port monitoring...")

    while icon.visible:
        current_ports = serial.tools.list_ports.comports()
        current_signature = ",".join([f"{p.device}_{p.vid}_{p.pid}" for p in current_ports])

        if current_signature != last_port_list_signature:
            update_icon_menu(icon)
            last_port_list_signature = current_signature
        
        current_port_name = None
        current_port_sn = None
        current_vid = None
        current_pid = None

        if TARGET_SERIAL:
            for p in current_ports:
                if p.serial_number == TARGET_SERIAL:
                    current_port_name = p.device
                    current_port_sn = p.serial_number
                    current_vid = p.vid
                    current_pid = p.pid
                    break
        
        should_read = False

        if current_port_name:
            # --- CONNECTED ---
            icon.icon = create_image('blue')
            notif_status = "" if NOTIFICATIONS_ENABLED else " (Silent)"
            v_str = f"{current_vid:04X}" if current_vid else "?"
            p_str = f"{current_pid:04X}" if current_pid else "?"
            icon.title = f"{current_port_name} [VID:{v_str} PID:{p_str}]{notif_status}"

            if current_port_sn != last_connected_device_sn:
                log(icon, f"Device connected: {current_port_name}")
                
                # 1. Backup clipboard ONLY if we haven't done so (clean state)
                if original_clipboard_content is None:
                    try:
                        original_clipboard_content = pyperclip.paste()
                        log(icon, "Original clipboard content saved.")
                    except:
                        log(icon, "Failed to read clipboard backup.", level="WARN")
                
                should_read = True
            
            if force_read_event.is_set():
                should_read = True
                force_read_event.clear()
            
            if should_read:
                # We expect perform_read_and_copy to return the text it copied
                copied_text = perform_read_and_copy(current_port_name, icon, current_vid, current_pid)
                if copied_text:
                    last_pasted_content = copied_text
                
                last_connected_device_sn = current_port_sn
        else:
            # --- DISCONNECTED ---
            icon.icon = create_image('green')
            icon.title = "No device selected (Right-click -> Select Device)"
            
            if last_connected_device_sn is not None:
                log(icon, "Device disconnected.")
                
                # 2. Smart Restore Logic
                current_clipboard = ""
                try:
                    current_clipboard = pyperclip.paste()
                except:
                    pass

                # Restore ONLY if the current clipboard is exactly what we put there
                if original_clipboard_content is not None:
                    if current_clipboard == last_pasted_content:
                        pyperclip.copy(original_clipboard_content)
                        log(icon, "Clipboard restored to original state.")
                    else:
                        log(icon, "Clipboard modified by user. Restoration skipped to prevent data loss.")
                    
                    # Reset state
                    original_clipboard_content = None
                    last_pasted_content = None
            
            last_connected_device_sn = None

        time.sleep(1)
    
    log(icon, "Monitoring stopped.")

def perform_read_and_copy(port_name, icon, vid, pid):
    """
    Returns the string that was copied to clipboard, or None if failed.
    """
    com = ChameleonCom()
    v_str = f"{vid:04X}" if vid else "?"
    p_str = f"{pid:04X}" if pid else "?"
    id_info = f"(VID: {v_str}, PID: {p_str})"
    
    result_text = None

    try:
        icon.title = f"Reading... {id_info}"
        log(icon, f"Opening port {port_name}...")
        com.open(port_name)
        cmd = ChameleonCMD(com)
        time.sleep(0.3)
        
        log(icon, f"Reading Slot: {TARGET_SLOT.name}, Freq: {TARGET_SENSE.name}...")
        nick_name = cmd.get_slot_tag_nick(TARGET_SLOT, TARGET_SENSE)
        
        if nick_name:
            clean_name = nick_name.strip().replace('\x00', '')
            final_name = clean_name.split(' ')[0]
            if final_name:
                pyperclip.copy(final_name)
                msg = f"Copied: {final_name}\n{id_info}"
                log(icon, msg, notify=True)
                result_text = final_name
            else:
                log(icon, f"Slot is empty. {id_info}", level="WARN", notify=True)
        else:
             log(icon, f"Read failed (no data). {id_info}", level="ERROR", notify=True)
    except Exception as e:
        log(icon, f"Communication error: {e}", level="ERROR", notify=True)
    finally:
        if com.isOpen(): com.close()
    
    return result_text

# --- INPUT LISTENER ---

def listen_for_exit(icon):
    print("\n" + "="*50)
    print(" APPLICATION RUNNING. TO EXIT PRESS >> ENTER << ")
    print("="*50 + "\n")
    input()
    print("Exiting application...")
    icon.stop()

# --- SETUP ---

def setup(icon):
    icon.visible = True
    t = threading.Thread(target=monitor_ports_and_state, args=(icon,))
    t.daemon = True
    t.start()

if __name__ == "__main__":
    load_config()
    main_menu = build_menu()
    image = create_image('green')
    tray_icon = Icon("Chameleon", image, "Starting...", menu=main_menu)

    exit_thread = threading.Thread(target=listen_for_exit, args=(tray_icon,))
    exit_thread.daemon = True 
    exit_thread.start()

    tray_icon.run(setup=setup)