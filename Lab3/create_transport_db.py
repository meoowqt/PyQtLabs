import sqlite3
import os
from datetime import datetime, timedelta
import random

def create_transport_database():
    # Удаляем старую БД если существует
    if os.path.exists('transport_company.db'):
        os.remove('transport_company.db')
    
    # Создаем соединение с БД
    conn = sqlite3.connect('transport_company.db')
    cursor = conn.cursor()
    
    # Создаем таблицу водителей
    cursor.execute('''
        CREATE TABLE drivers (
            driver_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            license_number TEXT UNIQUE NOT NULL,
            phone TEXT,
            email TEXT,
            hire_date TEXT,
            status TEXT DEFAULT 'active',
            salary REAL DEFAULT 0
        )
    ''')
    
    # Создаем таблицу транспортных средств
    cursor.execute('''
        CREATE TABLE vehicles (
            vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_plate TEXT UNIQUE NOT NULL,
            model TEXT NOT NULL,
            type TEXT NOT NULL,
            capacity_kg REAL NOT NULL,
            year INTEGER,
            status TEXT DEFAULT 'available',
            last_maintenance TEXT,
            next_maintenance TEXT
        )
    ''')
    
    # Создаем таблицу маршрутов
    cursor.execute('''
        CREATE TABLE routes (
            route_id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_city TEXT NOT NULL,
            end_city TEXT NOT NULL,
            distance_km REAL NOT NULL,
            estimated_time_hours REAL NOT NULL,
            base_price REAL NOT NULL
        )
    ''')
    
    # Создаем таблицу рейсов
    cursor.execute('''
        CREATE TABLE trips (
            trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
            route_id INTEGER,
            driver_id INTEGER,
            vehicle_id INTEGER,
            departure_time TEXT,
            arrival_time TEXT,
            actual_distance_km REAL,
            status TEXT DEFAULT 'scheduled',
            cargo_description TEXT,
            cargo_weight_kg REAL,
            revenue REAL,
            FOREIGN KEY (route_id) REFERENCES routes (route_id),
            FOREIGN KEY (driver_id) REFERENCES drivers (driver_id),
            FOREIGN KEY (vehicle_id) REFERENCES vehicles (vehicle_id)
        )
    ''')
    
    # Создаем таблицу клиентов
    cursor.execute('''
        CREATE TABLE clients (
            client_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            address TEXT
        )
    ''')
    
    # Добавляем водителей
    drivers = [
        ('Иван', 'Петров', 'AB123456', '+79161234567', 'ivan@mail.com', '2022-01-15', 'active', 65000),
        ('Петр', 'Сидоров', 'AB123457', '+79161234568', 'petr@mail.com', '2022-03-20', 'active', 62000),
        ('Мария', 'Иванова', 'AB123458', '+79161234569', 'maria@mail.com', '2021-11-10', 'active', 68000),
        ('Сергей', 'Козлов', 'AB123459', '+79161234570', 'sergey@mail.com', '2023-02-05', 'active', 60000),
        ('Анна', 'Морозова', 'AB123460', '+79161234571', 'anna@mail.com', '2022-07-12', 'vacation', 63000),
        ('Дмитрий', 'Новиков', 'AB123461', '+79161234572', 'dmitry@mail.com', '2021-05-30', 'active', 70000)
    ]
    
    cursor.executemany(
        'INSERT INTO drivers (first_name, last_name, license_number, phone, email, hire_date, status, salary) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        drivers
    )
    
    # Добавляем транспортные средства
    vehicles = [
        ('А123ВС77', 'Volvo FH16', 'грузовик', 20000, 2020, 'available', '2024-01-15', '2024-04-15'),
        ('В456ОР77', 'MAN TGX', 'грузовик', 18000, 2021, 'available', '2024-02-10', '2024-05-10'),
        ('С789ТК77', 'Scania R450', 'фура', 25000, 2019, 'maintenance', '2024-01-20', '2024-04-20'),
        ('Е321ХА77', 'Mercedes Actros', 'рефрижератор', 15000, 2022, 'available', '2024-03-01', '2024-06-01'),
        ('М654УН77', 'DAF XF', 'грузовик', 22000, 2020, 'on_route', '2024-02-28', '2024-05-28'),
        ('О987РВ77', 'Renault Magnum', 'фура', 24000, 2018, 'available', '2024-01-30', '2024-04-30')
    ]
    
    cursor.executemany(
        'INSERT INTO vehicles (license_plate, model, type, capacity_kg, year, status, last_maintenance, next_maintenance) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        vehicles
    )
    
    # Добавляем маршруты
    routes = [
        ('Москва', 'Санкт-Петербург', 710, 10, 25000),
        ('Москва', 'Казань', 815, 12, 28000),
        ('Москва', 'Нижний Новгород', 420, 6, 15000),
        ('Санкт-Петербург', 'Москва', 710, 10, 25000),
        ('Санкт-Петербург', 'Псков', 290, 5, 12000),
        ('Казань', 'Самара', 350, 6, 13000),
        ('Нижний Новгород', 'Москва', 420, 6, 15000),
        ('Москва', 'Ростов-на-Дону', 1070, 15, 35000)
    ]
    
    cursor.executemany(
        'INSERT INTO routes (start_city, end_city, distance_km, estimated_time_hours, base_price) VALUES (?, ?, ?, ?, ?)',
        routes
    )
    
    # Добавляем клиентов
    clients = [
        ('ООО "Ромашка"', 'Ирина Смирнова', '+79161234573', 'sales@romashka.ru', 'Москва, ул. Ленина, 1'),
        ('АО "Технопром"', 'Алексей Волков', '+79161234574', 'volkov@tehnoprom.ru', 'Санкт-Петербург, Невский пр., 100'),
        ('ИП "Сидоров А.В."', 'Андрей Сидоров', '+79161234575', 'sidorov@mail.com', 'Казань, ул. Баумана, 50'),
        ('ООО "Северсталь"', 'Ольга Ковалева', '+79161234576', 'kovaleva@severstal.ru', 'Череповец, ул. Металлургов, 25'),
        ('АО "ЮгТранс"', 'Денис Павлов', '+79161234577', 'pavlov@yugtrans.ru', 'Ростов-на-Дону, ул. Садовая, 75')
    ]
    
    cursor.executemany(
        'INSERT INTO clients (company_name, contact_person, phone, email, address) VALUES (?, ?, ?, ?, ?)',
        clients
    )
    
    # Добавляем рейсы
    trips = [
        (1, 1, 1, '2024-03-20 08:00:00', '2024-03-20 18:00:00', 710, 'completed', 'Электроника', 12000, 25000),
        (2, 2, 2, '2024-03-21 06:00:00', '2024-03-21 18:00:00', 815, 'completed', 'Одежда', 15000, 28000),
        (3, 3, 3, '2024-03-22 09:00:00', '2024-03-22 15:00:00', 420, 'in_progress', 'Продукты питания', 8000, 15000),
        (4, 4, 4, '2024-03-23 07:00:00', '2024-03-23 17:00:00', 710, 'scheduled', 'Строительные материалы', 13000, 25000),
        (5, 5, 5, '2024-03-24 10:00:00', '2024-03-24 15:00:00', 290, 'scheduled', 'Мебель', 10000, 12000),
        (6, 6, 6, '2024-03-25 08:30:00', '2024-03-25 14:30:00', 350, 'scheduled', 'Химические товары', 16000, 13000)
    ]
    
    cursor.executemany(
        'INSERT INTO trips (route_id, driver_id, vehicle_id, departure_time, arrival_time, actual_distance_km, status, cargo_description, cargo_weight_kg, revenue) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        trips
    )
    
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()
    
    print("База данных транспортной компании успешно создана!")
    print("Файл: transport_company.db")

if __name__ == '__main__':
    create_transport_database()