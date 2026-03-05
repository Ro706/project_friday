# Friday AI Assistant

Friday is a modular, high-performance personal AI assistant built with Python. It features a decentralized architecture where specialized modules handle conversation, real-time data, system automation, and entertainment.

## 🚀 Features

### 🤖 Intelligent Chat & Real-time Search
- **Conversational AI**: Powered by Groq (Llama 3.3) for fast, natural interactions.
- **Real-time Information**: Integrated DuckDuckGo search for up-to-the-minute news, weather, and facts.
- **Decision Logic**: Uses a Cohere-powered Decision Making Model (DMM) to route queries to the correct specialized tool.

### 🛠️ System Automation
- **App Management**: Open and close any installed application or website.
- **System Control**: Volume adjustment, muting, and screenshots via `pyautogui` and `pycaw`.
- **Content Creation**: Generate emails, scripts, or research papers directly into Notepad.

### 🎨 Creativity & Utility
- **Image Generation**: High-quality 4K image generation using Stable Diffusion XL via Hugging Face.
- **System Diagnostics**: Real-time CPU and RAM usage reports.
- **Email Integration**: Send emails directly through SMTP.
- **Camera Access**: Built-in photo capture application.

### 🎮 Gaming
- **Tic Tac Toe**: Intelligent AI-driven board game with hint support.
- **Ultra Breakout**: Advanced arcade game with levels, power-ups, and particle effects.

## 🏗️ Project Structure

```text
C:\Users\rohit\Desktop\Friday\
├── main.py                 # Central orchestrator and entry point
├── backend/                # Core AI and logic modules
│   ├── Model.py            # Decision Making Model (DMM)
│   ├── Chatbot.py          # Conversational LLM (Groq)
│   ├── Automation.py       # System and web automation
│   ├── ImageGeneration.py  # SDXL Image generation
│   └── TextToSpeech.py     # Centralized voice output
├── core/                   # Utility and system info modules
│   ├── news.py             # Global news retrieval
│   ├── weather.py          # Real-time weather data
│   ├── cpu_info.py         # Processor diagnostics
│   └── mail.py             # SMTP Email client
├── game/                   # Interactive games
│   ├── game1.py            # Tic Tac Toe
│   └── game2.py            # Advanced Ultra Breakout
└── data/                   # Persistent logs and generated assets
```

## 🔄 System Flow

Friday operates on a **Research -> Strategy -> Execution** lifecycle:

1.  **Input**: The user provides a text command in the terminal.
2.  **Classification**: The `Model.py` (DMM) analyzes the intent (e.g., is this a general question or a request to play a game?).
3.  **Routing**: `main.py` routes the task to the appropriate module in `backend/`, `core/`, or `game/`.
4.  **Feedback**: Friday provides immediate verbal and textual feedback through the `TextToSpeech` engine.

## 🛠️ Setup & Requirements

1.  **Environment Variables**: Create a `.env` file in the root directory with the following keys:
    ```env
    GROQ_API_KEY=your_key_here
    COHERE_API_KEY=your_key_here
    HUGGINGFACE_API_KEY=your_key_here
    USERNAME=your_name
    EMAIL_PASSWORD=your_app_password
    NEWS_API=your_newsapi_org_key
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run Assistant**:
    ```bash
    python main.py
    ```

## ⚖️ License
This project is for educational and personal automation purposes.
