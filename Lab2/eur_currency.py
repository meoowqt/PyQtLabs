from PyQt5.QtCore import QObject, pyqtSignal


class EURCurrency(QObject):
    valueChanged = pyqtSignal(float)

    def __init__(self):
        super().__init__()