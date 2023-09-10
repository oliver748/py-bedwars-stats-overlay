from PyQt6.QtWidgets import QApplication
from src.bedwars_overlay import BedwarsOverlay

if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")
    window = BedwarsOverlay(api_key="YOUR_API_KEY_HERE")
    window.resize(800, 400)
    window.show()
    app.exec()
