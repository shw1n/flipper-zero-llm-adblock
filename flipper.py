import serial  # Import the module directly
import time

class FlipperZero:
    """Interface for communicating with Flipper Zero via serial connection"""
    
    def __init__(self, port="COM3", baudrate=115200):  # Original port: /dev/cu.usbmodemflip_A75akoyu1
        """Initialize connection to Flipper Zero"""
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        
    def connect(self):
        """Establish serial connection and read initial messages"""
        try:
            self.serial = serial.Serial(self.port, baudrate=self.baudrate)  # Use serial.Serial instead of just Serial
            
            # Get initial prompt
            initial_prompt = self.serial.read_until(b'>:').decode('utf-8').strip()
            
            print(initial_prompt)
            
            return True
            
        except serial.SerialException as e:
            print(f"Error connecting to Flipper Zero: {e}")
            return False
            
    def disconnect(self):
        """Close the serial connection"""
        if self.serial:
            self.serial.close()
            self.serial = None
            
    def send_command(self, command):
        """Send a command to Flipper Zero and return the response"""
        if not self.serial:
            raise ConnectionError("Not connected to Flipper Zero")
            
        self.serial.write(f'{command}\r\n'.encode())
        response = self.serial.read_until(b'>:').decode('utf-8').strip()
        return response
        
    def __enter__(self):
        """Support for context manager protocol"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support for context manager protocol"""
        self.disconnect()

def tx(protocol: str, hex_address: str, hex_command: str) -> None:
    address = ' '.join(hex_address[i:i+2] for i in range(0, len(hex_address), 2)) if " " not in hex_address else hex_address
    command = ' '.join(hex_command[i:i+2] for i in range(0, len(hex_command), 2)) if " " not in hex_command else hex_command
    print(f"{protocol} {address} {command}")

def main():
    tx("Kaseikyo", "41543200", "72010000")
    # Example usage
    with FlipperZero() as flipper:
        #flipper.connect()
        #help_response = flipper.send_command('vibro 100,100,200')
        #help_response = flipper.send_command('ir tx Kaseikyo 41 54 32 00 72 01 00 00')  # Send mute IR command
        # need to reverse byte order compared to command in github files to work
        help_response = flipper.send_command('ir tx Kaseikyo 0x325441 0x0172')  # Send mute IR command
        print(help_response)

if __name__ == "__main__":
    main()
