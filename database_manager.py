import sqlite3
import math

from translations import translate_text

from functools import partial

from datetime import datetime

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS students \
                (student_id INT UNIQUE NOT NULL, \
                student_fullname TEXT, \
                student_level INT, \
                student_group_level INT, \
                student_lang INT)")

cursor.execute("CREATE TABLE IF NOT EXISTS students_groups \
                (student_id INT, \
                group_id INT, \
                FOREIGN KEY (student_id) REFERENCES students (student_id), \
                FOREIGN KEY (group_id) REFERENCES groups (group_id))")

cursor.execute("CREATE TABLE IF NOT EXISTS admins \
                (admin_id INT UNIQUE NOT NULL, \
                admin_fullname TEXT UNIQUE NOT NULL)")

cursor.execute("CREATE TABLE IF NOT EXISTS teachers \
                (teacher_id INT UNIQUE NOT NULL, \
                teacher_fullname TEXT, \
                teacher_lang INT)")

cursor.execute("CREATE TABLE IF NOT EXISTS admin_pay_card \
                (admin_id INT, \
                card_number INT, \
                price INT not null default 0, \
                FOREIGN KEY (admin_id) REFERENCES admins(admin_id))")

cursor.execute("CREATE TABLE IF NOT EXISTS groups \
                (group_id INTEGER PRIMARY KEY, \
                teacher_id INT NOT NULL, \
                FOREIGN KEY (teacher_id) REFERENCES teachers (teacher_id))")

cursor.execute("CREATE TABLE IF NOT EXISTS payments \
                (payment_id INTEGER PRIMARY KEY, \
                student_id INT, \
                group_id   INT, \
                capacity   INT, \
                payment_date date not null default null, \
                payment_check BOOL NOT NULL DEFAULT FALSE, \
                admin_check   BOOL NOT NULL DEFAULT FALSE, \
                FOREIGN KEY (student_id) REFERENCES students(student_id), \
                FOREIGN KEY (group_id) REFERENCES groups(group_id))")

cursor.execute("CREATE TABLE IF NOT EXISTS levels \
                (level INT NOT NULL, \
                teacher_id INT NOT NULL, \
                group_id INT NOT NULL, \
                FOREIGN KEY (group_id) REFERENCES groups (group_id)\
                FOREIGN KEY (teacher_id) REFERENCES teachers (teacher_id))")

cursor.execute("CREATE TABLE IF NOT EXISTS views \
                (view INT NOT NULL, \
                teacher_id INT NOT NULL, \
                group_id INT NOT NULL, \
                FOREIGN KEY (teacher_id) REFERENCES teachers (teacher_id), \
                FOREIGN KEY (group_id) REFERENCES groups (group_id))")

def add_student(id: int) -> None:
    cursor.execute("INSERT OR IGNORE INTO students (student_id) VALUES (?)", (id, ))
    conn.commit()

def add_student_fullname(id: int, fullname: str) -> None:
    cursor.execute("UPDATE students SET student_fullname = ? WHERE student_id = ?", (fullname, id))
    conn.commit()

def add_teacher(id: int) -> None:
    cursor.execute("INSERT OR IGNORE INTO teachers (teacher_id) VALUES (?)", (id, ))
    conn.commit()

def add_teacher_fullname(id: int, fullname: str) -> None:
    cursor.execute("UPDATE teachers SET teacher_fullname = ? WHERE teacher_id = ?", (fullname, id))
    conn.commit()

def add_price(id: int, price: int) -> None:
    cursor.execute("UPDATE admin_pay_card SET price = ? WHERE admin_id = ?", (price, id))
    conn.commit()

def add_admin(id: int, fullname: str) -> None:
    cursor.execute("INSERT OR IGNORE INTO admins (admin_id, admin_fullname) VALUES (?, ?)", (id, fullname,))
    conn.commit()

def add_levels_in_group(id: int, levels: [int]) -> None: # type: ignore
    cursor.execute("INSERT INTO groups (teacher_id) VALUES (?)", (id,))
    
    last_group_id = cursor.lastrowid
    
    for level in levels:
        cursor.execute("INSERT INTO views (view, teacher_id, group_id) VALUES (?, ?, ?)", 
                        (level, id, last_group_id))
        conn.commit()

