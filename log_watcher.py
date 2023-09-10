from PyQt6.QtCore import QThread, pyqtSignal
import time

class LogWatcher(QThread):
    new_player_signal = pyqtSignal(str)

    def run(self):
        # log file is typically in C:/Users/PC_USERNAME/.lunarclient/logs/game/
        with open('POINT_TO_THE_LOG_FILE', 'r', errors='ignore') as f:
            f.seek(0, 2)  # Go to the end of the file
            while True:
                line = f.readline().strip()
                if line:
                    self.new_player_signal.emit(line)
                time.sleep(0.1)
