# CCN Project - Modular Socket-Based Server-Client Communication

A comprehensive Python socket project for Computer Communication Networks course, with all server components broken down into separate, easy-to-understand modules.

---

## 📁 Project Structure

```
ccn-project/
├── server.py                 # Main server file (orchestrates all modules)
├── client.py                 # Basic client for review
├── weather_api.py            # Weather data module (modular & easy to modify)
├── requirements.txt          # Python dependencies
├── README.md                 # This comprehensive guide
├── server_log.txt            # Server logs (created automatically)
└── modules/                  # All server modules (8 main components)
    ├── __init__.py
    ├── server_connection.py  # Module 1: Server Initialization & Connection Handling
    ├── authentication.py    # Module 2: Client Authentication (Login System)
    ├── encryption.py         # Module 3: Secure Communication (Encryption/Decryption)
    ├── alert_generator.py    # Module 4: Alert Generation and Priority System
    ├── broadcaster.py        # Module 5: Broadcasting System
    ├── acknowledgment.py     # Module 6: Client Acknowledgment Handling
    ├── logger.py             # Module 7: Logging and Monitoring
    ├── shutdown.py           # Module 8: Graceful Shutdown & Exception Handling
    └── message_handler.py    # Shared: Common message sending/receiving functions
```

---

## 🎯 Overview of All 8 Modules

### **Module 1: Server Initialization & Connection Handling** (`modules/server_connection.py`)

**What it does:**
- Creates a TCP socket server
- Binds to a specific host and port (127.0.0.1:8888)
- Listens for incoming client connections
- Handles each client in a separate thread (allows multiple clients simultaneously)
- Manages the main server loop

**Key Functions:**
- `start_server()` - Initializes and starts the TCP server
- `handle_client()` - Processes each new client connection

**How it works:**
1. Creates a socket using `socket.socket(socket.AF_INET, socket.SOCK_STREAM)`
2. Binds to HOST:PORT and starts listening
3. When a client connects, accepts the connection
4. Creates a new thread for each client (so server can handle multiple clients at once)
5. Each client thread runs `handle_client()` function

**Testing:**
- Start server: `python server.py`
- You should see: "Server started on 127.0.0.1:8888"
- Try connecting multiple clients - all should connect successfully

---

### **Module 2: Client Authentication (Login System)** (`modules/authentication.py`)

**What it does:**
- Verifies username and password before allowing client access
- Maintains a user database (dictionary of username:password)
- Sends authentication prompts to client
- Returns username if successful, None if failed

**Key Functions:**
- `authenticate_client(client_socket, address)` - Main authentication function
- `add_user(username, password)` - Add new user to system

**How it works:**
1. Server sends "USERNAME:" prompt to client
2. Client responds with username
3. Server sends "PASSWORD:" prompt to client
4. Client responds with password
5. Server checks if username exists and password matches
6. Sends "AUTH_SUCCESS" or "AUTH_FAILED" back to client

**Default Users:**
```python
USERS = {
    "admin": "admin123",
    "user1": "pass123",
    "user2": "pass456"
}
```

**Testing:**
1. Start server
2. Connect client and try:
   - ✅ Correct: username="admin", password="admin123" → Should authenticate
   - ❌ Wrong: username="admin", password="wrong" → Should fail
   - ❌ Wrong: username="unknown", password="anything" → Should fail

**To add new users:**
Edit `modules/authentication.py`:
```python
USERS = {
    "admin": "admin123",
    "user1": "pass123",
    "user2": "pass456",
    "newuser": "newpass"  # Add your user here
}
```

---

### **Module 3: Secure Communication (Encryption & Decryption)** (`modules/encryption.py`)

**What it does:**
- Encrypts all messages before sending (using AES encryption via Fernet)
- Decrypts all received messages
- Generates encryption key that must be shared with clients
- Ensures data security during transmission

**Key Functions:**
- `encrypt_message(message)` - Encrypts a string message
- `decrypt_message(encrypted_data)` - Decrypts encrypted bytes
- `get_encryption_key()` - Returns the encryption key (to share with clients)

