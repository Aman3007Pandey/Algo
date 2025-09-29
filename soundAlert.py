import time
import os
import platform
from datetime import datetime, timedelta

LOG_PREFIX = "momentum_signals.log"
LOG_FILE = f"{datetime.now().strftime('%Y-%m-%d')}_{LOG_PREFIX}.log" # put today’s log file name here
# LOG_FILE="momentum_signals.log2"
def play_alert():
        print("reached here")
        os.system('afplay /System/Library/Sounds/Glass.aiff')  # macOS
        # or Linux: os.system('play -nq -t alsa synth 0.3 sine 1200')

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
