from db import get_connection

def fix_misencoded_russian(s: str) -> str:
    """
    Исправляет текст, искажённый из-за того, что UTF-8 данные были прочитаны как cp1251.
    Пример: "®892®­" → "а467на"
    """
    if not isinstance(s, str):
        return s
    try:
        # Ключевая операция: cp1251 → UTF-8
        return s.encode('cp1251').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError, ValueError):
        return s


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
        fixed_row = (
            row[0],  # id
            row[1],  # time_out
            row[2],  # time_in
            fix_misencoded_russian(row[3]),  # num авто
            fix_misencoded_russian(row[4]),  # ФИО водителя
            fix_misencoded_russian(row[5]),  # маршрут
            row[6],  # auto_id
            row[7],  # route_id
        )
        rows.append(fixed_row)
    conn.close()
    return rows


def get_all_cars():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, num, color, mark, personal_id FROM auto ORDER BY num")
    cars = []
    for row in cur.fetchall():
        fixed_row = (
            row[0],
            fix_misencoded_russian(row[1]),  # num
            fix_misencoded_russian(row[2]),  # color
            fix_misencoded_russian(row[3]),  # mark
            row[4],
        )
        cars.append(fixed_row)
    conn.close()
    return cars


def get_all_drivers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, first_name, last_name, father_name FROM auto_personnel ORDER BY last_name")
    drivers = []
    for row in cur.fetchall():
        fixed_row = (
            row[0],
            fix_misencoded_russian(row[1]),  # first_name
            fix_misencoded_russian(row[2]),  # last_name
            fix_misencoded_russian(row[3]),  # father_name
        )
        drivers.append(fixed_row)
    conn.close()
    return drivers


def get_all_routes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, data FROM routes ORDER BY name")
    routes = []
    for row in cur.fetchall():
        fixed_row = (
            row[0],
            fix_misencoded_russian(row[1]),  # name
            row[2],  # data
        )
        routes.append(fixed_row)
    conn.close()
    return routes


def call_distribute_bonuses(start_date: str, end_date: str, total_bonus: float):
    conn = get_connection()
    cur = conn.cursor()
    cur.callproc('distribute_bonuses', (start_date, end_date, total_bonus))
    results = []
    for row in cur.fetchall():
        fixed_row = (
            row[0],  # driver_id
            fix_misencoded_russian(row[1]),  # first_name
            fix_misencoded_russian(row[2]),  # last_name
            fix_misencoded_russian(row[3]),  # father_name
            row[4],  # completed_routes
            row[5],  # fastest_seconds
            row[6],  # bonus_amount
            row[7],  # bonus_percent
        )
        results.append(fixed_row)
    conn.close()
    return results


def get_routes_avg_time():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            r.name,
            ROUND(AVG(EXTRACT(EPOCH FROM (j.time_in - j.time_out)) / 60), 2) AS avg_minutes
        FROM routes r
        JOIN journal j ON r.id = j.route_id
        WHERE j.time_in IS NOT NULL AND j.time_out IS NOT NULL
        GROUP BY r.id, r.name
        ORDER BY avg_minutes
    """)
    results = []
    for row in cur.fetchall():
        fixed_row = (
            fix_misencoded_russian(row[0]),  # маршрут
            row[1],  # среднее время
        )
        results.append(fixed_row)
    conn.close()
    return results


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
    """Проверка: автомобиль не находится в незавершённом рейсе."""
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
    rows = cur.fetchall()
    conn.close()
    return rows

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
    """Список водителей для выбора при редактировании авто"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, CONCAT(last_name, ' ', first_name, ' ', COALESCE(father_name, '')) FROM auto_personnel ORDER BY last_name")
    rows = cur.fetchall()
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

def get_all_routes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, data FROM routes ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows

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