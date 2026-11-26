import serial
import time
import requests

# --- CONFIGURATION ---
ARDUINO_PORT = 'COM5'
BAUD_RATE = 115200

# Live or Testing ------------------------------------------------------------------
# DJANGO_SERVER_URL = 'https://wesley1crabajales.pythonanywhere.com/api/record_scan/'
DJANGO_SERVER_URL = 'http://127.0.0.1:8000/api/record_scan/'
# Live or Testing ------------------------------------------------------------------

def listen_to_arduino():
    try:

        # Added
        ser = serial.Serial()
        ser.port = ARDUINO_PORT
        ser.baudrate = BAUD_RATE
        ser.timeout = 1
        ser.dtr = False
        ser.rts = False
        ser.open()
        # Added

        # Removed ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1) # 1. Open the connection to the Arduino
        print(f"Connected to Arduino on {ARDUINO_PORT}. Waiting for card scans...")

        # Removed time.sleep(2)  # 2. Pause to let the Arduino reboot (happens automatically when USB connects)
        ser.reset_input_buffer() # Added

        while True: # 3. Create an infinite loop to constantly listen for new taps
            if ser.in_waiting > 0: # Check if there is new data waiting in the USB buffer
                # Removed scanned_uid = ser.readline().decode('utf-8').strip() # Read the line, convert it from raw bytes to text, and remove hidden newlines
                scanned_uid = ser.readline().decode('utf-8', errors='ignore').strip() # Added

                if scanned_uid: # If we successfully read a UID, print it

                    # Added
                    if len(scanned_uid) < 8 or not all(c in '0123456789ABCDEF' for c in scanned_uid):
                        print(f"ESP32 Status: {scanned_uid}")
                        continue
                    # Added

                    print(f"Card Tapped! UID: {scanned_uid}")
                    try:
                        payload = {'uid': scanned_uid} # Package the UID into a JSON format and send it to Django
                        # Removed response = requests.post(DJANGO_SERVER_URL, json=payload)
                        # Removed print(f"Server Reply: {response.json()}") # Print the server's reply (e.g., Success or Error)

                        #Added
                        response = requests.post(DJANGO_SERVER_URL, json=payload, timeout=5)
                        print(f"Server Reply ({response.status_code}): {response.text}")
                        #Added

                    except requests.exceptions.RequestException as e:
                        print(f"Network Error: Could not reach Django server. {e}")

    except serial.SerialException as e: # 4. Handle errors gracefully so the program doesn't crash violently
        print(f"Error connecting to Arduino: {e} (Is the Serial Monitor open in the Arduino IDE?)")
    except KeyboardInterrupt:
        print("\nBridge stopped by user.")


def terminal_test_mode(): # This is only for testing
    """Simulation mode: allows manual UID typing in the terminal without hardware."""
    print("--- RUNNING IN TERMINAL TEST MODE (NO HARDWARE REQUIRED) ---")
    print("Type a UID and press Enter to simulate a scan. Type 'exit' to quit.\n")

    while True:
        try:
            scanned_uid = input("Enter simulated UID: ").strip()

            if scanned_uid.lower() == 'exit':
                print("\nTest mode stopped by user.")
                break

            if scanned_uid:
                print(f"Simulating scan for UID: {scanned_uid}")
                try:
                    payload = {'uid': scanned_uid}
                    response = requests.post(DJANGO_SERVER_URL, json=payload)
                    print(f"Server Reply: {response.json()}\n")

                except requests.exceptions.RequestException as e:
                    print(f"Network Error: Could not reach Django server. {e}\n")

        except KeyboardInterrupt:
            print("\nTest mode stopped by user.")
            break

if __name__ == '__main__':

# Live or Testing ------------------------------------------------------------------
    listen_to_arduino() #uncomment for reading the arduino board
    # terminal_test_mode() # uncomment for testing
# Live or Testing ------------------------------------------------------------------

# Must paste to web url: http://127.0.0.1:8000/admin_portal.html