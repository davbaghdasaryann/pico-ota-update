"""
Raspberry Pi Pico OTA Update System
Main code that can update itself from a server
"""
import machine
import os
import utime
import ubinascii
import gc
try:
    import ujson as json
except ImportError:
    import json

# Version and device info
VERSION = "1.0.0"
DEVICE_ID = "pico_001"
OTA_SERVER = "http://your-server.com"  # Replace with your server URL

# Pin definitions
led_pin = 25
pwr_en = 14
uart_port = 0
uart_baute = 115200

# APN configuration
APN = "cmnbiot"

# Initialize LED
led_onboard = machine.Pin(led_pin, machine.Pin.OUT)

# Initialize UART
uart = None

def led_blink_pattern(pattern_name="default"):
    """Different LED blink patterns"""
    if pattern_name == "updating":
        # Fast blink during update
        for _ in range(10):
            led_onboard.value(1)
            utime.sleep(0.1)
            led_onboard.value(0)
            utime.sleep(0.1)
    elif pattern_name == "error":
        # SOS pattern
        for _ in range(3):
            led_onboard.value(1)
            utime.sleep(0.1)
            led_onboard.value(0)
            utime.sleep(0.1)
        utime.sleep(0.3)
        for _ in range(3):
            led_onboard.value(1)
            utime.sleep(0.3)
            led_onboard.value(0)
            utime.sleep(0.3)
        utime.sleep(0.3)
        for _ in range(3):
            led_onboard.value(1)
            utime.sleep(0.1)
            led_onboard.value(0)
            utime.sleep(0.1)
    else:
        # Default pattern
        led_onboard.value(1)
        utime.sleep(0.5)
        led_onboard.value(0)
        utime.sleep(0.5)

def powerOn(p):
    machine.Pin(p, machine.Pin.OUT).value(1)
    utime.sleep(2)

def sendCMD_waitResp(cmd, timeout=3000):
    print("CMD:", cmd)
    try:
        uart.write(cmd.encode() + b'\r\n')
        response = waitResp(timeout)
        print("RESP:", response)
        return response
    except Exception as e:
        print("UART CMD failed:", e)
        return ""

def waitResp(timeout=3000):
    start = utime.ticks_ms()
    resp = b""
    while utime.ticks_diff(utime.ticks_ms(), start) < timeout:
        if uart.any():
            try:
                resp += uart.read(1)
            except:
                break
        utime.sleep_ms(10)
    try:
        return resp.decode('utf-8')
    except:
        return "(binary data)"

def str_to_hexStr(string):
    try:
        return ubinascii.hexlify(string.encode('utf-8')).decode('utf-8')
    except:
        return string

def hexStr_to_str(hex_str):
    try:
        return ubinascii.unhexlify(hex_str.encode('utf-8')).decode('utf-8')
    except:
        return hex_str

def init_sim7020():
    global uart
    try:
        uart = machine.UART(uart_port, uart_baute, bits=8, parity=None, stop=1)
        powerOn(pwr_en)
        utime.sleep(2)
        
        if uart.any():
            uart.read()
        
        # Basic AT commands
        sendCMD_waitResp("AT")
        sendCMD_waitResp("ATE1")
        
        # Configure APN
        sendCMD_waitResp("AT+CFUN=0")
        utime.sleep(2)
        sendCMD_waitResp("AT*MCGDEFCONT=\"IP\",\"{}\"".format(APN))
        sendCMD_waitResp("AT+CFUN=1")
        utime.sleep(10)
        sendCMD_waitResp("AT+CGATT?")
        
        print("SIM7020E initialized successfully")
        return True
    except Exception as e:
        print("SIM7020E initialization failed:", e)
        return False

def http_get(url, endpoint):
    """Make HTTP GET request"""
    try:
        print("Making HTTP GET request to:", url + endpoint)
        sendCMD_waitResp("AT+CHTTPCREATE=\"{}\"".format(url))
        utime.sleep(1)
        sendCMD_waitResp("AT+CHTTPCON=0")
        utime.sleep(2)
        
        response = sendCMD_waitResp("AT+CHTTPSEND=0,0,\"{}\"".format(endpoint))
        utime.sleep(3)
        
        # Get response data
        data_resp = sendCMD_waitResp("AT+CHTTPREAD=0")
        
        sendCMD_waitResp("AT+CHTTPDISCON=0")
        sendCMD_waitResp("AT+CHTTPDESTROY=0")
        
        return data_resp
    except Exception as e:
        print("HTTP GET failed:", e)
        return None

