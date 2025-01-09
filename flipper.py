import serial
import time

def send_command(ser, command):
    """Send a command to Flipper Zero and return the response"""
    ser.write(f'{command}\r\n'.encode())
    response = ser.read_until(b'>:').decode('utf-8').strip()
    return response

def main():
    try:
        # Connect to Flipper Zero via serial
        port = "/dev/cu.usbmodemflip_A75akoyu1"  # Adjust port as needed
        #ser = serial.Serial(port, baudrate=9600, bytesize=8, stopbits=serial.STOPBITS_ONE, timeout=None)
        # any baudrate works it seems
        ser = serial.Serial(port, baudrate=115200)

        # Get initial prompt
        initial_prompt = ser.read_until(b'>:').decode('utf-8').strip()
        print(initial_prompt)
        
        
        # Send help command and get response
        help_response = send_command(ser, 'help')
        print(help_response)
        
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
