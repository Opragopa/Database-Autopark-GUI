import re

# Разрешённые буквы для российских номеров (только совпадающие с латиницей)
RUSSIAN_PLATE_LETTERS = "АВЕКМНОРСТУХ"

def validate_russian_plate(plate: str) -> bool:
    """Проверяет соответствие формату российского госномера: А123БВ"""
    if not plate:
        return False
    plate = plate.strip().upper()
    pattern = f"^[{RUSSIAN_PLATE_LETTERS}][0-9]{{3}}[{RUSSIAN_PLATE_LETTERS}]{{2}}$"
    return bool(re.fullmatch(pattern, plate))

def validate_name_part(name: str) -> bool:
    """Проверяет, что ФИО содержит только кириллицу, пробелы и дефисы, минимум 2 символа"""
    if not name:
        return False
    return bool(re.fullmatch(r"[А-ЯЁа-яё\- ]{2,}", name.strip()))

# Список реальных городов РФ (для маршрутов)
RUSSIAN_CITIES = {
    "Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань",
    "Нижний Новгород", "Челябинск", "Самара", "Омск", "Ростов-на-Дону",
    "Уфа", "Красноярск", "Воронеж", "Пермь", "Волгоград", "Сочи", "Геленджик",
    "Магадан", "Владивосток", "Иркутск", "Калининград", "Севастополь", "Курск",
    "Тула", "Ярославль", "Набережные Челны", "Тольятти", "Краснодар"
}

def validate_route_name(name: str) -> bool:
    """Проверяет маршрут: либо 'Город-Город', либо простое название"""
    name = name.strip()
    if not name or len(name) < 2:
        return False
    # Замена длинных/коротких дефисов на обычный
    name = name.replace("–", "-").replace("—", "-")
    if "-" in name:
        parts = [p.strip() for p in name.split("-") if p.strip()]
        if len(parts) == 2:
            return parts[0] in RUSSIAN_CITIES and parts[1] in RUSSIAN_CITIES
    return True