**How it works:**
1. Uses Fernet (symmetric encryption) - same key for encrypt and decrypt
2. When server starts, generates a random encryption key
3. All messages are encrypted before sending over socket
4. All received messages are decrypted before processing
5. Client must have the same key to communicate

**Encryption Flow:**
```
Server: "Hello" → encrypt → [encrypted bytes] → send over socket
Client: receive → decrypt → "Hello"
```

**Testing:**
1. Start server - note the encryption key displayed
2. Copy key to client.py: `ENCRYPTION_KEY = b'paste_key_here'`
3. Try connecting - messages should be encrypted/decrypted automatically
4. Try wrong key in client - should get decryption errors

**Security Note:**
- In production, share key securely (not hardcoded)
- Consider using SSL/TLS for key exchange
- Current implementation uses symmetric encryption (same key for both)

---

### **Module 4: Alert Generation and Priority System** (`modules/alert_generator.py`)

**What it does:**
- Generates alerts based on weather data
- Assigns priority levels: LOW, MEDIUM, HIGH
- Creates unique alert IDs
- Uses weather_api.py to get environmental data

**Key Functions:**
- `generate_alert()` - Creates a new alert with priority

**How it works:**
1. Calls `weather_api.get_current_weather()` to get weather data
2. Analyzes temperature and humidity:
   - **HIGH Priority**: temp > 30°C OR humidity > 80%
   - **MEDIUM Priority**: temp > 25°C OR humidity > 60%
   - **LOW Priority**: Otherwise
3. Creates alert dictionary with:
   - Priority level
   - Message (weather information)
   - Timestamp
   - Unique alert ID (based on current time)

**Alert Structure:**
```python
{
    "priority": "HIGH",  # or "MEDIUM" or "LOW"
    "message": "Weather Alert: Temp: 32°C, Humidity: 85%, Condition: Sunny",
    "timestamp": "2024-01-01 12:00:00",
    "alert_id": 1234567890
}
```

**Testing:**
1. Check `weather_api.py` - it generates random weather data
2. Run server - alerts generated every 30 seconds
3. Check logs - you'll see alert generation messages
4. Modify `weather_api.py` to return specific values to test priority:
   ```python
   # Force HIGH priority
   return {"temperature": 35, "humidity": 90, ...}
   ```

**To modify alert logic:**
Edit `modules/alert_generator.py` - change the priority conditions:
```python
if weather["temperature"] > 30:  # Change threshold
    priority = "HIGH"
```

---

### **Module 5: Broadcasting System** (`modules/broadcaster.py`)

**What it does:**
- Sends alerts to ALL connected clients simultaneously
- Handles disconnected clients gracefully
- Uses thread-safe operations (locks) to prevent conflicts

**Key Functions:**
- `broadcast_alert(alert, active_clients, lock)` - Sends alert to all clients

**How it works:**
1. Receives an alert from alert generator
2. Converts alert to JSON string
3. Loops through all active clients
4. Sends "ALERT:{json_data}" to each client
5. If sending fails (client disconnected), removes from active list
6. Uses lock to ensure thread-safe access to active_clients dictionary

**Broadcasting Flow:**
```
Alert Generated → broadcast_alert() → 
  For each client:
    - Send encrypted alert message
    - Log success/failure
    - Remove disconnected clients
```

**Testing:**
1. Start server
2. Connect multiple clients (2-3 clients)
3. Wait for alert (30 seconds)
4. All clients should receive the same alert simultaneously
5. Check server logs - should show "BROADCAST" messages for each client
6. Disconnect one client - next alert should only go to remaining clients

**Thread Safety:**
- Uses `lock` (threading.Lock()) to prevent race conditions
- Multiple threads can't modify `active_clients` at the same time
- Ensures data integrity when multiple clients connect/disconnect

---

### **Module 6: Client Acknowledgment Handling** (`modules/acknowledgment.py`)

**What it does:**
- Receives ACK (acknowledgment) messages from clients
- Confirms that clients received alerts successfully
- Handles heartbeat messages to keep connections alive
- Logs all acknowledgments

