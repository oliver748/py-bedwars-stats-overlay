from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QDialog, QCheckBox, QSpacerItem, QSizePolicy

class SettingsWindow(QDialog):
    player_name_changed_signal = pyqtSignal(str)  # new line
    show_own_name_checkbox_signal = pyqtSignal(int)  # new line

    def __init__(self, api_key, log_watcher):
        super().__init__()

        self.setFixedHeight(75)
        self.setFixedWidth(950)

        self.log_watcher = log_watcher

        self.setWindowTitle("Settings")

        main_layout = QHBoxLayout()

        # Left layout
        left_outer_layout = QVBoxLayout()
        left_layout = QVBoxLayout()

        api_label = QLabel("API Key:  ")
        self.api_input = QLineEdit()
        self.api_input.setText(api_key)
        self.api_input.textChanged.connect(self.update_api_key)

        api_layout = QHBoxLayout()
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_input)

        log_file_label = QLabel("Log Path:")
        self.log_file_input = QLineEdit()
        self.log_file_input.setText("/home/admin/.minecraft/logs/latest.log")
        self.log_file_input.textChanged.connect(self.update_log_file_path)

        log_file_layout = QHBoxLayout()
        log_file_layout.addWidget(log_file_label)
        log_file_layout.addWidget(self.log_file_input)

        left_layout.addLayout(api_layout)
        left_layout.addLayout(log_file_layout)

        left_outer_layout.addLayout(left_layout)
        left_outer_layout.addStretch()

        # Right layout
        right_outer_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        player_name_label = QLabel("Your own player name:   ")
        self.player_name_input = QLineEdit()
        self.player_name_input.setText("")

        self.player_name_input.textChanged.connect(self.update_player_name)  # new line
        
        player_name_layout = QHBoxLayout()
        player_name_layout.addWidget(player_name_label)
        player_name_layout.addWidget(self.player_name_input)

        self.show_own_name_label = QLabel("Show own name in table:")
        self.show_own_name_checkbox = QCheckBox()

        # set fixed size
        self.show_own_name_checkbox.setChecked(True)
        self.show_own_name_checkbox.setStyleSheet(
            """
            QCheckBox {
                width: 20px;
                height: 25px;
                background: gray;
                border-radius: 12px;
            }
            QCheckBox::indicator {
                width: 25px;
                height: 25px;
                background: #4d4d4d; 
                border-radius: 12px;
            }
            QCheckBox::indicator:checked {
                margin-left: 25px;
                background: white;
            }
            """
        )
        self.show_own_name_checkbox.setFixedSize(50, 25)

        self.show_own_name_checkbox.stateChanged.connect(self.update_show_own_name)

        show_own_name_layout = QHBoxLayout()
        show_own_name_layout.addWidget(self.show_own_name_label, alignment=Qt.AlignmentFlag.AlignLeft)
        show_own_name_layout.addWidget(self.show_own_name_checkbox, alignment=Qt.AlignmentFlag.AlignLeft)

        show_own_name_layout.addStretch(1)  # Stretch to occupy any extra space
                
        right_layout.addLayout(player_name_layout)
        

        right_layout.addLayout(show_own_name_layout)
        right_layout.addStretch()

        right_outer_layout.addLayout(right_layout)
        right_outer_layout.addStretch()

        # Adding some space in the middle
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        # Combine both layouts into the main layout
        main_layout.addLayout(left_outer_layout)
        main_layout.addItem(spacer)
        main_layout.addLayout(right_outer_layout)

        self.setLayout(main_layout)

    def update_show_own_name(self, state):
        self.show_own_name_checkbox_signal.emit(state)

    def update_player_name(self, new_player_name):
        self.player_name_changed_signal.emit(new_player_name)

    def update_api_key(self, new_api_key):
        print(f"Updating API key to {new_api_key}")

    def update_log_file_path(self, new_log_file_path):
        self.log_watcher.update_log_file_path(new_log_file_path)
        self.log_watcher.restart()
