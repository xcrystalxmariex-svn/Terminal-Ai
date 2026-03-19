# TermuxAI - AI-Powered Terminal Environment

## Product Overview
TermuxAI is a mobile-first coding and development environment powered by an AI agent. It provides a full Linux terminal (Termux-like) alongside an AI assistant that can see terminal activity, execute commands, and help with coding tasks.

## Core Features

### 1. First-Run Onboarding Wizard
- **Theme Selection**: 3 dark themes (Cyberpunk Void, Monokai Pro, Dracula)
- **AI Provider Config**: Support for OpenAI, Anthropic, Google Gemini, OpenAI-compatible endpoints, and Generic HTTP
- **Agent Customization**: Custom agent name and system prompt

### 2. Terminal Tab
- Full xterm.js terminal emulator connected to a real Linux PTY via WebSocket
- Special keys toolbar (ESC, TAB, CTRL, arrows) for mobile keyboard limitations
- CTRL shortcut panel (C, D, Z, L, A, E) for common terminal operations
- Shared terminal session between user and AI agent

### 3. AI Agent Tab
- Chat interface with conversational AI powered by user's configured provider
- Terminal context awareness - AI sees recent terminal output
- Code block parsing with "Run" buttons to execute commands in terminal
- Auto-execute mode option for hands-free terminal automation
- Chat history persistence in MongoDB

### 4. Settings Tab
- Live theme switching
- AI provider reconfiguration
- Agent name and system prompt editing
- Auto-execute toggle
- API key management (secured, shows "saved" indicator)

## Architecture
- **Backend**: FastAPI with WebSocket support, PTY terminal management, AI provider proxy
- **Frontend**: Expo (React Native) with expo-router tabs, WebView/iframe xterm.js
- **Database**: MongoDB for config, chat history
- **Terminal**: Real Linux PTY shared via WebSocket to multiple clients

## AI Providers Supported
| Provider | Endpoint | Model Examples |
|----------|----------|----------------|
| OpenAI | api.openai.com/v1/chat/completions | gpt-4o, gpt-4-turbo |
| Anthropic | api.anthropic.com/v1/messages | claude-sonnet-4-20250514 |
| Google Gemini | generativelanguage.googleapis.com/v1beta | gemini-2.0-flash |
| OpenAI Compatible | Custom | Any OpenAI-format API |
| Generic HTTP | Custom | Any REST API |

## Tech Stack
- Expo SDK 54, React Native, TypeScript
- FastAPI, Python, Motor (async MongoDB)
- xterm.js 5.3.0 with WebSocket PTY bridge
- MongoDB for persistence