**Key Functions:**
- `handle_client_acknowledgment(...)` - Main ACK handling function (runs in thread)

**How it works:**
1. Runs in a separate thread for each client
2. Continuously listens for messages from client
3. If message starts with "ACK:" → extracts alert ID and logs it
4. If message is "HEARTBEAT" → responds with "HEARTBEAT_OK" (keeps connection alive)
5. If connection lost → removes client from active list

**ACK Flow:**
```
Client receives alert → Client sends "ACK:1234567890" → 
Server receives ACK → Logs acknowledgment → Continues listening
```

**Testing:**
1. Start server and connect client
2. Wait for alert
3. Client should automatically send ACK
4. Check server logs - should see "ACK" entries:
   ```
   [2024-01-01 12:00:05] [ACK] Received ACK from admin for alert 1234567890
   ```
5. Check `server_log.txt` file - all ACKs are logged there

**Heartbeat:**
- Clients can send "HEARTBEAT" to check if server is alive
- Server responds with "HEARTBEAT_OK"
- Useful for detecting dead connections

---

### **Module 7: Logging and Monitoring** (`modules/logger.py`)

**What it does:**
- Logs all server events with timestamps
- Writes to both console (screen) and file (`server_log.txt`)
- Categorizes events by type (CONNECTION, AUTH, ALERT, etc.)

**Key Functions:**
- `log_event(event_type, message)` - Logs an event

**How it works:**
1. Gets current timestamp
2. Formats message: `[timestamp] [EVENT_TYPE] message`
3. Prints to console (so you can see it)
4. Appends to `server_log.txt` file

**Event Types:**
- `CONNECTION` - Client connects/disconnects
- `AUTH` - Authentication attempts (success/failure)
- `ALERT` - Alert generation
- `BROADCAST` - Alert sent to client
- `ACK` - Acknowledgment received
- `DISCONNECT` - Client disconnected
- `ERROR` - Errors occurred
- `SERVER` - Server start/shutdown
- `MESSAGE` - Other messages

**Testing:**
1. Start server - check console output
2. Connect client - see CONNECTION and AUTH logs
3. Wait for alert - see ALERT and BROADCAST logs
4. Check `server_log.txt` file - all events saved there
5. Try wrong password - see AUTH failure log

**Log File Format:**
```
[2024-01-01 12:00:00] [SERVER] Server started on 127.0.0.1:8888
[2024-01-01 12:00:05] [CONNECTION] New connection from ('127.0.0.1', 54321)
[2024-01-01 12:00:06] [AUTH] Client ('127.0.0.1', 54321) authenticated as admin
[2024-01-01 12:00:30] [ALERT] Generated HIGH priority alert: Weather Alert: ...
[2024-01-01 12:00:30] [BROADCAST] Alert sent to admin (('127.0.0.1', 54321))
[2024-01-01 12:00:31] [ACK] Received ACK from admin for alert 1234567890
```

---

### **Module 8: Graceful Shutdown & Exception Handling** (`modules/shutdown.py`)

**What it does:**
- Safely closes all client connections
- Closes server socket
- Handles errors gracefully
- Ensures clean exit

**Key Functions:**
- `shutdown_server(server_socket, active_clients, lock)` - Shuts down everything

**How it works:**
1. Sends "SERVER_SHUTDOWN" message to all clients
2. Closes all client sockets
3. Clears active_clients dictionary
4. Closes server socket
5. Logs shutdown event

**Testing:**
1. Start server with multiple clients connected
2. Press Ctrl+C to stop server
3. Check that:
   - All clients receive "SERVER_SHUTDOWN" message
   - Server closes cleanly (no errors)
   - Log shows "Server shutdown complete"
4. Try closing client while server running - should handle gracefully

**Exception Handling:**
- All modules use try-except blocks
- Errors are logged, not crashed
- Server continues running even if one client has issues

---

## 🚀 Installation & Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `cryptography` - For encryption/decryption

### Step 2: Start the Server

```bash
python server.py
```

