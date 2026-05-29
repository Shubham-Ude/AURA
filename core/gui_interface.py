from PyQt5.QtCore import QObject, pyqtSignal

class GUIInterface(QObject):
    user_text_signal = pyqtSignal(str)
    aura_text_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.gui_window = None  # Will be linked later

    def connect(self, gui_window):
        self.gui_window = gui_window
        self.user_text_signal.connect(gui_window.display_user_text)
        self.aura_text_signal.connect(gui_window.display_aura_text)

    def display_user_text(self, text):
        self.user_text_signal.emit(text)

    def display_aura_text(self, text):
        self.aura_text_signal.emit(text)

# Global instance
gui_interface = GUIInterface()
