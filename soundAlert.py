import time
import os
import platform
import winsound
from datetime import datetime, timedelta

FOLDER_PATH="today_logs"
HISTORICAL_FOLDER_PATH="historical_logs"
LOG_PREFIX = "momentum_signals"
DYNAMIC_LOG_PREFIX="dynamic_signals"
VOLUME_LOG_PREFIX="volume_signals"
LOG_FILE = f"{FOLDER_PATH}/{datetime.now().strftime('%Y-%m-%d')}_{VOLUME_LOG_PREFIX}.log" # put today’s log file 
print(LOG_FILE) 

# LOG_FILE="2025-10-10_dynamic_signals.log"
# LOG_FILE="momentum_signals.log2"
# def play_alert():
#         print("reached here")
#         os.system('afplay /System/Library/Sounds/Glass.aiff')  # macOS
        # or Linux: os.system('play -nq -t alsa synth 0.3 sine 1200')
def play_alert():
    # Play a simple system beep
    # winsound.MessageBeep()
    # winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
    base_dir = os.path.dirname(__file__)
    sound_path = os.path.join(base_dir, "sound", "my_alert.wav")
    # Play the sound once (non-blocking)
    winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)        

def watch_log():
    with open(LOG_FILE, "r") as f:
        # Move cursor to end of file so we only react to *new* lines
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if line:
                print("ALERT:", line.strip())  # optional print
                play_alert()
            else:
                time.sleep(2)  # wait before checking again

if __name__ == "__main__":
    watch_log()
