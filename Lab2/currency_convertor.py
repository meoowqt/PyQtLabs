import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGroupBox, QLabel, 
    QPushButton, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from currency_field import CurrencyField
from currency_rates import CurrencyRates
from usd_currency import USDCurrency
from eur_currency import EURCurrency
from rub_currency import RUBCurrency


class CurrencyConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Конвертер валют (USD / EUR / RUB)")
        self.setMinimumWidth(420)

        # Инициализация менеджера курсов
        self.rates = CurrencyRates()
        self.updating = False

        # Инициализация валютных классов
        self.usd = USDCurrency()
        self.eur = EURCurrency()
        self.rub = RUBCurrency()

        self.init_ui()
        self.connect_signals()

        # Установка начального значения
        self.usd_field.set_value(1.00)

    def init_ui(self):
        # Создание полей ввода
        self.usd_field = CurrencyField("USD")
        self.eur_field = CurrencyField("EUR")
        self.rub_field = CurrencyField("RUB")

        # Кнопка обновления курсов
        self.update_button = QPushButton("Обновить курсы с ЦБ РФ")
        self.update_button.setMinimumHeight(35)

        # Информационный лейбл
        self.info_label = QLabel(self.rates.get_rates_text())
        self.info_label.setWordWrap(True)
        self.info_label.setFont(QFont("Consolas", 9))
        self.info_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Лейбл времени обновления
        self.update_time_label = QLabel(f"Обновлено: {self.rates.get_last_updated()}")
        self.update_time_label.setFont(QFont("Arial", 8))
        self.update_time_label.setAlignment(Qt.AlignRight)

        # Компоновка
        currencies_layout = QVBoxLayout()
        currencies_layout.addWidget(self.usd_field)
        currencies_layout.addWidget(self.eur_field)
        currencies_layout.addWidget(self.rub_field)

        box = QGroupBox("Конвертация")
        box.setLayout(currencies_layout)

        # Layout для времени обновления
        time_layout = QHBoxLayout()
        time_layout.addStretch()
        time_layout.addWidget(self.update_time_label)

        main_layout = QVBoxLayout()
        main_layout.addWidget(box)
        main_layout.addWidget(self.update_button)
        main_layout.addWidget(QLabel("Текущие курсы:"))
        main_layout.addWidget(self.info_label)
        main_layout.addLayout(time_layout)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def connect_signals(self):
        # Подключение сигналов от полей ввода к валютам
        self.usd_field.valueChanged.connect(self.usd.valueChanged.emit)
        self.eur_field.valueChanged.connect(self.eur.valueChanged.emit)
        self.rub_field.valueChanged.connect(self.rub.valueChanged.emit)

        # Подключение сигналов валют к обработчикам
        self.usd.valueChanged.connect(lambda v: self.convert_from("USD", v))
        self.eur.valueChanged.connect(lambda v: self.convert_from("EUR", v))
        self.rub.valueChanged.connect(lambda v: self.convert_from("RUB", v))

        # Подключение кнопки обновления курсов
        self.update_button.clicked.connect(self.rates.update_rates)
        
        # Подключение сигналов обновления курсов
        self.rates.rates_updated.connect(self.on_rates_updated)
        self.rates.rates_error.connect(self.on_rates_error)

    def convert_from(self, from_currency, value):
        if self.updating:
            return

        self.updating = True

        try:
            if from_currency == "USD":
                self.eur_field.set_value(self.rates.convert("USD", "EUR", value))
                self.rub_field.set_value(self.rates.convert("USD", "RUB", value))
            elif from_currency == "EUR":
                self.usd_field.set_value(self.rates.convert("EUR", "USD", value))
                self.rub_field.set_value(self.rates.convert("EUR", "RUB", value))
            elif from_currency == "RUB":
                self.usd_field.set_value(self.rates.convert("RUB", "USD", value))
                self.eur_field.set_value(self.rates.convert("RUB", "EUR", value))
        finally:
            self.updating = False

    def on_rates_updated(self):
        """Обновляет интерфейс при изменении курсов"""
        self.info_label.setText(self.rates.get_rates_text())
        self.update_time_label.setText(f"Обновлено: {self.rates.get_last_updated()}")
        
        # Пересчитываем текущие значения
        current_usd = self.usd_field.get_value()
        if current_usd != 0:
            self.usd_field.set_value(current_usd)

    def on_rates_error(self, error_message):
        """Показывает сообщение об ошибке"""
        QMessageBox.warning(self, "Ошибка обновления курсов", error_message)


def main():
    app = QApplication(sys.argv)
    converter = CurrencyConverter()
    converter.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()