import sys
import random
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QLabel, QPushButton, QMessageBox, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QColor, QRegion

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_shape_changed = False
        self.setup_ui()

    def setup_ui(self):
       
        self.setMinimumSize(200, 200) 
        self.resize(500, 500)
        self.setWindowTitle("Генератор случайных чисел и смена формы окна")

        self.central_widget = QWidget()
        self.central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(self.central_widget)

        self.central_widget.setStyleSheet("""
            #CentralWidget {
                border: 2px solid #000000;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
        """)

        self.bg_label = QLabel(self.central_widget)
        self.bg_label.setScaledContents(True)
        self.bg_label.setVisible(False)
        self.bg_label.setAttribute(Qt.WA_TransparentForMouseEvents) 

        layout = QVBoxLayout(self.central_widget)
        layout.setAlignment(Qt.AlignCenter)

        self.label = QLabel("Нажмите кнопку для генерации числа")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.label)

        self.btn_change_text = QPushButton("Сгенерировать число")
        self.btn_change_shape = QPushButton("Изменить форму")

        layout.addWidget(self.btn_change_text)
        layout.addWidget(self.btn_change_shape)

        self.btn_change_text.clicked.connect(self.generate_random_number)
        self.btn_change_shape.clicked.connect(self.change_shape)

    def generate_random_number(self):
        random_number = random.randint(1, 1000)
        self.label.setText(f"Случайное число: {random_number}")

    def load_png_shape(self):
        """Загружает PNG и возвращает кортеж (pixmap_for_mask, pixmap_for_bg)."""
        filename = "lab1/shiny-red-heart-symbol-love-affection.png"

        if not os.path.exists(filename):
            QMessageBox.warning(self, "Файл не найден",
                                f"Файл {filename} не найден. Создана круглая форма программно.")
            circle = self.create_circle_shape()
            bg = circle.scaled(max(self.width(), self.height()), max(self.width(), self.height()),
                               Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            return circle, bg

        pixmap = QPixmap(filename)
        if pixmap.isNull():
            QMessageBox.warning(self, "Ошибка загрузки",
                                f"Не удалось загрузить файл {filename}.")
            circle = self.create_circle_shape()
            bg = circle.scaled(max(self.width(), self.height()), max(self.width(), self.height()),
                               Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            return circle, bg

        circle_size = int(min(self.width(), self.height()) * 0.8)
        circle_size = max(circle_size, 200)

        pixmap_for_mask = pixmap.scaled(circle_size, circle_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        bg_pixmap = pixmap.scaled(self.central_widget.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        return pixmap_for_mask, bg_pixmap

    def create_circle_shape(self):
        """Создает круглую форму программно, подгоняя под размер окна"""
        circle_size = int(min(self.width(), self.height()) * 0.8)
        circle_size = max(circle_size, 200)

        pixmap = QPixmap(circle_size, circle_size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(100, 150, 200, 180)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, circle_size, circle_size)
        painter.end()

        return pixmap

    def resizeEvent(self, event):
        self.bg_label.setGeometry(0, 0, self.central_widget.width(), self.central_widget.height())

        if self.is_shape_changed and not self.bg_label.pixmap().isNull():
            bg = self.bg_label.pixmap()
            if not bg.isNull():
                scaled_bg = bg.scaled(self.central_widget.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                self.bg_label.setPixmap(scaled_bg)
        super().resizeEvent(event)

    def change_shape(self):
        if not self.is_shape_changed:
            pixmap_mask, pixmap_bg = self.load_png_shape()

            mask = pixmap_mask.mask()
            if mask.isNull():
                mask = pixmap_mask.createMaskFromColor(QColor(0, 0, 0, 0), Qt.MaskOutColor)

            current_size = self.size()
            mask_size = pixmap_mask.size()
            x_offset = (current_size.width() - mask_size.width()) // 2
            y_offset = (current_size.height() - mask_size.height()) // 2

            region = QRegion(mask)
            region.translate(x_offset, y_offset)
            self.setMask(region)

            self.setWindowOpacity(0.85)

            if not pixmap_bg.isNull():
                scaled_bg = pixmap_bg.scaled(self.central_widget.size(),
                                             Qt.KeepAspectRatioByExpanding,
                                             Qt.SmoothTransformation)
                self.bg_label.setPixmap(scaled_bg)

            effect = QGraphicsOpacityEffect(self.bg_label)
            effect.setOpacity(0.6)
            self.bg_label.setGraphicsEffect(effect)
            self.bg_label.setVisible(True)

            self.is_shape_changed = True
            self.btn_change_shape.setText("Восстановить форму")
        else:
            self.clearMask()
            self.setWindowOpacity(1.0)
            self.bg_label.setVisible(False)
            self.bg_label.setPixmap(QPixmap())
            self.bg_label.setGraphicsEffect(None)
            self.is_shape_changed = False
            self.btn_change_shape.setText("Изменить форму")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