**What happens:**
1. Server starts on `127.0.0.1:8888`
2. Encryption key is displayed (COPY THIS!)
3. Server waits for clients
4. Logs are written to console and `server_log.txt`

**Example output:**
```
==================================================
SERVER STARTING...
==================================================
Encryption Key (share with clients): gAAAAABl...
==================================================

[2024-01-01 12:00:00] [SERVER] Server started on 127.0.0.1:8888
[2024-01-01 12:00:00] [SERVER] Waiting for clients...
```

### Step 3: Configure Client

1. Open `client.py`
2. Find this line:
   ```python
   ENCRYPTION_KEY = b''  # Paste server's encryption key here
   ```
3. Paste the encryption key from server output:
   ```python
   ENCRYPTION_KEY = b'gAAAAABl...'  # Your key here
   ```

### Step 4: Run Client

```bash
python client.py
```

**What happens:**
1. Client connects to server
2. Prompts for username
3. Prompts for password
4. If authenticated, receives welcome message
5. Waits for alerts

---

## 🧪 Complete Testing Guide

### Test 1: Basic Connection

**Goal:** Verify server accepts connections

**Steps:**
1. Start server: `python server.py`
2. In another terminal, start client: `python client.py`
3. Enter credentials: `admin` / `admin123`

**Expected:**
- ✅ Client connects successfully
- ✅ Authentication succeeds
- ✅ Welcome message received
- ✅ Server log shows: `[CONNECTION]` and `[AUTH]` entries

---

### Test 2: Authentication System

**Goal:** Test login with correct/incorrect credentials

**Steps:**
1. Start server
2. Test Case A - Correct credentials:
   - Client: username=`admin`, password=`admin123`
   - Expected: ✅ "Authentication successful!"
3. Test Case B - Wrong password:
   - Client: username=`admin`, password=`wrong`
   - Expected: ❌ "Authentication failed!"
4. Test Case C - Unknown user:
   - Client: username=`unknown`, password=`anything`
   - Expected: ❌ "Authentication failed!"

**Check logs:**
- Success: `[AUTH] Client ... authenticated as admin`
- Failure: `[AUTH] Authentication failed for ...`

---

### Test 3: Alert Generation

**Goal:** Verify alerts are generated with correct priorities

**Steps:**
1. Start server
2. Wait 30 seconds (or modify `server.py` to reduce interval for testing)
3. Check console output

**Expected:**
- ✅ Alert generated every 30 seconds
- ✅ Priority assigned (LOW/MEDIUM/HIGH)
- ✅ Log shows: `[ALERT] Generated HIGH priority alert: ...`

**To test different priorities:**
Edit `weather_api.py` temporarily:
```python
def get_current_weather():
    # Force HIGH priority
    return {
        "temperature": 35,  # > 30
        "humidity": 85,     # > 80
        "condition": "Hot",
        "timestamp": "..."
    }
```

---

### Test 4: Broadcasting to Multiple Clients

**Goal:** Verify alerts reach all connected clients

**Steps:**
1. Start server
2. Open 3 terminal windows
3. Run client in each: `python client.py`
4. Authenticate all 3 clients
5. Wait for alert (30 seconds)

**Expected:**
- ✅ All 3 clients receive the same alert
- ✅ Server log shows 3 BROADCAST entries:
  ```
  [BROADCAST] Alert sent to admin (...)
  [BROADCAST] Alert sent to user1 (...)
  [BROADCAST] Alert sent to user2 (...)
  ```

---

### Test 5: Acknowledgment System

**Goal:** Verify clients send ACK and server receives them

**Steps:**
1. Start server and client
2. Wait for alert
3. Client automatically sends ACK
4. Check server logs

**Expected:**
- ✅ Client displays alert
- ✅ Client sends ACK (automatic)
- ✅ Server log shows: `[ACK] Received ACK from admin for alert 1234567890`

**Check `server_log.txt`:**
```
[12:00:30] [ALERT] Generated HIGH priority alert: ...
[12:00:30] [BROADCAST] Alert sent to admin (...)
[12:00:31] [ACK] Received ACK from admin for alert 1234567890
```

