# 📱 Terminal-Ai Termux Setup Guide

This guide provides explicit instructions for duplicating the working setup for Terminal-Ai on Android using Termux, including the specific fixes required for Python 3.13 and native dependency builds.

## 🛠️ Prerequisites & System Fixes

If you encounter errors building wheels for `pydantic-core` or `maturin` due to missing Android API levels, run the following:

```bash
# Install build essentials
pkg install rust clang cmake ninja

# Export the required API level for the Rust compiler
export ANDROID_API_LEVEL=24
```

## 📦 Backend Setup

The backend requires Pydantic v2 to be compatible with Python 3.13 (to avoid `recursive_guard` errors).

```bash
cd ~/Terminal-Ai/backend

# Clean up any existing installations
pip uninstall pydantic fastapi -y

# Install the working stack
pip install fastapi uvicorn pydantic python-dotenv httpx
```

### Running the Backend
Run the server bound to all interfaces so the UI can connect:

```bash
cd ~/Terminal-Ai/backend
uvicorn server:app --host 0.0.0.0 --port 8000
```

## 🌐 Frontend Setup (Expo Web)

The frontend is an Expo project. Due to Termux/network restrictions, use local host mode instead of the ngrok tunnel.

```bash
cd ~/Terminal-Ai/frontend

# Install dependencies
npm install

# Point to the backend and start the web server
EXPO_PUBLIC_BACKEND_URL=http://127.0.0.1:8000 npx expo start --web --host 0.0.0.0
```

## 🚀 Accessing the UI

1. **On the same device:** Open `http://127.0.0.1:19006` in your browser.
2. **From any device on the same network:** Use the Pixel's LAN IP (e.g., `http://192.168.x.x:19006`).
   - Find your IP in Termux with: `ip addr show wlan0 | grep 'inet '`
