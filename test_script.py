#!/usr/bin/env python3
"""
Test Script for OTA System
Run this on your computer to test the server functionality
"""

import requests
import json
import time

# Configuration
SERVER_URL = "http://localhost:3000"
DEVICE_ID = "test_device_001"

def test_health_check():
    """Test server health"""
    print("Testing server health...")
    try:
        response = requests.get(f"{SERVER_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is healthy: {data['status']}")
            print(f"   Devices: {data['devices_connected']}")
            print(f"   Updates: {data['updates_available']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_check_update(current_version="1.0.0"):
    """Test update checking"""
    print(f"\nTesting update check for version {current_version}...")
    try:
        payload = {
            "device_id": DEVICE_ID,
            "current_version": current_version,
            "action": "check_update"
        }
        
        response = requests.post(f"{SERVER_URL}/ota", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("update_available"):
                print(f"✅ Update available: {data['current_version']} -> {data['new_version']}")
                print(f"   Description: {data['description']}")
                return data['new_version']
            else:
                print(f"✅ No update available: {data['message']}")
                return None
        else:
            print(f"❌ Update check failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Update check error: {e}")
        return None

def test_download_update():
    """Test update download"""
    print("\nTesting update download...")
    try:
        payload = {
            "device_id": DEVICE_ID,
            "action": "download_update"
        }
        
        response = requests.post(f"{SERVER_URL}/ota", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ Update downloaded: {data['version']}")
                print(f"   Description: {data['description']}")
                print(f"   Code size: {len(data['new_code']) // 2} bytes")
                return data
            else:
                print(f"❌ Download failed: {data.get('error')}")
                return None
        else:
            print(f"❌ Download failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Download error: {e}")
        return None

def test_get_devices():
    """Test getting device list"""
    print("\nTesting device list...")
    try:
        response = requests.get(f"{SERVER_URL}/devices")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total_devices']} devices:")
            for device in data['devices']:
                print(f"   - {device['device_id']} (v{device['current_version']})")
            return data['devices']
        else:
            print(f"❌ Device list failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Device list error: {e}")
        return None

def test_get_updates():
    """Test getting update list"""
    print("\nTesting update list...")
    try:
        response = requests.get(f"{SERVER_URL}/updates")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total_updates']} updates:")
            for update in data['updates']:
                print(f"   - v{update['version']}: {update['description']} ({update['code_size']} bytes)")
            return data['updates']
        else:
            print(f"❌ Update list failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Update list error: {e}")
        return None

def test_add_custom_update():
    """Test adding a custom update"""
    print("\nTesting custom update addition...")
    
    custom_code = '''"""
Custom Test Code - LED Sequence
Version 4.0.0
"""
import machine
import utime

VERSION = "4.0.0"
led = machine.Pin(25, machine.Pin.OUT)

def main():
    print("Custom test code running!")
    counter = 0
    while True:
        # Sequence: 1-2-3 blinks
        for i in range(1, 4):
            for _ in range(i):
                led.value(1)
                utime.sleep(0.2)
                led.value(0)
                utime.sleep(0.2)
            utime.sleep(1)
        counter += 1
        if counter % 5 == 0:
            print(f"Sequence count: {counter}")

if __name__ == "__main__":
    main()
'''
    
    try:
        payload = {
            "version": "4.0.0",
            "description": "Custom LED sequence test",
            "code": custom_code
        }
        
        response = requests.post(f"{SERVER_URL}/updates", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Custom update added: {data['message']}")
            return True
        else:
            print(f"❌ Custom update failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Custom update error: {e}")
        return False

def simulate_device_lifecycle():
    """Simulate a complete device update lifecycle"""
    print("\n" + "="*50)
    print("SIMULATING DEVICE UPDATE LIFECYCLE")
    print("="*50)
    
    current_version = "1.0.0"
    
    # Step 1: Check for updates
    new_version = test_check_update(current_version)
    if not new_version:
        print("No updates available, lifecycle complete")
        return
    
    # Step 2: Download update
    update_data = test_download_update()
    if not update_data:
        print("Download failed, lifecycle aborted")
        return
    
    # Step 3: Simulate applying update
    print(f"\n📦 Simulating update application...")
    print(f"   Current: {current_version}")
    print(f"   New: {new_version}")
    print(f"   ✅ Update would be applied successfully!")
    
    # Step 4: Check next update
    print(f"\n🔄 Checking for next update after {new_version}...")
    next_version = test_check_update(new_version)
    if next_version:
        print(f"   Next available: {next_version}")
    else:
        print("   Device would be up to date")

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting OTA System Tests")
    print("="*50)
    
    # Basic connectivity
    if not test_health_check():
        print("❌ Server not accessible, stopping tests")
        return False
    
    # Test endpoints
    test_get_updates()
    test_get_devices()
    
    # Test OTA flow
    test_check_update("1.0.0")
    test_check_update("2.0.0")
    test_check_update("3.0.0")  # Should be up to date
    
    # Test download
    test_download_update()
    
    # Add custom update
    test_add_custom_update()
    
    # Test updated list
    test_get_updates()
    
    # Full lifecycle simulation
    simulate_device_lifecycle()
    
    print("\n✅ All tests completed!")
    return True

def interactive_test():
    """Interactive test mode"""
    while True:
        print("\n" + "="*40)
        print("OTA System Interactive Test")
        print("="*40)
        print("1. Health Check")
        print("2. Check for Updates")
        print("3. Download Update")
        print("4. List Devices")
        print("5. List Updates")
        print("6. Add Custom Update")
        print("7. Full Lifecycle Test")
        print("8. Run All Tests")
        print("9. Exit")
        
        choice = input("\nSelect option (1-9): ").strip()
        
        if choice == "1":
            test_health_check()
        elif choice == "2":
            version = input("Enter current version (default: 1.0.0): ").strip()
            if not version:
                version = "1.0.0"
            test_check_update(version)
        elif choice == "3":
            test_download_update()
        elif choice == "4":
            test_get_devices()
        elif choice == "5":
            test_get_updates()
        elif choice == "6":
            test_add_custom_update()
        elif choice == "7":
            simulate_device_lifecycle()
        elif choice == "8":
            run_all_tests()
        elif choice == "9":
            print("Goodbye!")
            break
        else:
            print("Invalid option, please try again")

if __name__ == "__main__":
    import sys
    
    print("OTA System Test Script")
    print("Make sure your server is running on", SERVER_URL)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        run_all_tests()