---

### Test 6: Logging System

**Goal:** Verify all events are logged

**Steps:**
1. Start server
2. Connect client
3. Wait for alert
4. Check `server_log.txt` file

**Expected file contents:**
```
[2024-01-01 12:00:00] [SERVER] Server started on 127.0.0.1:8888
[2024-01-01 12:00:05] [CONNECTION] New connection from ('127.0.0.1', 54321)
[2024-01-01 12:00:06] [AUTH] Client ('127.0.0.1', 54321) authenticated as admin
[2024-01-01 12:00:30] [ALERT] Generated HIGH priority alert: ...
[2024-01-01 12:00:30] [BROADCAST] Alert sent to admin (...)
[2024-01-01 12:00:31] [ACK] Received ACK from admin for alert 1234567890
```

---

### Test 7: Graceful Shutdown

**Goal:** Verify server shuts down cleanly

**Steps:**
1. Start server with 2 clients connected
2. Press `Ctrl+C` on server
3. Check client terminals

**Expected:**
- ✅ Server sends "SERVER_SHUTDOWN" to all clients
- ✅ Clients disconnect gracefully
- ✅ Server log shows: `[SERVER] Server shutdown complete`
- ✅ No errors or crashes

---

### Test 8: Encryption/Decryption

**Goal:** Verify messages are encrypted

**Steps:**
1. Start server (note encryption key)
2. Set correct key in client.py
3. Connect - should work
4. Set wrong key in client.py
5. Try connecting - should fail

**Expected:**
- ✅ Correct key: Connection works, messages encrypted/decrypted
- ❌ Wrong key: Decryption errors, connection fails

**To see encrypted data:**
You can add print statements in `modules/encryption.py`:
```python
def encrypt_message(message):
    encrypted = cipher.encrypt(message.encode())
    print(f"Original: {message}, Encrypted: {encrypted}")  # Debug
    return encrypted
```

---

### Test 9: Multiple Simultaneous Connections

**Goal:** Verify server handles multiple clients at once

**Steps:**
1. Start server
2. Connect 5 clients simultaneously (5 terminals)
3. All authenticate
4. Wait for alert

**Expected:**
- ✅ All 5 clients connect successfully
- ✅ All authenticate
- ✅ All receive alerts simultaneously
- ✅ Server handles all without issues

---

### Test 10: Client Disconnection Handling

**Goal:** Verify server handles client disconnections

**Steps:**
1. Start server
2. Connect 2 clients
3. Close one client (Ctrl+C)
4. Wait for next alert

**Expected:**
- ✅ Server detects disconnected client
- ✅ Removes from active list
- ✅ Next alert only goes to remaining client
- ✅ Log shows: `[DISCONNECT] Removed disconnected client: ...`

---

## 📝 How Each Component Works Together

### Complete Flow Diagram:

```
1. Server Starts
   └─> Module 1: Creates socket, binds to port, starts listening
   └─> Module 3: Generates encryption key
   └─> Module 7: Logs "Server started"

2. Client Connects
   └─> Module 1: Accepts connection, creates thread
   └─> Module 2: Authenticates client (username/password)
   └─> Module 3: All messages encrypted/decrypted
   └─> Module 7: Logs connection and auth

3. Alert Generation (every 30 seconds)
   └─> Module 4: Generates alert based on weather
   └─> Module 7: Logs alert generation
   └─> Module 5: Broadcasts to all clients
   └─> Module 3: Encrypts alert messages
   └─> Module 7: Logs each broadcast

4. Client Receives Alert
   └─> Client decrypts message
   └─> Client displays alert
   └─> Client sends ACK

5. Server Receives ACK
   └─> Module 6: Handles acknowledgment
   └─> Module 7: Logs ACK received

6. Server Shutdown
   └─> Module 8: Sends shutdown to all clients
   └─> Module 8: Closes all connections
   └─> Module 7: Logs shutdown
```

---

## 🔧 Customization Guide

### Change Alert Interval

Edit `server.py`:
```python
def alert_generator():
    while server_running:
        time.sleep(10)  # Change from 30 to 10 seconds
```

