import serial
import time

class FlipperZero:
    """Interface for communicating with Flipper Zero via serial connection"""
    
    def __init__(self, port="/dev/cu.usbmodemflip_A75akoyu1", baudrate=115200):
        """Initialize connection to Flipper Zero"""
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        
    def connect(self):
        """Establish serial connection and read initial messages"""
        try:
            self.serial = serial.Serial(self.port, baudrate=self.baudrate)
            
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

def main():
    # Example usage
    with FlipperZero() as flipper:
        #flipper.connect()
        help_response = flipper.send_command('help')
        print(help_response)

if __name__ == "__main__":
    main()
