from PyQt6.QtCore import QThread, pyqtSignal
import time
import re

class LogWatcher(QThread):
    log_file_path = "/home/admin/.minecraft/logs/latest.log"
    new_player_signal = pyqtSignal(str)  # Emit type and player name

    def update_log_file_path(self, new_log_file_path):
        print(f"Updating log file path to {new_log_file_path}")
        self.log_file_path = new_log_file_path

    def restart(self):
        self.terminate()  # Stop the current thread
        self.start()  # Restart it

    def run(self):
        # if debug log is turned on it will show all lines
        DEBUG_LOG = True

        if not DEBUG_LOG:
            valid_line_pattern = re.compile(
                r'\[\d+:\d+:\d+\] \[Render thread/INFO\]: \[CHAT\] .*('
                'joined(?! the lobby)|'  # Match "joined" but not followed by " the lobby"
                'has quit|'
                'ONLINE: .+'
                ').*'
            )
        else:
            valid_line_pattern = re.compile(r".*")
        
        with open(self.log_file_path, 'r') as f:
            f.seek(0, 2)  # Go to the end of the file
            while True:
                line = f.readline().strip()
                if line and valid_line_pattern.match(line):
                    print(line)
                    self.new_player_signal.emit(line)
                
                time.sleep(0.01)