def add_student_group_view(id: int, group_view: int) -> None:
    cursor.execute("UPDATE students SET student_group_level = ? WHERE student_id = ?", (group_view, id, ))
    conn.commit()

def add_student_group(id: int, group_id: int) -> None:
    cursor.execute("INSERT OR IGNORE INTO students_groups (student_id, group_id) VALUES (?, ?)", (id, group_id, ))
    conn.commit()

    cursor.execute("INSERT OR IGNORE INTO payments (student_id, group_id, capacity) VALUES (?, ?, ?)", (id, group_id, 0, ))
    conn.commit()

def add_user_lang(id: int, lang: str) -> None:
    lang_conversion = {
        'ru': 1,
        'en': 2,
        'pl': 3,
        'uk': 4
    }

    index = lang_conversion[lang]
    print(id)

    print(check_student(id))

    print(check_teacher(id))

    if check_student(id) == True:
        print(index)
        cursor.execute("UPDATE students SET student_lang = ? WHERE student_id = ?", (index, id, ))
    elif check_teacher(id) == True:
        print(index)
        cursor.execute("UPDATE teachers SET teacher_lang = ? WHERE teacher_id = ?", (index, id, ))

    conn.commit()

def add_student_level(id: int, level: int, view: int) -> None:
    cursor.execute("UPDATE students SET student_level = ? WHERE student_id = ?", (view, id))
    conn.commit()

def add_admin_card(id: int, card_number: int) -> None:
    cursor.execute("INSERT INTO admin_pay_card (admin_id, card_number) VALUES (?, ?)", (id, card_number))
    conn.commit()

def add_group_level(id: int, level: int) -> None:
    cursor.execute("SELECT * FROM teachers WHERE teacher_id = ?", (id,))
    teacher = cursor.fetchone()

    if teacher is not None:
        cursor.execute("SELECT MAX(group_id) FROM groups WHERE teacher_id = ?", (teacher[0],))

        last_group_id = cursor.fetchone()[0]

        cursor.execute("INSERT INTO levels (level, teacher_id, group_id) VALUES (?, ?, ?)", (level, teacher[0], last_group_id))
        conn.commit()

def add_pay_user(id: int, group_id: int, choose: str) -> None:
    if choose == 'one':
        cursor.execute("INSERT INTO payments (student_id, group_id, capacity, payment_date, payment_check, admin_check) VALUES (?,?,?,?,?,?)", (id, group_id, 1, datetime.now(), True, True))
    elif choose == 'all':
        cursor.execute("INSERT INTO payments (student_id, group_id, capacity, payment_date, payment_check, admin_check) VALUES (?,?,?,?,?,?)", (id, group_id, 8, datetime.now(), True, True))

def get_lang(id: int) -> int:
    cursor.execute("SELECT teacher_lang FROM teachers WHERE teacher_id = ?", (id,))
    result = cursor.fetchone()
    if result is not None:
        return result[0]
    else:
        cursor.execute("SELECT student_lang FROM students WHERE student_id = ?", (id,))
        result = cursor.fetchone()
        if result is not None:
            return result[0]
    
    return 2

def get_all_teachers():
    cursor.execute("SELECT teacher_fullname, teacher_id FROM teachers")

    result = cursor.fetchall()

    return result

def get_views() -> []: # type: ignore
    cursor.execute("SELECT DISTINCT level FROM levels")
    result = cursor.fetchall()
    return [row[0] for row in result]

def get_views_by_level(level: int):
    cursor.execute("SELECT g.group_id, GROUP_CONCAT(v.view, ', ') AS views "
                    "FROM groups g "
                    "JOIN levels l ON g.group_id = l.group_id "
                    "JOIN views v ON g.group_id = v.group_id "
                    "WHERE l.level = ? "
                    "GROUP BY g.group_id", (level,))
    result = cursor.fetchall()
    return result

def delete_account(id: int) -> None:
    with conn:
        cursor = conn.cursor()

        cursor.execute("DELETE FROM students_groups WHERE student_id = ?", (id,))

        cursor.execute("DELETE FROM students WHERE student_id = ?", (id,))

        cursor.close()

