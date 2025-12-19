import csv
import re
import json
from typing import List, Dict
from checksum import calculate_checksum, serialize_result


def read_csv(filename: str) -> List[Dict]:
    data = []
    with open(filename, 'r', encoding='utf-16') as f:  
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            data.append(row)
    return data


def validate_email(email: str) -> bool:
    """
    Проверяет валидность email.
    Формат: латинские буквы, цифры, точки, @, поддомены.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_http_status(msg: str) -> bool:
    """
    Проверяет статус HTTP: три цифры, пробел, текст.
    Пример: "200 OK", "226 IM Used"
    """
    pattern = r'^\d{3}\s[A-Za-z\s]+$'
    return bool(re.match(pattern, msg))


def validate_snils(snils: str) -> bool:
    """
    Проверяет СНИЛС: 11 цифр подряд.
    """
    pattern = r'^\d{11}$'
    return bool(re.match(pattern, snils))


def validate_passport(passport: str) -> bool:
    """
    Проверяет паспорт: XX XX XXXXXX (2 цифры, пробел, 2 цифры, пробел, 6 цифр).
    """
    pattern = r'^\d{2}\s\d{2}\s\d{6}$'
    return bool(re.match(pattern, passport))


def validate_ip_v4(ip: str) -> bool:
    """
    Проверяет IPv4 адрес.
    """
    pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return bool(re.match(pattern, ip))


def validate_longitude(longitude: str) -> bool:
    """
    Проверяет долготу: число от -180 до 180, может быть дробным.
    """
    try:
        lon = float(longitude)
        return -180.0 <= lon <= 180.0
    except ValueError:
        return False


def validate_hex_color(color: str) -> bool:
    """
    Проверяет цвет в формате HEX: # + 6 шестнадцатеричных символов.
    """
    pattern = r'^#[0-9a-fA-F]{6}$'
    return bool(re.match(pattern, color))


def validate_isbn(isbn: str) -> bool:
    """
    Проверяет ISBN (13 или 10 цифр с дефисами).
    Пример: "1-02150-692-9" (10 цифр) или "978-1-61879-098-1" (13 цифр)
    """
    digits = re.sub(r'[^0-9]', '', isbn)
    if len(digits) == 10:
        pattern = r'^\d{1,5}-\d{1,7}-\d{1,7}-[\dX]$'
    elif len(digits) == 13:
        pattern = r'^\d{3}-\d{1,5}-\d{1,7}-\d{1,7}-\d$'
    else:
        return False
    return bool(re.match(pattern, isbn))


def validate_locale_code(locale: str) -> bool:
    """
    Проверяет код локали: формат "язык-регион" или только "язык".
    Пример: "es-uy", "xh", "ar-eg"
    """
    pattern = r'^[a-z]{2,3}(-[a-z]{2,3})?$'
    return bool(re.match(pattern, locale))


def validate_time(time_str: str) -> bool:
    """
    Проверяет время: HH:MM:SS.ffffff (от 00:00:00 до 23:59:59.999999)
    """
    pattern = r'^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)\.\d{6}$'
    if not re.match(pattern, time_str):
        return False
    return True


VALIDATORS = {
    'email': validate_email,
    'http_status_message': validate_http_status,
    'snils': validate_snils,
    'passport': validate_passport,
    'ip_v4': validate_ip_v4,
    'longitude': validate_longitude,
    'hex_color': validate_hex_color,
    'isbn': validate_isbn,
    'locale_code': validate_locale_code,
    'time': validate_time,
}


def validate_row(row: Dict) -> bool:
    """
    Проверяет всю строку.
    """
    for field, validator in VALIDATORS.items():
        if field in row:
            value = row[field].strip('"')  # Убираем кавычки
            if not validator(value):
                return False
    return True


def main():
    csv_filename = '25.csv'  
    data = read_csv(csv_filename)
    invalid_rows = []

    for index, row in enumerate(data):
        if not validate_row(row):
            invalid_rows.append(index)  

    checksum = calculate_checksum(invalid_rows)
    print(f'Найдено невалидных строк: {len(invalid_rows)}')
    print(f'Контрольная сумма: {checksum}')

    # Сохраняем результат
    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump({'variant': 25, 'checksum': checksum}, f, ensure_ascii=False, indent=2)
    print('Результат записан в result.json')


if __name__ == '__main__':
    main()