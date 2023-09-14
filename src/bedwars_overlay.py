from PyQt6.QtCore import Qt, QThreadPool, QRunnable, pyqtSignal, pyqtSlot, QObject, QSize
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QPushButton

from src.settings_window import SettingsWindow
from src.log_watcher import LogWatcher
from src.stats_fetcher import StatsFetcher
import re



class BedwarsOverlay(QWidget):
    BUTTON_STYLE = "background-color: #292929; color: white;"
    
    def __init__(self, api_key):
        super().__init__()

        self.setWindowTitle("Bedwars Overlay v1.0")
        self.own_player_name = ""

        self.show_own_name = True  # By default, show the own name in the table

        self.stats_fetcher = StatsFetcher()
        self.stats_fetcher.update_api_key(api_key)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setup_top_layout()
        self.setup_table()
        
        self.log_watcher = LogWatcher()
        self.log_watcher.new_player_signal.connect(self.update_table)
        self.log_watcher.start()

        self.thread_pool = QThreadPool()
        self.players_in_table = []

        self.settings_window = SettingsWindow(api_key, self.log_watcher)
        self.settings_window.player_name_changed_signal.connect(self.update_own_player_name)  # new line
        self.settings_window.show_own_name_checkbox_signal.connect(self.update_show_own_name)  # new line

        
    def setup_top_layout(self):
        settings_button = QPushButton()
        settings_button.setIcon(QIcon("cogwheel.png"))
        settings_button.setIconSize(QSize(24, 24))
        settings_button.setFixedSize(32, 32)
        settings_button.setStyleSheet(self.BUTTON_STYLE)
        settings_button.clicked.connect(self.open_settings)
        
        top_layout = QHBoxLayout()
        top_layout.addWidget(settings_button, alignment=Qt.AlignmentFlag.AlignLeft)

        self.layout.addLayout(top_layout)
        self.layout.addSpacing(5)

    def setup_table(self):
        labels = ["Username", "FKs", "FDs", "FKDR", "Wins", "W/L", "Beds Broken"]
        self.table = QTableWidget()
        self.table.setColumnCount(len(labels))
        self.table.setHorizontalHeaderLabels(labels)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet(self.BUTTON_STYLE)
        self.layout.addWidget(self.table)
    
    def open_settings(self):
        self.settings_window.show()

    def update_show_own_name(self, state):
        self.show_own_name = bool(state)

    def update_own_player_name(self, new_name):
        print(f"Updating own player name to {new_name}")
        self.own_player_name = new_name

    def update_api_key(self, new_api_key):
        print(f"Updating API key to {new_api_key}")
        self.stats_fetcher.update_api_key(new_api_key)

    def update_table(self, log_line):
        join_pattern = r'\[\d{2}:\d{2}:\d{2}\] \[.*? thread/INFO\]: \[CHAT\] ([\w]+) has joined( \(.*\))?'
        join_match = re.search(join_pattern, log_line)
        
        quit_pattern = r'\[\d{2}:\d{2}:\d{2}\] \[.*? thread/INFO\]: \[CHAT\] ([\w]+) has quit!'
        quit_match = re.search(quit_pattern, log_line)
        
        who_pattern = r'\[\d{2}:\d{2}:\d{2}\] \[.*? thread/INFO\]: \[CHAT\] ONLINE: ((?:[\w]+, )*[\w]+)'
        who_match = re.search(who_pattern, log_line)

        if join_match:
            player_name = join_match.group(1)
            
            if player_name == self.own_player_name:
                print("Resetting table...")
                self.table.setRowCount(0)  # Remove all rows
                self.players_in_table = []  # Reset list

            self.add_new_player(player_name)

        elif quit_match:
            player_name = quit_match.group(1)
            self.remove_player(player_name)

        elif who_match:
            player_names_str = who_match.group(1)
            player_names = player_names_str.split(", ")
            for player_name in player_names:
                self.add_new_player(player_name)

    def add_new_player(self, name):
        if name in self.players_in_table:
            return
        if name == self.own_player_name and not self.show_own_name:
            return
        
        print(f"Adding {name} to table")
        
        self.players_in_table.append(name)

        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        worker = Worker(self.stats_fetcher.get_stats, row_position, name)
        worker.signals.result.connect(self.display_stats)

        self.thread_pool.start(worker)

    def remove_player(self, name):
        if name not in self.players_in_table:
            return
        
        print(f"Removing {name} from table")

        self.players_in_table.remove(name)

        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == name:
                self.table.removeRow(row)
                break
    

    def find_color(self, fkdr):
        if fkdr == '?':
            return QColor("#FFFFFF")  # White
        elif fkdr <= 0.1:
            return QColor("#878787")
        elif fkdr <= 0.5:
            return QColor("#ADADAD")
        elif fkdr <= 1:
            return QColor("#FFC7BA")
        elif fkdr <= 2:
            return QColor("#FFA384")
        elif fkdr <= 3:
            return QColor("#FF7A4D")
        elif fkdr <= 4:
            return QColor("#FF5500")
        elif fkdr <= 5:
            return QColor("#E64D00")
        elif fkdr <= 6:
            return QColor("#CC4400")
        elif fkdr > 6:
            return QColor("#F07F65")

    @pyqtSlot(int, list)
    def display_stats(self, row_position, stats):
        for i, stat in enumerate(stats):
            print(i, stat)
            if i == 0:
                item = QTableWidgetItem(str(stat))
            else:
                item = NumericTableWidgetItem(str(stat))

            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

            self.table.setItem(row_position, i, item)
            if i == 3:
                self.table.item(row_position, i).setForeground(self.find_color(stat))


class WorkerSignals(QObject):
    result = pyqtSignal(int, list)

class Worker(QRunnable):
    def __init__(self, func, row_position, *args, **kwargs):
        super().__init__()

        self.func = func
        self.row_position = row_position
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        result = self.func(*self.args, **self.kwargs)
        if result is not None:
            self.signals.result.emit(self.row_position, result)
        else:
            print(f"Failed to fetch stats for row {self.row_position}")


class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            return float(self.text()) < float(other.text())
        except ValueError:
            return super().__lt__(other)
