from PyQt5.QtCore import QObject, pyqtSignal


class RUBCurrency(QObject):
    valueChanged = pyqtSignal(float)

    def __init__(self):
        super().__init__()