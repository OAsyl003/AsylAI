import csv
import os

# Глобальные контейнеры для данных
CAR_ISSUES: list[dict] = []
STEP_BY_STEP: list[dict] = []


def _load_data():
    base = os.path.dirname(__file__)
    data_dir = os.path.normpath(os.path.join(base, "..", "data"))

    # Загрузка car_issues.csv
    car_path = os.path.join(data_dir, "car_issues.csv")
    with open(car_path, encoding="utf-8") as f:
        raw_lines = [line.strip() for line in f if line.strip()]
    # Первый элемент — заголовок
    header_line = raw_lines[0]
    if header_line.startswith('"') and header_line.endswith('"'):
        header_line = header_line[1:-1]
    reader = csv.reader([header_line])
    car_headers = next(reader)

    for raw_line in raw_lines[1:]:
        line = raw_line
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        row = next(csv.reader([line]))
        # Формируем словарь с дефолтными пустыми строками для отсутствующих колонок
        entry = {car_headers[i]: row[i] if i < len(row) else "" for i in range(len(car_headers))}
        entry["Brand"] = entry.get("Brand", "") or ""
        entry["Symptom"] = entry.get("Symptom", "") or ""
        entry["Fault"] = entry.get("Fault", "") or ""
        entry["Recommendation"] = entry.get("Recommendation", "") or ""
        try:
            entry["Generation"] = int(entry.get("Generation", 0))
        except ValueError:
            entry["Generation"] = 0
        CAR_ISSUES.append(entry)

    # Загрузка step_by_step.csv
    step_path = os.path.join(data_dir, "step_by_step.csv")
    with open(step_path, encoding="utf-8") as f:
        raw_lines = [line.strip() for line in f if line.strip()]
    header_line = raw_lines[0]
    if header_line.startswith('"') and header_line.endswith('"'):
        header_line = header_line[1:-1]
    reader = csv.reader([header_line])
    step_headers = next(reader)

    for raw_line in raw_lines[1:]:
        line = raw_line
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        row = next(csv.reader([line]))
        entry = {step_headers[i]: row[i] if i < len(row) else "" for i in range(len(step_headers))}
        # Переименовываем Vehicle в Brand для консистенции
        entry["Brand"] = entry.get("Vehicle", "") or entry.get("Brand", "") or ""
        entry["Fault"] = entry.get("Fault", "") or ""
        entry["How_to_Fix"] = (entry.get("How_to_Fix", "") or "").rstrip('"')
        try:
            entry["Generation"] = int(entry.get("Generation", 0))
        except ValueError:
            entry["Generation"] = 0
        STEP_BY_STEP.append(entry)


def map_year_to_generation(year: int) -> int | None:
    if 2001 <= year <= 2002:
        return 1
    if 2003 <= year <= 2006:
        return 2
    if 2007 <= year <= 2011:
        return 3
    if 2012 <= year <= 2017:
        return 4
    if 2018 <= year <= 2023:
        return 5
    return None


def find_issue(brand: str, symptom: str, year: int) -> tuple[str | None, str | None, str | None]:
    if not (brand and year and symptom):
        return None, None, None

    gen = map_year_to_generation(year)
    if gen is None:
        return None, None, None

    lower_brand = brand.lower()
    lower_symptom = symptom.lower()

    # Поиск неисправности и рекомендации
    fault = None
    rec = None
    for entry in CAR_ISSUES:
        b = str(entry.get("Brand", "")).lower()
        s = str(entry.get("Symptom", "")).lower()
        if b.startswith(lower_brand) and entry.get("Generation") == gen and lower_symptom in s:
            fault = entry.get("Fault")
            rec = entry.get("Recommendation")
            break

    if not fault:
        return None, None, None

    # Поиск пошаговой инструкции
    how_to_fix = None
    for step in STEP_BY_STEP:
        b = str(step.get("Brand", "")).lower()
        f = step.get("Fault", "")
        if b.startswith(lower_brand) and f == fault and step.get("Generation") == gen:
            how_to_fix = step.get("How_to_Fix")
            break

    return fault, rec, how_to_fix


# Загружаем данные при импорте модуля
_load_data()