def delete_teacher(id: int) -> bool:
    with conn:
        cursor.execute("SELECT COUNT(*) FROM groups WHERE teacher_id = ?", (id,))
        result = cursor.fetchone()
        group_count = result[0]
        
        cursor.execute("SELECT COUNT(*) FROM students_groups WHERE group_id IN (SELECT group_id FROM groups WHERE teacher_id = ?)", (id,))
        result = cursor.fetchone()
        student_count = result[0]
        
        if group_count == 0 and student_count == 0:
            cursor.execute("DELETE FROM teachers WHERE teacher_id = ?", (id,))
            cursor.execute("DELETE FROM groups WHERE teacher_id = ?", (id,))
            cursor.execute("DELETE FROM levels WHERE group_id IN (SELECT group_id FROM groups WHERE teacher_id = ?)", (id,))
            cursor.execute("DELETE FROM views WHERE group_id IN (SELECT group_id FROM groups WHERE teacher_id = ?)", (id,))
            cursor.execute("DELETE FROM students_groups WHERE group_id IN (SELECT group_id FROM groups WHERE teacher_id = ?)", (id,))
            cursor.execute("DELETE FROM students WHERE student_id IN (SELECT student_id FROM students_groups WHERE group_id IN (SELECT group_id FROM groups WHERE teacher_id = ?))", (id,))
            cursor.execute("DELETE FROM payments WHERE student_id IN (SELECT student_id FROM students_groups WHERE group_id IN (SELECT group_id FROM groups WHERE teacher_id = ?))", (id,))
            return True
        
        return False

def delete_group(id: int) -> None:
    with conn:
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM students_groups WHERE group_id = ?", (id,))

        cursor.execute("DELETE FROM views WHERE group_id = ?", (id,))

        cursor.execute("DELETE FROM levels WHERE group_id = ?", (id,))

        cursor.execute("DELETE FROM groups WHERE group_id = ?", (id,))

        cursor.close()

def get_teacher_groups(id: int) -> []: # type: ignore
    cursor.execute("SELECT teachers.teacher_fullname, levels.level, views.view, groups.group_id \
                    FROM teachers \
                    JOIN groups ON teachers.teacher_id = groups.teacher_id \
                    JOIN levels ON groups.group_id = levels.group_id \
                    JOIN (SELECT group_id, GROUP_CONCAT(view) AS view \
                        FROM views \
                        GROUP BY group_id) AS views ON groups.group_id = views.group_id \
                    WHERE teachers.teacher_id = ?",
                (id,))

    return cursor.fetchall()

def get_student_groups(student_id: int) -> []: # type: ignore
    cursor.execute("SELECT s.student_fullname, l.level, GROUP_CONCAT(v.view), g.group_id "
                    "FROM students s "
                    "JOIN students_groups sg ON s.student_id = sg.student_id "
                    "JOIN groups g ON sg.group_id = g.group_id "
                    "JOIN views v ON g.group_id = v.group_id "
                    "JOIN levels l ON g.group_id = l.group_id "
                    "WHERE s.student_id = ? "
                    "GROUP BY s.student_fullname, l.level", (student_id,))
    result = cursor.fetchall()
    return result

def get_group_document_from_student(group_id: int) -> []: # type: ignore
    cursor.execute("SELECT teacher_id FROM groups WHERE group_id = ?", (group_id,))
    result = cursor.fetchone()
    print(result)
    return result

def get_group_document_from_teacher(group_id: int) -> []: # type: ignore
    cursor.execute("SELECT student_id FROM students_groups WHERE group_id = ?", (group_id, ))
    result = cursor.fetchall()
    print(result)
    return result

def get_student_account(id: int, lang) -> str:
    group_conversion = {
        3: "Групповое",
        2: "Парное",
        1: "Индивидуальное"
    }

    level_conversion = {
        6: "C1",
        5: "C2",
        4: "B1",
        3: "B2",
        2: "A1",
        1: "A2",
        0: "Новичок"
    }

    data = get_student_groups(id)
    
    if len(data) > 0:
        student_name = data[0][0]
        groups = []

        with conn:
            for row in data:
                views_str = row[2]
                views = [int(view) for view in views_str.split(",")]
                converted_views = [level_conversion[view] for view in views]
                group = group_conversion[row[1]]
                
                group_info = f"Id {row[-1]}: {translate_text('Занятие:', lang)} {translate_text(group, lang)}\n    {translate_text('Уровни:', lang)} {', '.join(converted_views)}\n"
                groups.append(group_info)

        result = f"{translate_text('ФИО студента:', lang)} {student_name}\n{translate_text('Группы:', lang)}\n{''.join(groups)}"
        return result
    else:
        return translate_text("В данный момент студент не состоит ни в одной группе.", lang)
    
