import json
import os
import requests
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
from bs4 import BeautifulSoup


class RateFetcher(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.rates = {}

    def run(self):
        try:
            # Получаем курсы с сайта ЦБ РФ
            url = "https://www.cbr.ru/currency_base/daily/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ищем таблицу с курсами валют
            table = soup.find('table', {'class': 'data'})
            if not table:
                self.error.emit("Не удалось найти таблицу с курсами")
                return

            rates = {}
            for row in table.find_all('tr')[1:]:  # Пропускаем заголовок
                cols = row.find_all('td')
                if len(cols) >= 5:
                    code = cols[1].text.strip()
                    if code in ['USD', 'EUR']:
                        unit = int(cols[2].text.strip())
                        rate = float(cols[4].text.strip().replace(',', '.'))
                        # Приводим к курсу за 1 единицу валюты
                        rates[code] = rate / unit

            if not rates:
                self.error.emit("Не удалось извлечь курсы валют")
                return

            self.rates = rates
            self.finished.emit(rates)

        except Exception as e:
            self.error.emit(f"Ошибка при получении курсов: {str(e)}")


class CurrencyRates(QObject):
    rates_updated = pyqtSignal()
    rates_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.rates_file = "Lab2/currency_rates.json"
        self.rates = {}
        self.last_updated = None
        self.fetcher = RateFetcher()
        self.fetcher.finished.connect(self._on_rates_fetched)
        self.fetcher.error.connect(self.rates_error.emit)
        
        self.load_rates()

    def load_rates(self):
        """Загружает курсы из файла или устанавливает значения по умолчанию"""
        if os.path.exists(self.rates_file):
            try:
                with open(self.rates_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.rates = data.get('rates', {})
                    self.last_updated = data.get('last_updated')
                    print(f"Курсы загружены из файла (обновлено: {self.last_updated})")
            except Exception as e:
                print(f"Ошибка загрузки курсов: {e}. Используются значения по умолчанию.")
                self.set_default_rates()
        else:
            self.set_default_rates()

    def set_default_rates(self):
        """Устанавливает курсы по умолчанию"""
        self.rates = {
            "USD": {"EUR": 1/1.16, "RUB": 81.27},
            "EUR": {"USD": 1.16, "RUB": 93.90},
            "RUB": {"USD": 1/81.27, "EUR": 1/93.90},
        }
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_rates()

    def save_rates(self):
        """Сохраняет курсы в файл"""
        data = {
            'rates': self.rates,
            'last_updated': self.last_updated
        }
        try:
            with open(self.rates_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения курсов: {e}")

    @pyqtSlot(dict)
    def _on_rates_fetched(self, new_rates):
        """Обрабатывает полученные курсы с сайта ЦБ"""
        try:
            # Получаем курсы USD/RUB и EUR/RUB
            usd_rub = new_rates.get('USD')
            eur_rub = new_rates.get('EUR')
            
            if usd_rub and eur_rub:
                # Пересчитываем все курсы на основе полученных данных
                self.rates = {
                    "USD": {
                        "EUR": usd_rub / eur_rub,
                        "RUB": usd_rub
                    },
                    "EUR": {
                        "USD": eur_rub / usd_rub,
                        "RUB": eur_rub
                    },
                    "RUB": {
                        "USD": 1 / usd_rub,
                        "EUR": 1 / eur_rub
                    }
                }
                
                self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_rates()
                self.rates_updated.emit()
                print("Курсы успешно обновлены с сайта ЦБ РФ")
            else:
                self.rates_error.emit("Не удалось получить все необходимые курсы")
                
        except Exception as e:
            self.rates_error.emit(f"Ошибка обработки курсов: {str(e)}")

    def update_rates(self):
        """Запускает обновление курсов"""
        if not self.fetcher.isRunning():
            self.fetcher.start()

    def convert(self, from_curr: str, to_curr: str, amount: float) -> float:
        """Конвертирует сумму из одной валюты в другую"""
        if from_curr == to_curr:
            return amount
        
        try:
            rate = self.rates[from_curr][to_curr]
            return amount * rate
        except KeyError:
            for mid_curr in self.rates.get(from_curr, {}):
                if to_curr in self.rates.get(mid_curr, {}):
                    return amount * self.rates[from_curr][mid_curr] * self.rates[mid_curr][to_curr]
            return 0.0

    def get_rates_text(self) -> str:
        """Возвращает текст с курсами для отображения"""
        lines = []
        for from_curr, to_rates in self.rates.items():
            for to_curr, rate in to_rates.items():
                lines.append(f"   1 {from_curr} = {rate:.6f} {to_curr}")
            lines.append("")
        return "\n".join(lines)

    def get_last_updated(self) -> str:
        """Возвращает время последнего обновления"""
        return self.last_updated or "Неизвестно"