### Add More Users

Edit `modules/authentication.py`:
```python
USERS = {
    "admin": "admin123",
    "user1": "pass123",
    "user2": "pass456",
    "yourname": "yourpass"  # Add here
}
```

### Change Priority Logic

Edit `modules/alert_generator.py`:
```python
# Custom priority rules
if weather["temperature"] > 35:  # Change threshold
    priority = "HIGH"
elif weather["temperature"] > 28:
    priority = "MEDIUM"
else:
    priority = "LOW"
```

### Use Real Weather API

Edit `weather_api.py`:
```python
import requests

def get_current_weather():
    API_KEY = "your_openweathermap_api_key"
    CITY = "Karachi"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    
    response = requests.get(url)
    data = response.json()
    return {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["main"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
```

Then add to `requirements.txt`:
```
requests
```

---

## 🐛 Troubleshooting

### Problem: "Connection refused"
**Solution:** Make sure server is running first

### Problem: "Encryption error" or "Decryption failed"
**Solution:** 
- Check encryption key in client.py matches server key
- Make sure key is in bytes format: `ENCRYPTION_KEY = b'your_key'`

### Problem: "Authentication failed" even with correct password
**Solution:**
- Check username/password in `modules/authentication.py` USERS dictionary
- Make sure no extra spaces in input

### Problem: No alerts received
**Solution:**
- Wait 30 seconds (alerts generated every 30 seconds)
- Check server logs for alert generation
- Make sure client is authenticated

### Problem: Module import errors
**Solution:**
- Make sure you're running from project root directory
- Check that `modules/` folder exists with all files
- Verify `modules/__init__.py` exists

---

## 📊 Understanding the Code Structure

### Why Modular Design?

1. **Easy to Understand:** Each file does one thing
2. **Easy to Modify:** Change one module without affecting others
3. **Easy to Test:** Test each module independently
4. **Easy to Explain:** Show your sir each module separately

### Module Dependencies:

```
server.py
  └─> Uses all 8 modules

modules/server_connection.py
  └─> Uses: logger, authentication, acknowledgment

modules/authentication.py
  └─> Uses: logger, message_handler

modules/encryption.py
  └─> Uses: logger

modules/alert_generator.py
  └─> Uses: logger, weather_api

modules/broadcaster.py
  └─> Uses: logger, message_handler

modules/acknowledgment.py
  └─> Uses: logger, message_handler

modules/logger.py
  └─> No dependencies (base module)

modules/shutdown.py
  └─> Uses: logger, message_handler

modules/message_handler.py
  └─> Uses: encryption, logger
```

---

## 🎓 For Your Presentation

### What to Explain:

1. **Module 1:** "This handles server setup and accepts connections"
2. **Module 2:** "This verifies users before allowing access"
3. **Module 3:** "This encrypts all data for security"
4. **Module 4:** "This creates alerts based on weather conditions"
5. **Module 5:** "This sends alerts to all connected clients"
6. **Module 6:** "This receives confirmations from clients"
7. **Module 7:** "This records all events for monitoring"
8. **Module 8:** "This ensures clean shutdown without errors"

### Demo Flow:

1. Start server → Show Module 1 working
2. Connect client → Show Module 2 (authentication)
3. Wait for alert → Show Modules 4, 5, 6 (generation, broadcast, ACK)
4. Show logs → Show Module 7
5. Shutdown → Show Module 8

---

## ✅ Checklist Before Submission

- [ ] All 8 modules created and working
- [ ] Server starts without errors
- [ ] Client connects and authenticates
- [ ] Alerts are generated and broadcast
- [ ] ACKs are received and logged
- [ ] Logs are written to file
- [ ] Server shuts down gracefully
- [ ] Code is well-commented
- [ ] README is complete

---

## 📞 Support

If you face any issues:
1. Check `server_log.txt` for error messages
2. Verify all modules are in `modules/` folder
3. Make sure encryption key is set correctly
4. Check Python version (3.7+ required)

---

**Good luck with your CCN project! 🚀**
