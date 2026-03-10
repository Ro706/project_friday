import threading
import time
import winsound
from backend.TextToSpeech import speak

def reminder_thread(delay, message):
    """Wait for the specified time and then alert the user."""
    time.sleep(delay)
    print(f"\n[Reminder Alert]: {message}")
    
    # Play a notification sound (Frequency: 1000Hz, Duration: 500ms)
    winsound.Beep(1000, 500)
    winsound.Beep(1200, 500)
    
    speak(f"Reminder: {message}")

def set_reminder(time_str, message):
    """
    Parses time (e.g., '5 minutes', '1 hour') and starts a background thread.
    Returns a status message.
    """
    try:
        parts = time_str.split()
        amount = int(parts[0])
        unit = parts[1].lower()

        if "minute" in unit:
            delay = amount * 60
        elif "hour" in unit:
            delay = amount * 3600
        elif "second" in unit:
            delay = amount
        else:
            return "Unknown time unit. Please use seconds, minutes, or hours."

        thread = threading.Thread(target=reminder_thread, args=(delay, message), daemon=True)
        thread.start()
        return f"Done! I'll remind you to {message} in {amount} {unit}."
    except Exception as e:
        return f"Failed to set reminder: {e}"
