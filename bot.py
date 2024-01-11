import sqlite3
from datetime import datetime, timedelta

# Подключение к базе данных
conn = sqlite3.connect('schedule.db')
cursor = conn.cursor()

# Создание таблиц в базе данных
cursor.execute('''
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number INTEGER NOT NULL,
        capacity INTEGER NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        teacher_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        day DATE NOT NULL,
        time_slot INTEGER NOT NULL,
        is_deleted INTEGER DEFAULT 0,
        FOREIGN KEY (subject_id) REFERENCES subjects(id),
        FOREIGN KEY (teacher_id) REFERENCES teachers(id),
        FOREIGN KEY (room_id) REFERENCES rooms(id)
    )
''')
conn.commit()

#функции с добавлениями. Классы я стараюсь не юзать, сорри
def add_subject(name):
    cursor.execute('INSERT INTO subjects (name) VALUES (?)', (name,))
    conn.commit()
    print("\nПредмет добавлен")

def add_teacher(name):
    cursor.execute('INSERT INTO teachers (name) VALUES (?)', (name,))
    conn.commit()
    print("\nПреподаватель добавлен")

def add_room(number, capacity):
    cursor.execute('INSERT INTO rooms (number, capacity) VALUES (?, ?)', (number, capacity))
    conn.commit()
    print("\nКласс добавлен")

def add_schedule(subject_id, teacher_id, room_id, day, time_slot):
    cursor.execute('''
        SELECT COUNT(id) FROM schedule
        WHERE teacher_id = ? AND day = ? AND time_slot = ? AND is_deleted = 0
    ''', (teacher_id, day, time_slot))
    occupied_slots_count = cursor.fetchone()[0]

    if occupied_slots_count > 0:
        print("Выбранный номер урока уже занят.")
        return

    cursor.execute('''
        SELECT COUNT(id) FROM schedule
        WHERE teacher_id = ? AND day = ? AND is_deleted = 0
    ''', (teacher_id, day))
    lesson_count = cursor.fetchone()[0]

    if lesson_count >= 5:
        print("Преподаватель не может провести более 5 уроков в день.")
        return
    cursor.execute('''
        INSERT INTO schedule (subject_id, teacher_id, room_id, day, time_slot)
        VALUES (?, ?, ?, ?, ?)
    ''', (subject_id, teacher_id, room_id, day, time_slot))
    conn.commit()
    print("Запись в расписание добвлена")

#получение сегодняшней даты
def get_today_schedule():
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT subjects.name, teachers.name, rooms.number, schedule.time_slot
        FROM schedule
        JOIN subjects ON schedule.subject_id = subjects.id
        JOIN teachers ON schedule.teacher_id = teachers.id
        JOIN rooms ON schedule.room_id = rooms.id
        WHERE schedule.day = ? AND schedule.is_deleted = 0
    ''', (today,))
    schedule = cursor.fetchall()
    return schedule

#удаление занятия
def delete_schedule_entry(entry_id):
    cursor.execute('UPDATE schedule SET is_deleted = 1 WHERE id = ?', (entry_id,))
    conn.commit()
    print("\nЗанятие удалено")

#форматирование данных для вывода
def format_schedule_entry(entry, state=False):
    return state and f"ID: {entry[5]} {entry[3]}. {entry[0]} с учителем {entry[1]} в кабинете {entry[2]}" or f"{entry[3]}. {entry[0]} с учителем {entry[1]} в кабинете {entry[2]}"

#основное меню
def print_menu():
    print("\n1. Добавить предмет")
    print("2. Добавить преподавателя")
    print("3. Добавить кабинет")
    print("4. Добавить запись в расписание")
    print("5. Просмотреть расписание на сегодня")
    print("6. Удалить запись из расписания")
    print("0. Выйти")

def user_input():
    return input("\nВыберите действие (введите соответствующую цифру): ")

#Функции вывода информации с базы (у меня же нa ID`ax все завязано)
def print_subjects():
    cursor.execute('SELECT * FROM subjects')
    subjects = cursor.fetchall()
    print("Доступные предметы:")
    for subject in subjects:
        print(f"ID: {subject[0]}, Название: {subject[1]}")

def print_teacher():
    cursor.execute('SELECT * FROM teachers')
    teachers = cursor.fetchall()
    print("Доступные преподаватели:")
    for teacher in teachers:
        print(f"ID: {teacher[0]}, Название: {teacher[1]}")

def print_rooms():
    cursor.execute('SELECT * FROM rooms')
    rooms = cursor.fetchall()
    print("Доступные кабинеты:")
    for room in rooms:
        print(f"ID: {room[0]}, Номер кабинета: {room[1]}, Вместимость: {room[2]}")

def print_schedule():
    cursor.execute('''
        SELECT subjects.name, teachers.name, rooms.number, schedule.day, schedule.time_slot, schedule.id
        FROM schedule
        JOIN subjects ON schedule.subject_id = subjects.id
        JOIN teachers ON schedule.teacher_id = teachers.id
        JOIN rooms ON schedule.room_id = rooms.id
    ''')
    schedule = cursor.fetchall()
    if not schedule:
        print("Расписания нет.")
    else:
        print("Расписание:")
        for entry in schedule:
            print(format_schedule_entry(entry, True))

#мейн функция
while True:
    print_menu()
    choice = user_input()

    if choice == "1":
        subject_name = input("Введите название предмета: ")
        add_subject(subject_name)

    elif choice == "2":
        teacher_name = input("Введите имя преподавателя: ")
        add_teacher(teacher_name)

    elif choice == "3":
        room_number = int(input("Введите номер кабинета: "))
        if not (1 <= room_number <= 150):
            print("Некорректный номер кабинета. Введите число от 1 до 150.")
        else:
            room_capacity = int(input("Введите вместимость кабинета: "))
            add_room(room_number, room_capacity)

    elif choice == "4":
        print_subjects()
        subject_id = int(input("Введите ID предмета: "))
        print_teacher()
        teacher_id = int(input("Введите ID преподавателя: "))
        print_rooms()
        room_id = int(input("Введите ID кабинета: "))
        day = input("Введите день в формате YYYY-MM-DD: ")
        time_slot = int(input("Введите номер урока: "))
        add_schedule(subject_id, teacher_id, room_id, day, time_slot)

    elif choice == "5":
        today_schedule = get_today_schedule()
        if not today_schedule:
            print("\nНа сегодня расписания нет.")
        else:
            print("\nРасписание на сегодня:")
            sorted_schedule = sorted(today_schedule, key=lambda x: x[3])  # Сортировка по дню
            for entry in sorted_schedule:
                print(format_schedule_entry(entry))

    elif choice == "6":
        print_schedule()
        entry_id_to_delete = int(input("Введите ID записи для удаления: "))
        delete_schedule_entry(entry_id_to_delete)

    elif choice == "0":
        break

    else:
        print("Некорректный ввод. Попробуйте еще раз.")
