import sys
import os
from datetime import datetime
from PyQt5.QtCore import QUrl, QObject, QTimer, pyqtSignal, pyqtSlot, pyqtProperty
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine


class Interface(QObject):
    # Сигналы для уведомления об изменении свойств
    saveTimerRunningChanged = pyqtSignal()
    saveIntervalChanged = pyqtSignal()
    
    # Сигнал для запроса сохранения
    saveRequested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        # Таймер для автоматического сохранения
        self._save_timer = QTimer()
        self._save_timer.timeout.connect(self._save_canvas_auto)
        
        # Настройки сохранения
        self._save_interval = 10000  # 10 секунд
        self._save_directory = "lab4/saved_canvases"
        self._save_counter = 0
        self._max_saves = 100
        
        # Создаем директорию для сохранения, если её нет
        if not os.path.exists(self._save_directory):
            os.makedirs(self._save_directory)
            print(f"Создана директория: {self._save_directory}")
        
        # Автоматически запускаем автосохранение при создании
        self._save_timer.start(self._save_interval)
        print(f"Автосохранение запущено (интервал: {self._save_interval/1000} секунд)")
    
    # Свойства для QML с сигналами уведомления
    @pyqtProperty(bool, notify=saveTimerRunningChanged)
    def saveTimerRunning(self):
        return self._save_timer.isActive()
    
    @pyqtProperty(int, notify=saveIntervalChanged)
    def saveInterval(self):
        return self._save_interval
    
    @pyqtSlot(int)
    def setSaveInterval(self, interval_ms):
        """Устанавливает интервал автосохранения в миллисекундах"""
        if interval_ms != self._save_interval:
            self._save_interval = interval_ms
            self._save_timer.setInterval(interval_ms)
            self.saveIntervalChanged.emit()
            print(f"Интервал автосохранения изменен на: {interval_ms/1000} секунд")
    
    # Методы для QML
    @pyqtSlot()
    def startAutoSave(self):
        """Запускает автоматическое сохранение"""
        if not self._save_timer.isActive():
            self._save_timer.start(self._save_interval)
            self.saveTimerRunningChanged.emit()
            print("Автосохранение запущено")
    
    @pyqtSlot()
    def stopAutoSave(self):
        """Останавливает автоматическое сохранение"""
        if self._save_timer.isActive():
            self._save_timer.stop()
            self.saveTimerRunningChanged.emit()
            print("Автосохранение остановлено")
    
    @pyqtSlot()
    def toggleAutoSave(self):
        """Переключает состояние автосохранения"""
        if self._save_timer.isActive():
            self.stopAutoSave()
        else:
            self.startAutoSave()
    
    @pyqtSlot()
    def saveCanvasManually(self):
        """Ручное сохранение"""
        print("Ручное сохранение...")
        self.saveRequested.emit()
    
    @pyqtSlot(str, result=str)
    def getSavePath(self, filename):
        """Возвращает полный путь для сохранения файла"""
        return os.path.join(self._save_directory, filename).replace('\\', '/')
    
    def _save_canvas_auto(self):
        """Метод, вызываемый по таймеру для автосохранения (через Python)"""
        print("Автосохранение...")
        self.saveRequested.emit()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    interface = Interface()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("_backend", interface)

    # Загружаем QML
    engine.load("lab4/mainWindow.qml")

    # Проверка успешной загрузки QML
    if not engine.rootObjects():
        print("Ошибка: Не удалось загрузить QML файл!")
        sys.exit(-1)

    sys.exit(app.exec())