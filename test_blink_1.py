"""
Test Blink Code 1 - Fast Blink Pattern
Version 2.0.0 - This will be served by the OTA server
"""
import machine
import utime

# Version info
VERSION = "2.0.0"
DEVICE_ID = "pico_001"

# Pin definitions
led_pin = 25

# Initialize LED
led_onboard = machine.Pin(led_pin, machine.Pin.OUT)

def fast_blink_pattern():
    """Fast blink pattern - 0.2 seconds on/off"""
    led_onboard.value(1)
    utime.sleep(0.2)
    led_onboard.value(0)
    utime.sleep(0.2)

def startup_sequence():
    """Startup sequence - 3 long blinks"""
    print("=== Fast Blink Test Code Started ===")
    print("Version:", VERSION)
    
    for i in range(3):
        print("Startup blink", i + 1)
        led_onboard.value(1)
        utime.sleep(1)
        led_onboard.value(0)
        utime.sleep(0.5)

def main():
    """Main application"""
    startup_sequence()
    
    print("Starting fast blink pattern...")
    counter = 0
    
    while True:
        try:
            fast_blink_pattern()
            counter += 1
            
            # Print status every 25 blinks (10 seconds)
            if counter % 25 == 0:
                print("Fast blink count:", counter)
            
            # Add some variation every 100 blinks
            if counter % 100 == 0:
                print("Special sequence!")
                for _ in range(5):
                    led_onboard.value(1)
                    utime.sleep(0.05)
                    led_onboard.value(0)
                    utime.sleep(0.05)
                utime.sleep(1)
                
        except Exception as e:
            print("Error in main loop:", e)
            utime.sleep(1)

# Run the application
if __name__ == "__main__":
    main()