def get_user_name(id: int) -> str:
    cursor.execute("SELECT student_fullname FROM students WHERE student_id = ?", (id, ))

    result = cursor.fetchone()

    return result[0]
    
def get_card_number() -> int:
    cursor.execute("SELECT * FROM admin_pay_card")

    result = cursor.fetchone()

    return result[0], int(result[1]), result[2]

def get_admin_account(id: int, lang) -> str:
    cursor.execute("SELECT a.admin_fullname, p.card_number, p.price FROM admins as a INNER JOIN admin_pay_card AS p ON a.admin_id = p.admin_id WHERE a.admin_id = ?", (id, ))

    result = cursor.fetchone()

    if result is not None:
        return f"Name: {result[0]}\nCard number: {result[1]}\nPrice: {result[2]}"

def get_teacher_account(id: int, lang) -> str:
    translate_function = partial(translate_text, lang=lang)

    group_conversion = {
        3: "Групповое",
        2: "Парное",
        1: "Индивидуальное"
    }

    level_conversion = {
        6: "C1",
        5: "C2",
        4: "B1",
        3: "B2",
        2: "A1",
        1: "A2",
        0: "Новичок"
    }
    
    data = get_teacher_groups(id)

    if len(data) > 0:
        teacher_name = data[0][0]
        groups = []

        with conn:
            for row in data:
                group = group_conversion[row[1]]
                levels = []

                views = row[2].split(", ")
                for view in views:
                    digits = view.split(",")
                    for digit in digits:
                        try:
                            digit_int = int(digit.strip())
                            level = level_conversion[digit_int]
                            levels.append(level)
                        except ValueError:
                            levels.append(f"{translate_text('Некорректное значение:', lang)} {digit.strip()}")

                group_info = f"Id {row[-1]}: {translate_text(group, lang)} {translate_text('занятие', lang)}\n    {translate_text('Уровень:', lang)} {' '.join(map(translate_function, levels))}\n"
                groups.append(group_info)

        translate_groups = map(translate_function, groups)
        result = f"{translate_text('ФИО преподавателя:', lang)} {teacher_name}\n{translate_text('Группы:', lang)}\n{''.join(translate_groups)}"
        return result
    else:
        return translate_text("В данный момент у вас нет групп.", lang)

def check_student(id: int) -> bool:
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (id,))
    data = cursor.fetchone()
    if data is not None:
        return True
    
    return False

def check_teacher(id: int) -> bool:
    cursor.execute("SELECT * FROM teachers WHERE teacher_id = ?", (id,))
    data = cursor.fetchone()
    if data is not None:
        return True
    
    return False

def check_admin(id: int) -> bool:
    cursor.execute("SELECT * FROM admins WHERE admin_id = ?", (id,))
    data = cursor.fetchone()
    if data is not None:
        return True
    
    return False

def get_payload_check(student_id: int, group_id: int) -> bool:
    cursor.execute("SELECT payment_check FROM payments WHERE student_id = ? AND group_id = ?", (student_id, group_id, ))
    data = cursor.fetchone()

    if data is None:
        return True
    
    return data[0]

def get_group_count(id: int) -> list:
    cursor.execute("SELECT * FROM groups WHERE group_id = ?", (id,))
    data = cursor.fetchall()
    result = list(data)
    return result

def get_groups_id(id: int) -> list:
    cursor.execute("SELECT DISTINCT g.group_id \
                    FROM groups AS g \
                    INNER JOIN teachers AS t ON t.teacher_id = g.teacher_id \
                    INNER JOIN levels AS l ON l.group_id = g.group_id \
                    INNER JOIN views AS v ON v.group_id = g.group_id \
                    INNER JOIN students AS s ON s.student_level = v.view \
                    WHERE s.student_id = ?", (id,))
    
    data = cursor.fetchall()
    result = list(data)
    print(result)
    return result
    