from PyQt6.QtCore import Qt, QThreadPool, QRunnable, pyqtSignal, pyqtSlot, QObject, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QHBoxLayout, QPushButton, QDialog
from PyQt6.QtGui import QIcon
from src.log_watcher import LogWatcher
from src.stats_fetcher import StatsFetcher
import re

class BedwarsOverlay(QWidget):
    def __init__(self, api_key):
        super().__init__()

        self.setWindowTitle("Bedwars Overlay v1.0")
        
        self.own_player_name = "YOUR_OWN_NAME_HERE"

        self.stats_fetcher = StatsFetcher()
        self.stats_fetcher.update_api_key(api_key)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        settings_button = QPushButton()
        settings_button.setIcon(QIcon("cogwheel.png"))
        settings_button.setIconSize(QSize(24, 24))
        settings_button.setFixedSize(32, 32)
        settings_button.setStyleSheet("background-color: #292929; color: white;")
        settings_button.clicked.connect(self.open_settings)

        
        top_layout = QHBoxLayout()
        top_layout.addWidget(settings_button, alignment=Qt.AlignmentFlag.AlignLeft)

        self.layout.addLayout(top_layout)
        self.layout.addSpacing(5)


        self.labels = ["Username", "FKs", "FDs", "FKDR", "Wins", "W/L", "Beds Broken"]

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.labels))
        self.table.setHorizontalHeaderLabels(self.labels)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)        
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("background-color: #292929; color: white;")
        self.layout.addWidget(self.table)

        self.log_watcher = LogWatcher()
        self.log_watcher.new_player_signal.connect(self.update_table)
        self.log_watcher.start()

        self.thread_pool = QThreadPool()

        self.players_in_table = []

        self.settings_window = SettingsWindow(api_key)

    def open_settings(self):
        self.settings_window.show()

    def update_api_key(self, new_api_key):
        print(f"Updating API key to {new_api_key}")
        self.stats_fetcher.update_api_key(new_api_key)

    def update_table(self, log_line):
        join_pattern = r'\[info\]  \[\d{2}:\d{2}:\d{2}\] \[Client thread/INFO\]: \[CHAT\] ([\w]+) has joined \(.*\)'
        join_match = re.search(join_pattern, log_line)
        
        quit_pattern = r'\[info\]  \[\d{2}:\d{2}:\d{2}\] \[Client thread/INFO\]: \[CHAT\] ([\w]+) has quit!'
        quit_match = re.search(quit_pattern, log_line)

        who_pattern = r'\[info\]  \[\d{2}:\d{2}:\d{2}\] \[Client thread/INFO\]: \[CHAT\] ONLINE: ((?:[\w]+, )+[\w]+)'
        who_match = re.search(who_pattern, log_line)

        if join_match:
            player_name = join_match.group(1)
            
            if player_name == self.own_player_name:
                print("Resetting table...")
                self.table.setRowCount(0)  # Remove all rows
                self.players_in_table = []  # Reset list
                return
            
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

    @pyqtSlot(int, list)
    def display_stats(self, row_position, stats):
        for i, stat in enumerate(stats):
            if i == 0:
                item = QTableWidgetItem(str(stat))
            else:
                item = NumericTableWidgetItem(str(stat))

            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.table.setItem(row_position, i, item)


class SettingsWindow(QDialog):
    def __init__(self, api_key):
        super().__init__()

        self.setWindowTitle("Settings")
        self.setFixedWidth(350)
        self.setFixedHeight(50)

        layout = QVBoxLayout()

        api_label = QLabel("API Key:")
        self.api_input = QLineEdit()
        self.api_input.setText(api_key)
        self.api_input.textChanged.connect(self.update_api_key)

        api_layout = QHBoxLayout()
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_input)

        layout.addLayout(api_layout)
        self.setLayout(layout)

    def update_api_key(self, new_api_key):
        print(f"Updating API key to {new_api_key}")


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
