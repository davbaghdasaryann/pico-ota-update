const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static('public'));

// Store device information and available updates
const devices = new Map();
const availableUpdates = new Map();

// Initialize with test updates
function initializeUpdates() {
    // Load test blink codes
    const testCode1 = fs.readFileSync(path.join(__dirname, 'test_blink_1.py'), 'utf8');
    const testCode2 = fs.readFileSync(path.join(__dirname, 'test_blink_2.py'), 'utf8');
    
    availableUpdates.set('2.0.0', {
        version: '2.0.0',
        description: 'Fast blink pattern test',
        code: testCode1,
        hex_code: Buffer.from(testCode1).toString('hex')
    });
    
    availableUpdates.set('3.0.0', {
        version: '3.0.0',
        description: 'Slow pulse pattern test',
        code: testCode2,
        hex_code: Buffer.from(testCode2).toString('hex')
    });
    
    console.log('Initialized with', availableUpdates.size, 'available updates');
}

// Helper function to get next version
function getNextVersion(currentVersion) {
    const versions = Array.from(availableUpdates.keys()).sort();
    const currentIndex = versions.indexOf(currentVersion);
    
    if (currentIndex === -1) {
        // Current version not found, return first available
        return versions[0];
    }
    
    if (currentIndex < versions.length - 1) {
        // Return next version
        return versions[currentIndex + 1];
    }
    
    // Already at latest version
    return null;
}

// Helper function to convert string to hex
function stringToHex(str) {
    return Buffer.from(str, 'utf8').toString('hex');
}

// Helper function to convert hex to string
function hexToString(hex) {
    return Buffer.from(hex, 'hex').toString('utf8');
}

// Main OTA endpoint
app.post('/ota', (req, res) => {
    try {
        const { device_id, current_version, action } = req.body;
        
        console.log(`OTA request from ${device_id}: ${action} (current: ${current_version})`);
        
        // Update device info
        devices.set(device_id, {
            device_id,
            current_version,
            last_seen: new Date(),
            ip: req.ip
        });
        
        if (action === 'check_update') {
            // Check if update is available
            const nextVersion = getNextVersion(current_version);
            
            if (nextVersion) {
                const updateInfo = availableUpdates.get(nextVersion);
                res.json({
                    update_available: true,
                    new_version: nextVersion,
                    description: updateInfo.description,
                    current_version: current_version
                });
                console.log(`Update available for ${device_id}: ${current_version} -> ${nextVersion}`);
            } else {
                res.json({
                    update_available: false,
                    message: 'Device is up to date',
                    current_version: current_version
                });
                console.log(`No update available for ${device_id}`);
            }
        } else if (action === 'download_update') {
            // Provide the update code
            const nextVersion = getNextVersion(current_version);
            
            if (nextVersion) {
                const updateInfo = availableUpdates.get(nextVersion);
                res.json({
                    success: true,
                    version: nextVersion,
                    description: updateInfo.description,
                    new_code: updateInfo.hex_code
                });
                console.log(`Sent update ${nextVersion} to ${device_id}`);
            } else {
                res.json({
                    success: false,
                    error: 'No update available'
                });
            }
        } else {
            res.status(400).json({
                success: false,
                error: 'Invalid action'
            });
        }
    } catch (error) {
        console.error('OTA endpoint error:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error'
        });
    }
});

// Get device status
app.get('/devices', (req, res) => {
    const deviceList = Array.from(devices.values());
    res.json({
        devices: deviceList,
        total_devices: deviceList.length
    });
});

// Get available updates
app.get('/updates', (req, res) => {
    const updateList = Array.from(availableUpdates.values()).map(update => ({
        version: update.version,
        description: update.description,
        code_size: update.code.length
    }));
    res.json({
        updates: updateList,
        total_updates: updateList.length
    });
});

// Add new update (for testing)
app.post('/updates', (req, res) => {
    try {
        const { version, description, code } = req.body;
        
        if (!version || !description || !code) {
            return res.status(400).json({
                success: false,
                error: 'Missing required fields: version, description, code'
            });
        }
        
        availableUpdates.set(version, {
            version,
            description,
            code,
            hex_code: stringToHex(code)
        });
        
        res.json({
            success: true,
            message: `Update ${version} added successfully`
        });
        
        console.log(`New update added: ${version}`);
    } catch (error) {
        console.error('Add update error:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error'
        });
    }
});

