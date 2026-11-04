import serial
import time

# --- CONFIGURATION ---
ARDUINO_PORT = 'COM5'
BAUD_RATE = 9600

def listen_to_arduino():
    try:
        # 1. Open the connection to the Arduino
        ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to Arduino on {ARDUINO_PORT}. Waiting for card scans...")

        # 2. Pause to let the Arduino reboot (happens automatically when USB connects)
        time.sleep(2)

        # 3. Create an infinite loop to constantly listen for new taps
        while True:
            # Check if there is new data waiting in the USB buffer
            if ser.in_waiting > 0:
                # Read the line, convert it from raw bytes to text, and remove hidden newlines
                scanned_uid = ser.readline().decode('utf-8').strip()

                # If we successfully read a UID, print it
                if scanned_uid:
                    print(f"Card Tapped! UID: {scanned_uid}")
                    # (Later, we will add the code here to send this to Django)

    # 4. Handle errors gracefully so the program doesn't crash violently
    except serial.SerialException as e:
        print(f"Error connecting to Arduino: {e} (Is the Serial Monitor open in the Arduino IDE?)")
    except KeyboardInterrupt:
        print("\nBridge stopped by user.")

if __name__ == '__main__':
    listen_to_arduino()