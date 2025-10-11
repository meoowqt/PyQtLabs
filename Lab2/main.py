#!/usr/bin/env python3
# currency_converter_pyqt5.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QLabel, QGridLayout, QVBoxLayout, QGroupBox
)
from PyQt5.QtGui import QDoubleValidator, QFont
from PyQt5.QtCore import Qt


class CurrencyConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Конвертер валют (USD / EUR / RUB)")
        self.setMinimumWidth(380)

        # --- Курсы ---
        self.rates = {
            "USD": {"EUR": 1/1.16, "RUB": 81.27},
            "EUR": {"USD": 1.16, "RUB": 93.90},
            "RUB": {"USD": 1/81.27, "EUR": 1/93.90},
        }

        self.updating = False

        # --- Поля ввода ---
        self.input_usd = QLineEdit()
        self.input_eur = QLineEdit()
        self.input_rub = QLineEdit()

        validator = QDoubleValidator(-1e12, 1e12, 8, self)
        validator.setNotation(QDoubleValidator.StandardNotation)
        for le in (self.input_usd, self.input_eur, self.input_rub):
            le.setValidator(validator)
            le.setPlaceholderText("0.00")
            le.setAlignment(Qt.AlignRight)

        # --- Лейблы ---
        self.label_usd = QLabel("USD")
        self.label_eur = QLabel("EUR")
        self.label_rub = QLabel("RUB")

        # --- Информационный лейбл с курсами ---
        self.info_label = QLabel(self._rates_text())
        self.info_label.setWordWrap(True)
        self.info_label.setFont(QFont("Consolas", 10))
        self.info_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # --- Сигналы ---
        self.input_usd.textChanged.connect(lambda text: self.on_text_changed("USD", text))
        self.input_eur.textChanged.connect(lambda text: self.on_text_changed("EUR", text))
        self.input_rub.textChanged.connect(lambda text: self.on_text_changed("RUB", text))

        # --- Компоновка ---
        grid = QGridLayout()
        grid.addWidget(self.label_usd, 0, 0)
        grid.addWidget(self.input_usd, 0, 1)
        grid.addWidget(self.label_eur, 1, 0)
        grid.addWidget(self.input_eur, 1, 1)
        grid.addWidget(self.label_rub, 2, 0)
        grid.addWidget(self.input_rub, 2, 1)

        box = QGroupBox("Конвертация")
        box.setLayout(grid)

        v = QVBoxLayout()
        v.addWidget(box)
        v.addWidget(QLabel("Курсы:"))
        v.addWidget(self.info_label)
        v.addStretch()
        self.setLayout(v)

        self.input_usd.setText("1.00")

    def _rates_text(self) -> str:
        """Возвращает текст с курсами построчно."""
        lines = []
        for c_from, mapping in self.rates.items():
            for c_to, val in mapping.items():
                lines.append(f"   1 {c_from} = {val:.6f} {c_to}")
            lines.append("") 
        return "\n".join(lines)

    def on_text_changed(self, currency_from: str, text: str):
        if self.updating:
            return

        if text.strip() == "":
            try:
                self.updating = True
                if currency_from != "USD":
                    self.input_usd.blockSignals(True); self.input_usd.clear(); self.input_usd.blockSignals(False)
                if currency_from != "EUR":
                    self.input_eur.blockSignals(True); self.input_eur.clear(); self.input_eur.blockSignals(False)
                if currency_from != "RUB":
                    self.input_rub.blockSignals(True); self.input_rub.clear(); self.input_rub.blockSignals(False)
            finally:
                self.updating = False
            return

        try:
            value = float(text)
        except ValueError:
            return

        try:
            self.updating = True
            if currency_from == "USD":
                eur_val = self._convert("USD", "EUR", value)
                rub_val = self._convert("USD", "RUB", value)
                self.input_eur.blockSignals(True); self.input_eur.setText(f"{eur_val:.2f}"); self.input_eur.blockSignals(False)
                self.input_rub.blockSignals(True); self.input_rub.setText(f"{rub_val:.2f}"); self.input_rub.blockSignals(False)

            elif currency_from == "EUR":
                usd_val = self._convert("EUR", "USD", value)
                rub_val = self._convert("EUR", "RUB", value)
                self.input_usd.blockSignals(True); self.input_usd.setText(f"{usd_val:.2f}"); self.input_usd.blockSignals(False)
                self.input_rub.blockSignals(True); self.input_rub.setText(f"{rub_val:.2f}"); self.input_rub.blockSignals(False)

            elif currency_from == "RUB":
                usd_val = self._convert("RUB", "USD", value)
                eur_val = self._convert("RUB", "EUR", value)
                self.input_usd.blockSignals(True); self.input_usd.setText(f"{usd_val:.2f}"); self.input_usd.blockSignals(False)
                self.input_eur.blockSignals(True); self.input_eur.setText(f"{eur_val:.2f}"); self.input_eur.blockSignals(False)
        finally:
            self.updating = False

    def _convert(self, frm: str, to: str, amount: float) -> float:
        if frm == to:
            return amount
        try:
            rate = self.rates[frm][to]
            return amount * rate
        except KeyError:
            for mid in self.rates.get(frm, {}):
                if to in self.rates.get(mid, {}):
                    return amount * self.rates[frm][mid] * self.rates[mid][to]
            return 0.0


def main():
    app = QApplication(sys.argv)
    w = CurrencyConverter()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