// Delete update
app.delete('/updates/:version', (req, res) => {
    const version = req.params.version;
    
    if (availableUpdates.has(version)) {
        availableUpdates.delete(version);
        res.json({
            success: true,
            message: `Update ${version} deleted successfully`
        });
        console.log(`Update deleted: ${version}`);
    } else {
        res.status(404).json({
            success: false,
            error: 'Update not found'
        });
    }
});

// Get specific update code (for debugging)
app.get('/updates/:version/code', (req, res) => {
    const version = req.params.version;
    const update = availableUpdates.get(version);
    
    if (update) {
        res.type('text/plain');
        res.send(update.code);
    } else {
        res.status(404).json({
            success: false,
            error: 'Update not found'
        });
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'OK',
        timestamp: new Date().toISOString(),
        devices_connected: devices.size,
        updates_available: availableUpdates.size
    });
});

// Serve web interface
app.get('/', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html>
<head>
    <title>Raspberry Pi Pico OTA Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; }
        .button { padding: 10px 20px; margin: 5px; background: #007cba; color: white; border: none; cursor: pointer; }
        .button:hover { background: #005a87; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .status { padding: 4px 8px; border-radius: 4px; }
        .online { background: #d4edda; color: #155724; }
        .offline { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Raspberry Pi Pico OTA Server</h1>
        
        <div class="section">
            <h2>Server Status</h2>
            <p>Status: <span class="status online">Online</span></p>
            <p>Connected Devices: <span id="device-count">0</span></p>
            <p>Available Updates: <span id="update-count">0</span></p>
        </div>
        
        <div class="section">
            <h2>Actions</h2>
            <button class="button" onclick="refreshData()">Refresh Data</button>
            <button class="button" onclick="viewDevices()">View Devices</button>
            <button class="button" onclick="viewUpdates()">View Updates</button>
        </div>
        
        <div class="section">
            <h2>Connected Devices</h2>
            <div id="devices-table"></div>
        </div>
        
        <div class="section">
            <h2>Available Updates</h2>
            <div id="updates-table"></div>
        </div>
    </div>

    <script>
        function refreshData() {
            fetch('/devices')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('device-count').textContent = data.total_devices;
                    displayDevices(data.devices);
                });
            
            fetch('/updates')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('update-count').textContent = data.total_updates;
                    displayUpdates(data.updates);
                });
        }
        
        function displayDevices(devices) {
            const html = devices.length > 0 ? 
                '<table><tr><th>Device ID</th><th>Current Version</th><th>Last Seen</th><th>IP</th></tr>' +
                devices.map(device => 
                    '<tr>' +
                    '<td>' + device.device_id + '</td>' +
                    '<td>' + device.current_version + '</td>' +
                    '<td>' + new Date(device.last_seen).toLocaleString() + '</td>' +
                    '<td>' + device.ip + '</td>' +
                    '</tr>'
                ).join('') + '</table>' :
                '<p>No devices connected</p>';
            
            document.getElementById('devices-table').innerHTML = html;
        }
        
        function displayUpdates(updates) {
            const html = updates.length > 0 ?
                '<table><tr><th>Version</th><th>Description</th><th>Code Size</th></tr>' +
                updates.map(update => 
                    '<tr>' +
                    '<td>' + update.version + '</td>' +
                    '<td>' + update.description + '</td>' +
                    '<td>' + update.code_size + ' bytes</td>' +
                    '</tr>'
                ).join('') + '</table>' :
                '<p>No updates available</p>';
            
            document.getElementById('updates-table').innerHTML = html;
        }
        
        function viewDevices() {
            refreshData();
        }
        
        function viewUpdates() {
            refreshData();
        }
        
        // Initial load
        refreshData();
        
        // Auto-refresh every 30 seconds
        setInterval(refreshData, 30000);
    </script>
</body>
</html>
    `);
});

// Start server
app.listen(PORT, () => {
    console.log(`OTA Server running on port ${PORT}`);
    console.log(`Web interface: http://localhost:${PORT}`);
    console.log(`Health check: http://localhost:${PORT}/health`);
    
    // Initialize with test updates
    initializeUpdates();
});
