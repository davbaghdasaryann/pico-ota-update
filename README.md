# Raspberry Pi Pico OTA Update System

This is a complete Over-The-Air (OTA) update system for Raspberry Pi Pico using MicroPython and SIM7020E.

## Components

1. **Main OTA Code** - Runs on the Pico, checks for and applies updates
2. **Test Blink Codes** - Two different LED blink patterns for testing
3. **Node.js Server** - Serves updates and manages devices

## Setup Instructions

### 1. Server Setup

#### Prerequisites
- Node.js (version 14 or higher)
- npm (comes with Node.js)

#### Installation
```bash
# Create project directory
mkdir pico-ota-server
cd pico-ota-server

# Save the package.json file
# Save the server.js file (Node.js OTA Server code)

# Install dependencies
npm install

# For development (optional)
npm install -g nodemon
```

#### Create Test Files
Save the two test blink codes as:
- `test_blink_1.py` - Fast blink pattern
- `test_blink_2.py` - Slow pulse pattern

#### Start Server
```bash
# Production
npm start

# Development (auto-restart on changes)
npm run dev
```

The server will start on port 3000. Access the web interface at `http://localhost:3000`

### 2. Raspberry Pi Pico Setup

#### Prerequisites
- Raspberry Pi Pico with MicroPython installed
- SIM7020E module connected
- LED on pin 25 (onboard LED)

#### Hardware Connections
```
SIM7020E -> Pico
TX       -> GP1 (UART0 RX)
RX       -> GP0 (UART0 TX)
PWR_EN   -> GP14
VCC      -> 3.3V
GND      -> GND
```

#### Installation
1. Save the main OTA code as `main.py` on your Pico
2. Update the server URL in the code:
   ```python
   OTA_SERVER = "http://your-server-ip:3000"  # Replace with your server
   ```
3. Configure your APN if different:
   ```python
   APN = "your-apn-here"  # Replace with your carrier's APN
   ```

### 3. Testing the System

#### Initial Test
1. Start the server
2. Upload main OTA code to Pico
3. Power on the Pico
4. Watch the serial output for connection and OTA check messages

#### Test Update Process
1. The main code (version 1.0.0) will check for updates every 10 loops
2. Server will offer version 2.0.0 (fast blink)
3. Pico will download and apply the update, then restart
4. New code will run with fast blink pattern
5. Next update check will offer version 3.0.0 (slow pulse)

## API Endpoints

### Check for Updates
```http
POST /ota
Content-Type: application/json

{
  "device_id": "pico_001",
  "current_version": "1.0.0",
  "action": "check_update"
}
```

### Download Update
```http
POST /ota
Content-Type: application/json

{
  "device_id": "pico_001",
  "action": "download_update"
}
```

### View Devices
```http
GET /devices
```

### View Available Updates
```http
GET /updates
```

### Add New Update
```http
POST /updates
Content-Type: application/json

{
  "version": "4.0.0",
  "description": "New feature update",
  "code": "# Python code here..."
}
```

## Configuration

### Server Configuration
- Port: Set `PORT` environment variable (default: 3000)
- Updates: Modify `initializeUpdates()` function to add more updates

### Pico Configuration
- Update interval: Modify the counter check in main loop
- Server URL: Update `OTA_SERVER` variable
- Device ID: Change `DEVICE_ID` for multiple devices
- APN: Update `APN` variable for your carrier

## Features

### Server Features
- ✅ Web interface for monitoring
- ✅ Device management
- ✅ Update management
- ✅ Version control
- ✅ Hex encoding/decoding
- ✅ RESTful API
- ✅ Real-time device status

### Pico Features
- ✅ Automatic update checking
- ✅ Code download and application
- ✅ Backup creation
- ✅ Error handling and recovery
- ✅ LED status indicators
- ✅ Version management
- ✅ SIM7020E communication

## LED Status Indicators

- **Default Blink**: Normal operation (0.5s on/off)
- **Fast Blink**: Update in progress (0.1s on/off)
- **SOS Pattern**: Error occurred (3 short, 3 long, 3 short)

## Troubleshooting

### Common Issues

1. **No AT Command Response**
   - Check SIM7020E connections
   - Verify power supply
   - Check UART configuration

2. **Update Download Fails**
   - Verify server URL is correct
   - Check network connectivity
   - Ensure APN is configured correctly

3. **Update Application Fails**
   - Check available memory
   - Verify code syntax
   - Look for backup file (main_backup.py)

### Debug Tips

1. **Enable Verbose Logging**
   ```python
   # Add more print statements in OTA functions
   print("Debug: Current step...")
   ```

2. **Manual Testing**
   ```python
   # Test individual functions
   perform_ota_update()
   ```

3. **Server Logs**
   - Check console output for server errors
   - Monitor device connections in web interface

## Security Considerations

### For Production Use
- Add authentication to OTA endpoints
- Use HTTPS instead of HTTP
- Implement code signing/verification
- Add rate limiting
- Validate device IDs
- Encrypt communications

### Example Security Enhancement
```javascript
// Add to server.js
const crypto = require('crypto');

function verifyDevice(device_id, signature) {
    // Implement device verification
    return true; // Placeholder
}

function signCode(code) {
    // Implement code signing
    return crypto.createHash('sha256').update(code).digest('hex');
}
```

## Extending the System

### Adding New Features
1. **Multiple File Updates**: Extend to update multiple files
2. **Rollback Capability**: Add automatic rollback on failure
3. **Scheduled Updates**: Add time-based update scheduling
4. **Update Channels**: Support beta/stable update channels
5. **Compression**: Add code compression for large updates

### Example Extension
```python
# Add to Pico code for rollback
def rollback_update():
    try:
        with open("main_backup.py", "r") as f:
            backup_code = f.read()
        with open("main.py", "w") as f:
            f.write(backup_code)
        machine.reset()
    except:
        print("Rollback failed")
```

## License

MIT License - Feel free to modify and use for your projects.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review server logs and Pico serial output
3. Verify hardware connections
4. Test with minimal code first
