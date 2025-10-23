from PyQt5.QtWidgets import QLineEdit, QLabel, QHBoxLayout, QWidget
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt, pyqtSignal


class CurrencyField(QWidget):
    valueChanged = pyqtSignal(float)

    def __init__(self, currency_code):
        super().__init__()
        self.currency_code = currency_code
        self.validator = QDoubleValidator(-1e12, 1e12, 8, self)
        self.validator.setNotation(QDoubleValidator.StandardNotation)
        
        self.layout = QHBoxLayout()
        self.label = QLabel(currency_code)
        self.input = QLineEdit()
        self.input.setValidator(self.validator)
        self.input.setPlaceholderText("0.00")
        self.input.setAlignment(Qt.AlignRight)
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input)
        self.setLayout(self.layout)
        
        self.input.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text):
        if text.strip():
            try:
                value = float(text)
                self.valueChanged.emit(value)
            except ValueError:
                pass

    def set_value(self, value):
        self.input.blockSignals(True)
        self.input.setText(f"{value:.2f}")
        self.input.blockSignals(False)

    def get_value(self):
        """Возвращает текущее значение поля"""
        text = self.input.text().strip()
        if text:
            try:
                return float(text)
            except ValueError:
                return 0.0
        return 0.0

    def clear(self):
        self.input.blockSignals(True)
        self.input.clear()
        self.input.blockSignals(False)