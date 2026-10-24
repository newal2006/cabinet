"""
CabiNet — школьная платформа для тестов

Автор: Новиков Алексей Валерьевич
Год создания: 2026
Лицензия: All rights reserved

(c) 2026 Новиков Алексей Валерьевич. Все права защищены.
Любое копирование, распространение или изменение
без письменного разрешения автора запрещено.
"""
"""
CabiNet — база данных
"""
import sqlite3
import os
import sys
from datetime import datetime

# Определяем папку, где лежит .exe (или .py)
if getattr(sys, 'frozen', False):
    # Запущено как .exe
    APP_DIR = os.path.dirname(sys.executable)
else:
    # Запущено как .py
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(APP_DIR, 'cabinet.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            access_code TEXT UNIQUE,
            status TEXT DEFAULT 'draft',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            started_at TEXT,
            ended_at TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id INTEGER,
            order_num INTEGER,
            question TEXT NOT NULL,
            options TEXT,
            correct_answer TEXT,
            explanation TEXT,
            qtype TEXT DEFAULT 'single',
            points INTEGER DEFAULT 1,
            FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER,
            lesson_id INTEGER,
            student_name TEXT NOT NULL,
            student_ip TEXT,
            answer TEXT,
            is_correct INTEGER DEFAULT 0,
            points_earned INTEGER DEFAULT 0,
            answered_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS student_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id INTEGER,
            student_name TEXT NOT NULL,
            order_json TEXT,
            finished_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("[DB] База инициализирована:", DB_PATH)


# ==================== УРОКИ ====================

def create_lesson(title):
    conn = get_db()
    cur = conn.cursor()
    code = f"K{datetime.now().strftime('%d%H%M%S')}"
    cur.execute('''INSERT INTO lessons (title, access_code, status) VALUES (?, ?, 'draft')''',
                (title, code))
    conn.commit()
    lid = cur.lastrowid
    conn.close()
    return {'id': lid, 'title': title, 'access_code': code}


def get_all_lessons():
    conn = get_db()
    rows = conn.execute('SELECT * FROM lessons ORDER BY id DESC').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_lesson(lid):
    conn = get_db()
    row = conn.execute('SELECT * FROM lessons WHERE id = ?', (lid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def start_lesson(lid):
    conn = get_db()
    conn.execute('''UPDATE lessons SET status='active', started_at=? WHERE id=?''',
                 (datetime.now().isoformat(), lid))
    conn.commit()
    conn.close()


def finish_lesson(lid):
    conn = get_db()
    conn.execute('''UPDATE lessons SET status='finished', ended_at=? WHERE id=?''',
                 (datetime.now().isoformat(), lid))
    conn.commit()
    conn.close()


def reset_lesson(lid):
    conn = get_db()
    conn.execute('DELETE FROM answers WHERE lesson_id = ?', (lid,))
    conn.execute('DELETE FROM student_progress WHERE lesson_id = ?', (lid,))
    conn.execute('''UPDATE lessons SET status='draft', started_at=NULL, ended_at=NULL WHERE id=?''',
                 (lid,))
    conn.commit()
    conn.close()


def delete_lesson(lid):
    conn = get_db()
    conn.execute('DELETE FROM answers WHERE lesson_id = ?', (lid,))
    conn.execute('DELETE FROM assignments WHERE lesson_id = ?', (lid,))
    conn.execute('DELETE FROM student_progress WHERE lesson_id = ?', (lid,))
    conn.execute('DELETE FROM lessons WHERE id = ?', (lid,))
    conn.commit()
    conn.close()


# ==================== ЗАДАНИЯ ====================

def add_assignment(lesson_id, question, options_json, correct_answer,
                   explanation='', points=1, qtype='single'):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT MAX(order_num) FROM assignments WHERE lesson_id = ?', (lesson_id,))
    row = cur.fetchone()
    next_num = (row[0] or 0) + 1
    cur.execute('''
        INSERT INTO assignments 
        (lesson_id, order_num, question, options, correct_answer, explanation, qtype, points)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (lesson_id, next_num, question, options_json, correct_answer,
          explanation, qtype, points))
    conn.commit()
    a_id = cur.lastrowid
    conn.close()
    return a_id


def get_assignments(lesson_id):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM assignments WHERE lesson_id = ? ORDER BY order_num',
        (lesson_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_assignment(aid):
    conn = get_db()
    conn.execute('DELETE FROM assignments WHERE id = ?', (aid,))
    conn.commit()
    conn.close()


# ==================== ОТВЕТЫ ====================

def save_answer(aid, lid, student_name, student_ip, answer, is_correct, points):
    conn = get_db()
    cur = conn.cursor()
    existing = cur.execute('''SELECT id FROM answers WHERE assignment_id = ? AND student_name = ?''',
                           (aid, student_name)).fetchone()
    if existing:
        conn.close()
        return None
    cur.execute('''
        INSERT INTO answers 
        (assignment_id, lesson_id, student_name, student_ip, answer, is_correct, points_earned)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (aid, lid, student_name, student_ip, answer, 1 if is_correct else 0, points))
    conn.commit()
    a_id = cur.lastrowid
    conn.close()
    return a_id


def get_answers(aid):
    conn = get_db()
    rows = conn.execute('''SELECT * FROM answers WHERE assignment_id = ? ORDER BY answered_at''',
                        (aid,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_lesson_results(lid):
    conn = get_db()
    rows = conn.execute('''
        SELECT 
            student_name,
            student_ip,
            COUNT(*) as answered_count,
            SUM(is_correct) as correct_count,
            SUM(points_earned) as total_points,
            MIN(answered_at) as first_answer
        FROM answers WHERE lesson_id = ?
        GROUP BY student_name
        ORDER BY total_points DESC, first_answer ASC
    ''', (lid,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_progress(lid, student_name, order_json):
    conn = get_db()
    cur = conn.cursor()
    existing = cur.execute('''SELECT id FROM student_progress WHERE lesson_id = ? AND student_name = ?''',
                           (lid, student_name)).fetchone()
    if existing:
        cur.execute('''UPDATE student_progress SET order_json = ? WHERE id = ?''',
                    (order_json, existing['id']))
    else:
        cur.execute('''INSERT INTO student_progress (lesson_id, student_name, order_json)
                       VALUES (?, ?, ?)''', (lid, student_name, order_json))
    conn.commit()
    conn.close()


def mark_finished(lid, student_name):
    conn = get_db()
    conn.execute('''UPDATE student_progress SET finished_at = ? 
                    WHERE lesson_id = ? AND student_name = ?''',
                 (datetime.now().isoformat(), lid, student_name))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    print("[DB] Готово!")