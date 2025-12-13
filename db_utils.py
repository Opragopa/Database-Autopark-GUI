from db import get_connection

def fix_misencoded_russian(s: str) -> str:
    if not isinstance(s, str):
        return s
    try:
        return s.encode('cp1251').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError, ValueError):
        return s

# === Для journal_form.py (combo boxes) ===
def get_all_cars_for_combo():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, num FROM auto ORDER BY num")
    rows = [(row[0], fix_misencoded_russian(row[1])) for row in cur.fetchall()]
    conn.close()
    return rows

def get_all_routes_for_combo():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM routes ORDER BY name")
    rows = [(row[0], fix_misencoded_russian(row[1])) for row in cur.fetchall()]
    conn.close()
    return rows

def get_all_drivers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, first_name, last_name, father_name FROM auto_personnel ORDER BY last_name")
    drivers = []
    for row in cur.fetchall():
        drivers.append((
            row[0],
            fix_misencoded_russian(row[1]),
            fix_misencoded_russian(row[2]),
            fix_misencoded_russian(row[3]),
        ))
    conn.close()
    return drivers

def get_all_cars():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, a.num, a.color, a.mark, a.personal_id,
               CONCAT(p.last_name, ' ', p.first_name, ' ', COALESCE(p.father_name, ''))
        FROM auto a
        LEFT JOIN auto_personnel p ON a.personal_id = p.id
        ORDER BY a.num
    """)
    cars = []
    for row in cur.fetchall():
        cars.append((
            row[0],
            fix_misencoded_russian(row[1]),  # num
            fix_misencoded_russian(row[2]),  # color
            fix_misencoded_russian(row[3]),  # mark
            row[4],                          # personal_id
            fix_misencoded_russian(row[5]),  # driver full name (может быть None)
        ))
    conn.close()
    return cars

# === Для routes_view.py ===
def get_all_routes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, data FROM routes ORDER BY name")
    routes = []
    for row in cur.fetchall():
        routes.append((
            row[0],
            fix_misencoded_russian(row[1]),  # name
            row[2],                          # data
        ))
    conn.close()
    return routes

# === Основные функции (journal, отчёты и т.д.) ===
def fetch_journal_with_details():
    conn = get_connection()
    cur = conn.cursor()
    query = """
        SELECT 
            j.id,
            j.time_out,
            j.time_in,
            a.num,
            CONCAT(p.last_name, ' ', p.first_name, ' ', COALESCE(p.father_name, '')),
            r.name,
            j.auto_id,
            j.route_id
        FROM journal j
        JOIN auto a ON j.auto_id = a.id
        JOIN auto_personnel p ON a.personal_id = p.id
        JOIN routes r ON j.route_id = r.id
        ORDER BY j.time_out DESC;
    """
    cur.execute(query)
    rows = []
    for row in cur.fetchall():
        rows.append((
            row[0],
            row[1],
            row[2],
            fix_misencoded_russian(row[3]),
            fix_misencoded_russian(row[4]),
            fix_misencoded_russian(row[5]),
            row[6],
            row[7],
        ))
    conn.close()
    return rows

def call_distribute_bonuses(start_date: str, end_date: str, total_bonus: float):
    conn = get_connection()
    cur = conn.cursor()
    cur.callproc('distribute_bonuses', (start_date, end_date, total_bonus))
    results = []
    for row in cur.fetchall():
        results.append((
            row[0],
            fix_misencoded_russian(row[1]),
            fix_misencoded_russian(row[2]),
            fix_misencoded_russian(row[3]),
            row[4],
            row[5],
            row[6],
            row[7],
        ))
    conn.close()
    return results

def get_routes_avg_time():
    """
    Возвращает список маршрутов со средним временем прохождения.
    Формат: [(название_маршрута, среднее_время_в_минутах), ...]
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Запрос: только те маршруты, у которых есть завершённые рейсы
        cur.execute("""
            SELECT 
                r.name,
                ROUND(AVG(
                    EXTRACT(EPOCH FROM (j.time_in - j.time_out)) / 60
                ), 2) AS avg_minutes
            FROM routes r
            JOIN journal j ON r.id = j.route_id
            WHERE j.time_in IS NOT NULL 
              AND j.time_out IS NOT NULL
              AND j.time_in > j.time_out  -- исключаем некорректные записи
            GROUP BY r.id, r.name
            ORDER BY avg_minutes ASC;
        """)
        results = []
        for row in cur.fetchall():
            # Проверка: есть ли хотя бы 2 элемента
            if len(row) >= 2:
                route_name = fix_misencoded_russian(str(row[0])) if row[0] is not None else "Неизвестный маршрут"
                avg_minutes = float(row[1]) if row[1] is not None else 0.0
                results.append((route_name, avg_minutes))
            else:
                # Пропускаем некорректную строку
                continue
        return results
    except Exception as e:
        # Логирование ошибки (опционально)
        print(f"⚠️ Ошибка в get_routes_avg_time: {e}")
        return []  # Возвращаем пустой список — GUI покажет "Нет данных"
    finally:
        conn.close()

