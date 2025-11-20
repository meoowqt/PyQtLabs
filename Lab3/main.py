import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, 
                             QWidget, QPushButton, QFileDialog, QMessageBox, 
                             QTableView, QComboBox, QDialog, QTextEdit, 
                             QHBoxLayout, QLabel, QDialogButtonBox, QToolBar,
                             QStatusBar, QMenuBar, QHeaderView, QFrame)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont, QPalette, QColor
from PyQt5.QtCore import Qt

class QueryDialog(QDialog):
    """Модальное окно для выполнения произвольных SQL-запросов"""
    def __init__(self, parent=None, connection=None):
        super().__init__(parent)
        self.connection = connection
        self.setWindowTitle("Выполнить SQL-запрос")
        self.setModal(True)
        self.resize(700, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                font-family: Consolas, monospace;
            }
            QLabel {
                font-weight: bold;
                color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Поле для ввода запроса
        self.query_edit = QTextEdit()
        self.query_edit.setPlaceholderText("Введите SQL-запрос...")
        layout.addWidget(QLabel("SQL-запрос:"))
        layout.addWidget(self.query_edit)
        
        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.execute_query)
        button_box.rejected.connect(self.reject)
        
        # Стилизация кнопок для темной темы
        button_box.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton[text="Cancel"] {
                background-color: #f44336;
            }
            QPushButton[text="Cancel"]:hover {
                background-color: #da190b;
            }
        """)
        
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def execute_query(self):
        query = self.query_edit.toPlainText().strip()
        if not query:
            QMessageBox.warning(self, "Ошибка", "Введите SQL-запрос")
            return
            
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            if query.lower().startswith('select'):
                # Для SELECT запросов показываем результаты
                result = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels(columns)
                
                for row in result:
                    items = [QStandardItem(str(item)) for item in row]
                    model.appendRow(items)
                
                result_dialog = QDialog(self)
                result_dialog.setWindowTitle("Результат запроса")
                result_dialog.resize(900, 500)
                result_dialog.setStyleSheet("""
                    QDialog {
                        background-color: #2b2b2b;
                        color: #ffffff;
                    }
                    QTableView {
                        background-color: #3c3c3c;
                        color: #ffffff;
                        alternate-background-color: #404040;
                        selection-background-color: #4CAF50;
                        gridline-color: #555;
                    }
                    QTableView::item {
                        padding: 5px;
                        border-bottom: 1px solid #555;
                    }
                    QHeaderView::section {
                        background-color: #2196F3;
                        color: white;
                        padding: 5px;
                        font-weight: bold;
                        border: none;
                    }
                """)
                
                layout = QVBoxLayout()
                table_view = QTableView()
                table_view.setModel(model)
                table_view.resizeColumnsToContents()
                table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                table_view.setAlternatingRowColors(True)
                layout.addWidget(table_view)
                
                button_box = QDialogButtonBox(QDialogButtonBox.Ok)
                button_box.accepted.connect(result_dialog.accept)
                button_box.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                """)
                layout.addWidget(button_box)
                
                result_dialog.setLayout(layout)
                result_dialog.exec_()
            else:
                # Для других запросов подтверждаем выполнение
                self.connection.commit()
                QMessageBox.information(self, "Успех", "Запрос выполнен успешно")
                self.accept()
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса:\n{str(e)}")

class TransportApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.connection = None
        self.current_db_path = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Транспортная компания - Управление перевозками")
        self.setGeometry(100, 100, 1200, 800)
        
        # Установка темной темы приложения
        self.set_dark_theme()
        
        # Центральный виджет с вкладками
        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)
        
        # Создаем начальные вкладки
        self.create_initial_tabs()
        
        # Создаем меню
        self.create_menu()
        
        # Панель инструментов
        self.create_toolbar()
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе - подключите базу данных")
        
    def set_dark_theme(self):
        """Устанавливает темную тему для приложения"""
        dark_stylesheet = """
            QMainWindow {
                background-color: #2b2b2b;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #3c3c3c;
                border-radius: 4px;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #cccccc;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #2196F3;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #555;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
            QComboBox {
                padding: 6px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #3c3c3c;
                color: white;
                min-width: 150px;
            }
            QComboBox:disabled {
                background-color: #333;
                color: #666;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: white;
                selection-background-color: #2196F3;
            }
            QTableView {
                background-color: #3c3c3c;
                color: white;
                alternate-background-color: #404040;
                selection-background-color: #4CAF50;
                gridline-color: #555;
                border: none;
            }
            QTableView::item {
                padding: 6px;
                border-bottom: 1px solid #444;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
            QLabel {
                color: #ffffff;
                font-weight: bold;
            }
            QToolBar {
                background-color: #333;
                border: none;
                border-bottom: 1px solid #444;
                padding: 5px;
                spacing: 10px;
            }
            QStatusBar {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
            }
            QMenuBar {
                background-color: #222;
                color: white;
                font-weight: bold;
            }
            QMenuBar::item:selected {
                background-color: #2196F3;
            }
            QMenu {
                background-color: #333;
                color: white;
                border: 1px solid #555;
            }
            QMenu::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QFrame {
                background-color: #333;
            }
            QTextEdit {
                background-color: #3c3c3c;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
            }
        """
        self.setStyleSheet(dark_stylesheet)
        
    def create_initial_tabs(self):
        """Создает начальные пустые вкладки с красивым оформлением в темной теме"""
        tab_names = [
            "Схема БД",
            "Список таблиц", 
            "Данные по колонке",
            "Водители",
            "Транспорт",
            "Рейсы"
        ]
        
        for i, name in enumerate(tab_names):
            tab = QWidget()
            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignCenter)
            
            # Создаем красивый заголовок
            title_label = QLabel(name)
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    color: #cccccc;
                    font-weight: bold;
                    margin: 20px;
                }
            """)
            layout.addWidget(title_label)
            
            # Добавляем иконку и описание
            descriptions = [
                "Информация о структуре базы данных",
                "Список всех таблиц в системе",
                "Просмотр данных по выбранной колонке", 
                "Управление водителями и их данными",
                "Информация о транспортных средствах",
                "Отслеживание рейсов и маршрутов"
            ]
            
            desc_label = QLabel(descriptions[i])
            desc_label.setAlignment(Qt.AlignCenter)
            desc_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #aaaaaa;
                    margin: 10px;
                }
            """)
            layout.addWidget(desc_label)
            
            # Добавляем подсказку
            hint_label = QLabel("Данные появятся после подключения к базе данных")
            hint_label.setAlignment(Qt.AlignCenter)
            hint_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #888888;
                    font-style: italic;
                    margin: 20px;
                }
            """)
            layout.addWidget(hint_label)
            
            tab.setLayout(layout)
            self.central_widget.addTab(tab, name)
    
    def create_menu(self):
        """Создает меню приложения"""
        menubar = self.menuBar()
        
        # Меню Подключение
        connection_menu = menubar.addMenu('Подключение')
        
        set_connection_action = connection_menu.addAction('Установить соединение')
        set_connection_action.triggered.connect(self.set_connection)
        
        close_connection_action = connection_menu.addAction('Закрыть соединение')
        close_connection_action.triggered.connect(self.close_connection)
        
        # Меню Запросы
        query_menu = menubar.addMenu('Запросы')
        custom_query_action = query_menu.addAction('Произвольный SQL-запрос')
        custom_query_action.triggered.connect(self.show_custom_query_dialog)
    
    def create_toolbar(self):
        """Создает панель инструментов с кнопками и комбобоксом"""
        toolbar = QToolBar('Основные инструменты')
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        
        # Кнопка "Список таблиц"
        self.bt_tables = QPushButton('Список таблиц')
        self.bt_tables.clicked.connect(self.show_tables_list)
        toolbar.addWidget(self.bt_tables)
        
        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #555;")
        toolbar.addWidget(separator)
        
        # Выпадающий список для колонок
        toolbar.addWidget(QLabel("Колонка:"))
        self.column_combo = QComboBox()
        self.column_combo.setMinimumWidth(200)
        self.column_combo.currentTextChanged.connect(self.on_column_changed)
        toolbar.addWidget(self.column_combo)
        
        # Разделитель
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setStyleSheet("background-color: #555;")
        toolbar.addWidget(separator2)
        
        # Кнопка "Список водителей"
        self.bt_drivers = QPushButton('Список водителей')
        self.bt_drivers.clicked.connect(self.show_drivers_list)
        toolbar.addWidget(self.bt_drivers)
        
        # Кнопка "Список транспорта"
        self.bt_vehicles = QPushButton('Список транспорта')
        self.bt_vehicles.clicked.connect(self.show_vehicles_list)
        toolbar.addWidget(self.bt_vehicles)
        
        # Кнопка "Активные рейсы"
        self.bt_active_trips = QPushButton('Активные рейсы')
        self.bt_active_trips.clicked.connect(self.show_active_trips)
        toolbar.addWidget(self.bt_active_trips)
        
        # Кнопка "Доходы по рейсам"
        self.bt_revenue = QPushButton('Доходы по рейсам')
        self.bt_revenue.clicked.connect(self.show_revenue_report)
        toolbar.addWidget(self.bt_revenue)
        
        # Изначально отключаем элементы, пока нет подключения
        self.set_connection_elements_enabled(False)
    
    def set_connection_elements_enabled(self, enabled):
        """Включает/выключает элементы управления"""
        self.bt_tables.setEnabled(enabled)
        self.bt_drivers.setEnabled(enabled)
        self.bt_vehicles.setEnabled(enabled)
        self.bt_active_trips.setEnabled(enabled)
        self.bt_revenue.setEnabled(enabled)
        self.column_combo.setEnabled(enabled)
    
    def set_connection(self):
        """Установка соединения с БД"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Выберите файл базы данных транспортной компании", 
            "", 
            "SQLite Databases (*.db *.sqlite *.sqlite3);;All Files (*)"
        )
        
        if file_path:
            try:
                if self.connection:
                    self.connection.close()
                
                self.connection = sqlite3.connect(file_path)
                self.current_db_path = file_path
                
                # Обновляем первую вкладку с информацией о схеме БД
                self.update_schema_tab()
                
                # Обновляем комбобокс с колонками
                self.update_column_combo()
                
                self.set_connection_elements_enabled(True)
                self.status_bar.showMessage(f"Подключено к БД: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка подключения", f"Не удалось подключиться к БД:\n{str(e)}")
    
    def close_connection(self):
        """Закрытие соединения с БД"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.current_db_path = None
        
        # Очищаем все вкладки - создаем новые виджеты вместо изменения существующих
        for i in range(self.central_widget.count()):
            # Создаем полностью новую вкладку вместо изменения существующей
            new_tab = self.create_empty_tab(i)
            
            # Заменяем вкладку
            self.central_widget.removeTab(i)
            self.central_widget.insertTab(i, new_tab, self.get_tab_name(i))
        
        self.column_combo.clear()
        self.set_connection_elements_enabled(False)
        self.status_bar.showMessage("Соединение с БД закрыто")
    
    def create_empty_tab(self, index):
        """Создает пустую вкладку с красивым оформлением в темной теме"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        tab_names = ["Схема БД", "Список таблиц", "Данные по колонке", "Водители", "Транспорт", "Рейсы"]
        descriptions = [
            "Информация о структуре базы данных",
            "Список всех таблиц в системе",
            "Просмотр данных по выбранной колонке", 
            "Управление водителями и их данными",
            "Информация о транспортных средствах",
            "Отслеживание рейсов и маршрутов"
        ]
        
        title_label = QLabel(tab_names[index])
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #cccccc;
                font-weight: bold;
                margin: 20px;
            }
        """)
        layout.addWidget(title_label)
        
        desc_label = QLabel(descriptions[index])
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #aaaaaa;
                margin: 10px;
            }
        """)
        layout.addWidget(desc_label)
        
        hint_label = QLabel("Данные появятся после подключения к базе данных")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #888888;
                font-style: italic;
                margin: 20px;
            }
        """)
        layout.addWidget(hint_label)
        
        tab.setLayout(layout)
        return tab
    
    def get_tab_name(self, index):
        """Возвращает название вкладки по индексу"""
        tab_names = ["Схема БД", "Список таблиц", "Данные по колонке", "Водители", "Транспорт", "Рейсы"]
        return tab_names[index]
    
    def update_schema_tab(self):
        """Обновляет вкладку с информацией о схеме БД"""
        if not self.connection:
            return
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM sqlite_master WHERE type='table'")
            result = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            # Создаем модель для таблицы
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(columns)
            
            for row in result:
                items = [QStandardItem(str(item)) for item in row]
                model.appendRow(items)
            
            # Обновляем первую вкладку
            self.update_tab_with_table(0, model, "Схема базы данных транспортной компании")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при получении схемы БД:\n{str(e)}")
    
    def update_column_combo(self):
        """Обновляет комбобокс с доступными колонками"""
        if not self.connection:
            return
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            columns = set()
            for table in tables:
                try:
                    cursor.execute(f"PRAGMA table_info({table})")
                    table_columns = cursor.fetchall()
                    for col in table_columns:
                        columns.add(f"{table}.{col[1]}")  # формат: таблица.колонка
                except:
                    continue  # Пропускаем таблицы с ошибками
            
            self.column_combo.clear()
            self.column_combo.addItems(sorted(columns))
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при получении колонок:\n{str(e)}")
    
    def show_tables_list(self):
        """Показывает список таблиц БД"""
        if not self.connection:
            QMessageBox.warning(self, "Ошибка", "Нет подключения к базе данных")
            return
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            result = cursor.fetchall()
            
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(['Название таблицы'])
            
            for row in result:
                items = [QStandardItem(str(item)) for item in row]
                model.appendRow(items)
            
            self.update_tab_with_table(1, model, "Таблицы в базе данных")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса:\n{str(e)}")
    
    def show_drivers_list(self):
        """Показывает список водителей"""
        if not self.connection:
            QMessageBox.warning(self, "Ошибка", "Нет подключения к базе данных")
            return
            
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT 
                    driver_id,
                    first_name,
                    last_name,
                    license_number,
                    phone,
                    email,
                    hire_date,
                    status,
                    salary
                FROM drivers
                ORDER BY status, last_name
            ''')
            result = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(columns)
            
            for row in result:
                items = [QStandardItem(str(item)) for item in row]
                model.appendRow(items)
            
            self.update_tab_with_table(3, model, "Список водителей")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса:\n{str(e)}")
    
    def on_column_changed(self, column_full_name):
        """Обработчик изменения выбранной колонки"""
        if not self.connection or not column_full_name:
            return
            
        try:
            # Разделяем на таблицу и колонку
            table_name, column_name = column_full_name.split('.')
            
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT {column_name} FROM {table_name} LIMIT 100")
            result = cursor.fetchall()
            
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels([f'{table_name}.{column_name}'])
            
            for row in result:
                items = [QStandardItem(str(item)) for item in row]
                model.appendRow(items)
            
            self.update_tab_with_table(2, model, f"Данные из {table_name}.{column_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса для колонки:\n{str(e)}")
    
    def show_active_trips(self):
        """Показывает активные рейсы"""
        if not self.connection:
            QMessageBox.warning(self, "Ошибка", "Нет подключения к базе данных")
            return
            
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT t.trip_id, r.start_city, r.end_city, 
                       d.first_name || ' ' || d.last_name as driver,
                       v.license_plate, t.departure_time, t.status
                FROM trips t
                JOIN routes r ON t.route_id = r.route_id
                JOIN drivers d ON t.driver_id = d.driver_id
                JOIN vehicles v ON t.vehicle_id = v.vehicle_id
                WHERE t.status IN ('in_progress', 'scheduled')
                ORDER BY t.departure_time
            ''')
            result = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(columns)
            
            for row in result:
                items = [QStandardItem(str(item)) for item in row]
                model.appendRow(items)
            
            self.update_tab_with_table(5, model, "Активные и запланированные рейсы")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса:\n{str(e)}")
    
    def show_revenue_report(self):
        """Показывает отчет по доходам"""
        if not self.connection:
            QMessageBox.warning(self, "Ошибка", "Нет подключения к базе данных")
            return
            
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT 
                    t.trip_id,
                    r.start_city || ' - ' || r.end_city as route,
                    t.cargo_description,
                    t.cargo_weight_kg,
                    t.revenue,
                    t.departure_time
                FROM trips t
                JOIN routes r ON t.route_id = r.route_id
                WHERE t.status = 'completed'
                ORDER BY t.revenue DESC
            ''')
            result = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(columns)
            
            total_revenue = 0
            for row in result:
                items = [QStandardItem(str(item)) for item in row]
                model.appendRow(items)
                if row[4]:  # revenue
                    total_revenue += float(row[4])
            
            # Добавляем итоговую строку
            if result:
                model.appendRow([
                    QStandardItem("ИТОГО"),
                    QStandardItem(""),
                    QStandardItem(""),
                    QStandardItem(""),
                    QStandardItem(f"{total_revenue:.2f} руб."),
                    QStandardItem("")
                ])
            
            self.update_tab_with_table(5, model, "Отчет по доходам от выполненных рейсов")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса:\n{str(e)}")
    
    def show_vehicles_list(self):
        """Показывает список транспортных средств"""
        if not self.connection:
            QMessageBox.warning(self, "Ошибка", "Нет подключения к базе данных")
            return
            
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT 
                    vehicle_id,
                    license_plate,
                    model,
                    type,
                    capacity_kg,
                    year,
                    status,
                    last_maintenance,
                    next_maintenance
                FROM vehicles
                ORDER BY status, model
            ''')
            result = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(columns)
            
            for row in result:
                items = [QStandardItem(str(item)) for item in row]
                model.appendRow(items)
            
            self.update_tab_with_table(4, model, "Список транспортных средств")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса:\n{str(e)}")
    
    def update_tab_with_table(self, tab_index, model, title):
        """Обновляет указанную вкладку таблицей"""
        if tab_index >= self.central_widget.count():
            return
            
        # Создаем полностью новую вкладку вместо изменения существующей
        new_tab = QWidget()
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #4CAF50;
                margin: 15px;
                padding: 10px;
                background-color: #1e1e1e;
                border-radius: 6px;
            }
        """)
        layout.addWidget(title_label)
        
        # Информация о количестве строк
        count_label = QLabel(f"Найдено записей: {model.rowCount()}")
        count_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #cccccc;
                margin: 5px 15px;
            }
        """)
        layout.addWidget(count_label)
        
        # Таблица
        table_view = QTableView()
        table_view.setModel(model)
        table_view.resizeColumnsToContents()
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        table_view.setAlternatingRowColors(True)
        table_view.setSelectionBehavior(QTableView.SelectRows)
        layout.addWidget(table_view)
        
        new_tab.setLayout(layout)
        
        # Заменяем вкладку
        current_tab_text = self.central_widget.tabText(tab_index)
        self.central_widget.removeTab(tab_index)
        self.central_widget.insertTab(tab_index, new_tab, current_tab_text)
        self.central_widget.setCurrentIndex(tab_index)
    
    def show_custom_query_dialog(self):
        """Показывает модальное окно для выполнения произвольных SQL-запросов"""
        if not self.connection:
            QMessageBox.warning(self, "Ошибка", "Сначала установите соединение с БД")
            return
            
        dialog = QueryDialog(self, self.connection)
        dialog.exec_()

def main():
    app = QApplication(sys.argv)
    
    # Установка темной палитры для всего приложения
    app.setStyle('Fusion')
    
    # Дополнительная настройка темной темы
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(43, 43, 43))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(dark_palette)
    
    window = TransportApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()