def check_for_update():
    """Check if there's a new version available"""
    try:
        print("Checking for updates...")
        
        # Create request payload
        check_payload = {
            "device_id": DEVICE_ID,
            "current_version": VERSION,
            "action": "check_update"
        }
        
        json_payload = json.dumps(check_payload)
        hex_payload = str_to_hexStr(json_payload)
        
        # Make request
        sendCMD_waitResp("AT+CHTTPCREATE=\"{}\"".format(OTA_SERVER))
        utime.sleep(1)
        sendCMD_waitResp("AT+CHTTPCON=0")
        utime.sleep(2)
        
        post_cmd = "AT+CHTTPSEND=0,1,\"/ota\",,\"application/json\",{}".format(hex_payload)
        sendCMD_waitResp(post_cmd)
        utime.sleep(3)
        
        # Get response
        response = sendCMD_waitResp("AT+CHTTPREAD=0")
        
        sendCMD_waitResp("AT+CHTTPDISCON=0")
        sendCMD_waitResp("AT+CHTTPDESTROY=0")
        
        # Parse response
        if response and "update_available" in response:
            try:
                # Extract JSON from response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_str = response[json_start:json_end]
                    update_info = json.loads(json_str)
                    return update_info
            except:
                pass
        
        return None
    except Exception as e:
        print("Update check failed:", e)
        return None

def download_update():
    """Download new code from server"""
    try:
        print("Downloading update...")
        led_blink_pattern("updating")
        
        # Request download
        download_payload = {
            "device_id": DEVICE_ID,
            "action": "download_update"
        }
        
        json_payload = json.dumps(download_payload)
        hex_payload = str_to_hexStr(json_payload)
        
        sendCMD_waitResp("AT+CHTTPCREATE=\"{}\"".format(OTA_SERVER))
        utime.sleep(1)
        sendCMD_waitResp("AT+CHTTPCON=0")
        utime.sleep(2)
        
        post_cmd = "AT+CHTTPSEND=0,1,\"/ota\",,\"application/json\",{}".format(hex_payload)
        sendCMD_waitResp(post_cmd)
        utime.sleep(5)  # Longer timeout for download
        
        # Get response with code
        response = sendCMD_waitResp("AT+CHTTPREAD=0", timeout=10000)
        
        sendCMD_waitResp("AT+CHTTPDISCON=0")
        sendCMD_waitResp("AT+CHTTPDESTROY=0")
        
        if response and "new_code" in response:
            try:
                # Extract JSON from response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_str = response[json_start:json_end]
                    update_data = json.loads(json_str)
                    
                    if "new_code" in update_data:
                        # Decode the new code
                        new_code = hexStr_to_str(update_data["new_code"])
                        return new_code
            except Exception as e:
                print("Failed to parse update data:", e)
        
        return None
    except Exception as e:
        print("Download failed:", e)
        return None

def apply_update(new_code):
    """Apply the downloaded update"""
    try:
        print("Applying update...")
        led_blink_pattern("updating")
        
        # Backup current main.py
        try:
            with open("main.py", "r") as f:
                current_code = f.read()
            with open("main_backup.py", "w") as f:
                f.write(current_code)
            print("Backup created")
        except:
            print("Backup creation failed")
        
        # Write new code
        with open("main.py", "w") as f:
            f.write(new_code)
        
        print("Update applied successfully")
        print("Restarting in 3 seconds...")
        utime.sleep(3)
        machine.reset()
        
    except Exception as e:
        print("Update application failed:", e)
        led_blink_pattern("error")
        return False

def perform_ota_update():
    """Main OTA update function"""
    try:
        print("=== Starting OTA Update Check ===")
        
        # Check for updates
        update_info = check_for_update()
        
        if update_info and update_info.get("update_available"):
            print("Update available! Version:", update_info.get("new_version"))
            
            # Download update
            new_code = download_update()
            
            if new_code:
                print("Code downloaded successfully")
                
                # Apply update
                apply_update(new_code)
            else:
                print("Failed to download update")
                return False
        else:
            print("No updates available")
            return True
            
    except Exception as e:
        print("OTA update failed:", e)
        led_blink_pattern("error")
        return False

def main():
    """Main application loop"""
    print("=== Raspberry Pi Pico OTA System ===")
    print("Version:", VERSION)
    print("Device ID:", DEVICE_ID)
    
    # Initialize SIM7020E
    if not init_sim7020():
        print("Failed to initialize SIM7020E")
        while True:
            led_blink_pattern("error")
            utime.sleep(2)
    
    # Main loop
    update_counter = 0
    while True:
        try:
            print("\n--- Main Loop ---")
            
            # Normal operation - blink LED
            led_blink_pattern("default")
            
            # Check for OTA updates every 10 loops (adjust as needed)
            update_counter += 1
            if update_counter >= 10:
                update_counter = 0
                perform_ota_update()
            
            # Wait before next iteration
            utime.sleep(5)
            
        except Exception as e:
            print("Main loop error:", e)
            led_blink_pattern("error")
            utime.sleep(5)

# Run main application
if __name__ == "__main__":
    main()
