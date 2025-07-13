"""
Test Blink Code 2 - Slow Pulse Pattern
Version 3.0.0 - This will be served by the OTA server
"""
import machine
import utime

# Version info
VERSION = "3.0.0"
DEVICE_ID = "pico_001"

# Pin definitions
led_pin = 25

# Initialize LED
led_onboard = machine.Pin(led_pin, machine.Pin.OUT)

def slow_pulse_pattern():
    """Slow pulse pattern - 2 seconds on, 1 second off"""
    led_onboard.value(1)
    utime.sleep(2)
    led_onboard.value(0)
    utime.sleep(1)

def breathing_pattern():
    """Breathing-like pattern with multiple pulses"""
    # Quick triple pulse
    for _ in range(3):
        led_onboard.value(1)
        utime.sleep(0.3)
        led_onboard.value(0)
        utime.sleep(0.3)
    
    # Long pause
    utime.sleep(2)

def startup_sequence():
    """Startup sequence - heartbeat pattern"""
    print("=== Slow Pulse Test Code Started ===")
    print("Version:", VERSION)
    
    for i in range(2):
        print("Startup heartbeat", i + 1)
        # Double beat
        led_onboard.value(1)
        utime.sleep(0.2)
        led_onboard.value(0)
        utime.sleep(0.2)
        led_onboard.value(1)
        utime.sleep(0.2)
        led_onboard.value(0)
        utime.sleep(1)

def main():
    """Main application"""
    startup_sequence()
    
    print("Starting slow pulse pattern...")
    counter = 0
    
    while True:
        try:
            # Alternate between two patterns
            if counter % 5 == 0:
                print("Breathing pattern")
                breathing_pattern()
            else:
                slow_pulse_pattern()
            
            counter += 1
            
            # Print status every 10 cycles
            if counter % 10 == 0:
                print("Pulse cycle count:", counter)
            
            # Special long sequence every 20 cycles
            if counter % 20 == 0:
                print("Long sequence!")
                for i in range(10):
                    led_onboard.value(1)
                    utime.sleep(0.1)
                    led_onboard.value(0)
                    utime.sleep(0.1)
                utime.sleep(3)
                
        except Exception as e:
            print("Error in main loop:", e)
            utime.sleep(1)

# Run the application
if __name__ == "__main__":
    main()