# === CRUD-операции ===
def insert_journal(time_out, time_in, auto_id, route_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO journal (time_out, time_in, auto_id, route_id) VALUES (%s, %s, %s, %s)",
        (time_out, time_in, auto_id, route_id)
    )
    conn.commit()
    conn.close()

def update_journal(journal_id, time_out, time_in, auto_id, route_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE journal 
        SET time_out = %s, time_in = %s, auto_id = %s, route_id = %s 
        WHERE id = %s
    """, (time_out, time_in, auto_id, route_id, journal_id))
    conn.commit()
    conn.close()

def delete_journal(journal_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM journal WHERE id = %s", (journal_id,))
    conn.commit()
    conn.close()

def check_car_returned(auto_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM journal WHERE auto_id = %s AND time_in IS NULL", (auto_id,))
    result = cur.fetchone()
    conn.close()
    return result is None

def get_driver_by_id(driver_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, first_name, last_name, father_name FROM auto_personnel WHERE id = %s", (driver_id,))
    row = cur.fetchone()
    conn.close()
    return row

def insert_driver(first_name, last_name, father_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO auto_personnel (first_name, last_name, father_name) VALUES (%s, %s, %s)",
        (first_name, last_name, father_name)
    )
    conn.commit()
    conn.close()

def update_driver(driver_id, first_name, last_name, father_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE auto_personnel 
        SET first_name = %s, last_name = %s, father_name = %s 
        WHERE id = %s
    """, (first_name, last_name, father_name, driver_id))
    conn.commit()
    conn.close()

def delete_driver(driver_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM auto_personnel WHERE id = %s", (driver_id,))
    conn.commit()
    conn.close()

def get_car_by_id(car_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, a.num, a.color, a.mark, a.personal_id,
               CONCAT(p.last_name, ' ', p.first_name, ' ', COALESCE(p.father_name, ''))
        FROM auto a
        LEFT JOIN auto_personnel p ON a.personal_id = p.id
        WHERE a.id = %s
    """, (car_id,))
    row = cur.fetchone()
    conn.close()
    return row

def get_all_drivers_for_select():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, CONCAT(last_name, ' ', first_name, ' ', COALESCE(father_name, '')) FROM auto_personnel ORDER BY last_name")
    rows = []
    for row in cur.fetchall():
        rows.append((
            row[0],
            fix_misencoded_russian(row[1]) if row[1] else "",
        ))
    conn.close()
    return rows

def insert_car(num, color, mark, personal_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO auto (num, color, mark, personal_id) VALUES (%s, %s, %s, %s)",
        (num, color, mark, personal_id)
    )
    conn.commit()
    conn.close()

def update_car(car_id, num, color, mark, personal_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE auto 
        SET num = %s, color = %s, mark = %s, personal_id = %s 
        WHERE id = %s
    """, (num, color, mark, personal_id, car_id))
    conn.commit()
    conn.close()

def delete_car(car_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM auto WHERE id = %s", (car_id,))
    conn.commit()
    conn.close()

def get_route_by_id(route_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, data FROM routes WHERE id = %s", (route_id,))
    row = cur.fetchone()
    conn.close()
    return row

def insert_route(name, date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO routes (name, data) VALUES (%s, %s)", (name, date))
    conn.commit()
    conn.close()

def update_route(route_id, name, date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE routes SET name = %s, data = %s WHERE id = %s", (name, date, route_id))
    conn.commit()
    conn.close()

def delete_route(route_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM routes WHERE id = %s", (route_id,))
    conn.commit()
    conn.close()

def get_all_cities_list():
    """Возвращает список всех городов РФ (без дубликатов)."""
    conn = get_connection()
    cur = conn.cursor()
    # Извлекаем все уникальные города из маршрутов
    cur.execute("""
        SELECT DISTINCT TRIM(SUBSTRING(name FROM 1 FOR POSITION('-' IN name || '-') - 1)) AS city1,
               TRIM(SUBSTRING(name FROM POSITION('-' IN name || '-') + 1)) AS city2
        FROM routes
        WHERE name LIKE '%-%'
        UNION
        SELECT DISTINCT TRIM(SUBSTRING(name FROM 1 FOR POSITION('—' IN name || '—') - 1)) AS city1,
               TRIM(SUBSTRING(name FROM POSITION('—' IN name || '—') + 1)) AS city2
        FROM routes
        WHERE name LIKE '%—%'
    """)
    cities_set = set()
    for row in cur.fetchall():
        for city in row:
            if city and len(city.strip()) > 0:
                cities_set.add(city.strip())

    # Добавим города, которые есть в таблице routes как одиночные названия
    cur.execute("SELECT DISTINCT name FROM routes WHERE name NOT LIKE '%-%' AND name NOT LIKE '%—%'")
    for row in cur.fetchall():
        if row[0]:
            cities_set.add(row[0].strip())

    conn.close()
    return sorted(list(cities_set))