# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install
```bash
pip install -r requirements.txt
```

### Step 2: Start Server
```bash
python server.py
```
**Copy the encryption key that appears!**

### Step 3: Start Client
1. Open `client.py`
2. Paste encryption key: `ENCRYPTION_KEY = b'paste_key_here'`
3. Run: `python client.py`
4. Login: `admin` / `admin123`

---

## 📁 Project Structure

```
server.py              → Main server (uses all modules)
client.py              → Client application
weather_api.py         → Weather data (modular)
modules/               → All 8 server modules
  ├── server_connection.py    # Module 1: Server setup
  ├── authentication.py      # Module 2: Login system
  ├── encryption.py           # Module 3: Security
  ├── alert_generator.py      # Module 4: Alert creation
  ├── broadcaster.py         # Module 5: Send to all
  ├── acknowledgment.py      # Module 6: ACK handling
  ├── logger.py               # Module 7: Logging
  ├── shutdown.py             # Module 8: Clean exit
  └── message_handler.py      # Shared: Message functions
```

---

## 🧪 Quick Tests

### Test Connection
1. Start server
2. Start client
3. Login with: `admin` / `admin123`
4. ✅ Should see "Welcome admin!"

### Test Alerts
1. Wait 30 seconds after login
2. ✅ Should receive alert
3. ✅ Client sends ACK automatically

### Test Multiple Clients
1. Start server
2. Open 3 terminals
3. Run client in each
4. ✅ All receive same alert

---

## 🔑 Default Users

- `admin` / `admin123`
- `user1` / `pass123`
- `user2` / `pass456`

---

## 📝 Key Files

- **README.md** - Complete documentation
- **server_log.txt** - All server events (auto-created)
- **modules/** - All 8 modular components

---

## ❓ Common Issues

**Connection refused?** → Start server first!

**Encryption error?** → Check key in client.py matches server

**No alerts?** → Wait 30 seconds, check server logs

---

For detailed information, see **README.md**

