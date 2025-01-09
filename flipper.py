import serial
import time

def main():
    try:
        # Connect to Flipper Zero via serial
        port = "/dev/cu.usbmodemflip_A75akoyu1"  # Adjust port as needed
        ser = serial.Serial(port, baudrate=9600, bytesize=8, stopbits=serial.STOPBITS_ONE, timeout=None)
        print(ser.read_until(b'>:').decode('utf-8').strip())
        
        # Give device time to initialize
        time.sleep(2)
        ser.write(b'help\r\n')
        print(ser.read_until(b'>:').decode('utf-8').strip())
        
        # Read the welcome message
        welcome_message = ser.readline().decode('utf-8').strip()
        print("Welcome message received:")
        print(welcome_message)
            
    except serial.SerialException as e:
        print(f"Error connecting to serial port: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    main()
