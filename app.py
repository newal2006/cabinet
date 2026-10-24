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
CabiNet — сервер (полная версия)
Один тест = много вопросов. 4 типа вопросов.
"""
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import qrcode
import os
import io
import base64
import socket
import json
import random
from datetime import datetime

from database import (
    init_db, create_lesson, get_all_lessons, get_lesson,
    start_lesson, finish_lesson, reset_lesson, delete_lesson,
    add_assignment, get_assignments, delete_assignment,
    save_answer, get_answers, get_lesson_results,
    save_progress, mark_finished
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cabinet_secret_2026'
socketio = SocketIO(app, cors_allowed_origins='*')

state = {
    'teacher_sid': None,
    'projector_sid': None,
    'students': {},
    'active_lesson_id': None,
    'test_running': False,
}


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def make_qr(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

from flask import send_from_directory

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )
# ==================== СТРАНИЦЫ ====================

@app.route('/')
def index():
    """Главная — учитель с QR-кодом"""
    ip = get_local_ip()
    url = f"http://{ip}:8080/join"
    qr = make_qr(url)
    return render_template('teacher.html', ip=ip, url=url, qr=qr)


@app.route('/join')
def join_page():
    """Вход ученика"""
    return render_template('student_join.html')


@app.route('/lesson')
def lesson_page():
    """Урок ученика"""
    return render_template('student_lesson.html')


@app.route('/manage')
@app.route('/teacher/lessons')
def manage_page():
    """Управление уроками — единый интерфейс"""
    return render_template('teacher_manage.html')


# ==================== API: УРОКИ ====================

@app.route('/api/lessons', methods=['GET'])
def api_get_lessons():
    return jsonify(get_all_lessons())


@app.route('/api/lessons', methods=['POST'])
def api_create_lesson():
    data = request.json
    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({'error': 'Укажите тему урока'}), 400
    lesson = create_lesson(title)
    print(f"[L] Создан урок: {title}")
    return jsonify(lesson)


@app.route('/api/lessons/<int:lid>', methods=['GET'])
def api_get_lesson(lid):
    lesson = get_lesson(lid)
    if not lesson:
        return jsonify({'error': 'Урок не найден'}), 404
    lesson['assignments'] = get_assignments(lid)
    lesson['results'] = get_lesson_results(lid)
    return jsonify(lesson)


@app.route('/api/lessons/<int:lid>', methods=['DELETE'])
def api_delete_lesson(lid):
    delete_lesson(lid)
    if state['active_lesson_id'] == lid:
        state['active_lesson_id'] = None
        state['test_running'] = False
    return jsonify({'ok': True})


@app.route('/api/lessons/<int:lid>/start', methods=['POST'])
def api_start_lesson(lid):
    """Запустить тест — рассылает всем ученикам"""
    assignments = get_assignments(lid)
    if not assignments:
        return jsonify({'error': 'В уроке нет заданий'}), 400

    start_lesson(lid)
    state['active_lesson_id'] = lid
    state['test_running'] = True

    for sid in list(state['students'].keys()):
        send_test_to_student(sid, lid)

    socketio.emit('test_started', {'lesson_id': lid, 'total': len(assignments)})
    print(f"[L] ТЕСТ ЗАПУЩЕН: урок #{lid}, вопросов: {len(assignments)}")
    return jsonify({'ok': True, 'total': len(assignments)})


@app.route('/api/lessons/<int:lid>/finish', methods=['POST'])
def api_finish_lesson(lid):
    finish_lesson(lid)
    if state['active_lesson_id'] == lid:
        state['active_lesson_id'] = None
        state['test_running'] = False
    socketio.emit('test_finished', {'lesson_id': lid})
    print(f"[L] ТЕСТ ЗАВЕРШЁН: урок #{lid}")
    return jsonify({'ok': True})


@app.route('/api/lessons/<int:lid>/reset', methods=['POST'])
def api_reset_lesson(lid):
    reset_lesson(lid)
    if state['active_lesson_id'] == lid:
        state['active_lesson_id'] = None
        state['test_running'] = False
    return jsonify({'ok': True})


def send_test_to_student(sid, lid):
    """Отправить ученику его персональный вариант теста"""
    student = state['students'].get(sid)
    if not student:
        return

    assignments = get_assignments(lid)
    if not assignments:
        return

    order = [a['id'] for a in assignments]
    random.shuffle(order)
    student['order'] = order
    save_progress(lid, student['name'], json.dumps(order))

    by_id = {a['id']: a for a in assignments}
    personal_tasks = []
    for i, aid in enumerate(order, 1):
        a = by_id[aid]
        opts = json.loads(a['options']) if a['options'] else []
        random.shuffle(opts)
        personal_tasks.append({
            'num': i,
            'id': a['id'],
            'question': a['question'],
            'options': opts,
            'qtype': a.get('qtype', 'single')
        })

    socketio.emit('start_test', {
        'lesson_id': lid,
        'tasks': personal_tasks,
        'total': len(personal_tasks)
    }, to=sid)
    print(f"[T] Тест отправлен: {student['name']} ({len(personal_tasks)} вопросов)")


# ==================== API: ЗАДАНИЯ ====================

@app.route('/api/lessons/<int:lid>/assignments', methods=['POST'])
def api_add_assignment(lid):
    data = request.json
    question = (data.get('question') or '').strip()
    options = data.get('options') or []
    correct = data.get('correct') or ''
    explanation = (data.get('explanation') or '').strip()
    points = int(data.get('points') or 1)
    qtype = data.get('qtype', 'single')

    if not question:
        return jsonify({'error': 'Введите вопрос'}), 400
    if qtype in ('single', 'multiple', 'poll') and len(options) < 2:
        return jsonify({'error': 'Нужно минимум 2 варианта'}), 400

    if qtype == 'single':
        if isinstance(correct, list):
            correct = correct[0] if correct else ''
        if correct not in options:
            return jsonify({'error': 'Правильный ответ не найден среди вариантов'}), 400
        correct_str = correct
    elif qtype == 'multiple':
        if not isinstance(correct, list):
            correct = [correct] if correct else []
        correct_str = json.dumps(correct, ensure_ascii=False)
    else:
        correct_str = ''

    a_id = add_assignment(lid, question, json.dumps(options, ensure_ascii=False),
                          correct_str, explanation, points, qtype)
    return jsonify({'id': a_id})


@app.route('/api/assignments/<int:aid>', methods=['DELETE'])
def api_delete_assignment(aid):
    delete_assignment(aid)
    return jsonify({'ok': True})


@app.route('/api/lessons/<int:lid>/import', methods=['POST'])
def api_import_assignments(lid):
    """Импорт заданий из текста"""
    data = request.json
    text = data.get('text', '')
    points = int(data.get('points', 1))

    if not text.strip():
        return jsonify({'error': 'Пустой текст'}), 400

    parsed = parse_assignments_text(text)
    if not parsed:
        return jsonify({'error': 'Не удалось распознать задания'}), 400

    added = 0
    errors = []
    for i, a in enumerate(parsed, 1):
        try:
            add_assignment(lid, a['question'],
                           json.dumps(a['options'], ensure_ascii=False),
                           a['correct'], a.get('explanation', ''),
                           points, a['qtype'])
            added += 1
        except Exception as e:
            errors.append(f"Задание {i}: {str(e)}")

    print(f"[A] Импортировано {added} заданий в урок #{lid}")
    return jsonify({'ok': True, 'added': added, 'errors': errors, 'total': len(parsed)})


def parse_assignments_text(text):
    """
    Формат:
    # Заголовок
    Текст вопроса
    * Правильный ответ (один)
    - Неправильный вариант
    + Правильный ответ (несколько)
    ? — открытый ответ
    ~ Вариант для опроса
    ! Пояснение
    """
    lines = text.split('\n')
    assignments = []
    current_q = None
    current_options = []
    current_correct_single = None
    current_correct_multiple = []
    current_explanation = ''
    current_type = 'single'

    def finish():
        nonlocal current_q, current_options, current_correct_single
        nonlocal current_correct_multiple, current_explanation, current_type
        if current_q:
            if current_type == 'open':
                assignments.append({
                    'question': current_q,
                    'options': [],
                    'correct': '',
                    'explanation': current_explanation,
                    'qtype': 'open'
                })
            elif current_type == 'poll':
                assignments.append({
                    'question': current_q,
                    'options': current_options[:],
                    'correct': '',
                    'explanation': current_explanation,
                    'qtype': 'poll'
                })
            elif current_type == 'multiple':
                seen = set()
                uniq_multiple = []
                for x in current_correct_multiple:
                    if x not in seen:
                        seen.add(x)
                        uniq_multiple.append(x)
                all_opts = uniq_multiple + [o for o in current_options if o not in uniq_multiple]
                assignments.append({
                    'question': current_q,
                    'options': all_opts,
                    'correct': json.dumps(uniq_multiple, ensure_ascii=False),
                    'explanation': current_explanation,
                    'qtype': 'multiple'
                })
            else:  # single
                if current_correct_single:
                    opts = current_options[:]
                    if current_correct_single not in opts:
                        opts.append(current_correct_single)
                    assignments.append({
                        'question': current_q,
                        'options': opts,
                        'correct': current_correct_single,
                        'explanation': current_explanation,
                        'qtype': 'single'
                    })
        current_q = None
        current_options = []
        current_correct_single = None
        current_correct_multiple = []
        current_explanation = ''
        current_type = 'single'

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith('//'):
            continue
        if line.startswith('! '):
            current_explanation = line[2:].strip()
            continue
        if line.startswith('# '):
            finish()
            continue
        if line.startswith('* '):
            val = line[2:].strip()
            if val:
                current_correct_single = val
                if val not in current_options:
                    current_options.append(val)
            continue
        if line.strip() == '*':
            current_type = 'open'
            continue
        if line.startswith('+ '):
            val = line[2:].strip()
            if val:
                current_type = 'multiple'
                current_correct_multiple.append(val)
                if val not in current_options:
                    current_options.append(val)
            continue
        if line.strip() == '?':
            current_type = 'open'
            continue
        if line.startswith('~ '):
            val = line[2:].strip()
            if val:
                if current_type == 'single' and current_correct_single is None and not current_correct_multiple:
                    current_type = 'poll'
                current_options.append(val)
            continue
        if line.startswith('- '):
            val = line[2:].strip()
            if val:
                current_options.append(val)
            continue
        if current_q is None:
            current_q = line.strip()
        else:
            current_q += ' ' + line.strip()

    finish()

    valid = []
    for a in assignments:
        if not a['question']:
            continue
        if a['qtype'] in ('single', 'multiple', 'poll') and len(a['options']) < 2:
            continue
        valid.append(a)
    return valid


# ==================== API: РЕЗУЛЬТАТЫ ====================

@app.route('/api/assignments/<int:aid>/answers', methods=['GET'])
def api_get_answers(aid):
    return jsonify(get_answers(aid))


@app.route('/api/lessons/<int:lid>/results', methods=['GET'])
def api_get_results(lid):
    return jsonify(get_lesson_results(lid))

# ==================== API: ОТЧЁТЫ ====================


# ==================== API: УЧЕНИКИ ====================

@app.route('/api/students', methods=['GET'])
def api_get_students():
    return jsonify({
        'students': list(state['students'].values()),
        'count': len(state['students'])
    })


@app.route('/api/students/<sid>/kick', methods=['POST'])
def api_kick_student(sid):
    if sid in state['students']:
        student = state['students'].pop(sid)
        socketio.emit('kicked', {'reason': 'Учитель удалил вас из урока'}, to=sid)
        if state['teacher_sid']:
            socketio.emit('student_left', student, to=state['teacher_sid'])
        return jsonify({'ok': True})
    return jsonify({'error': 'Ученик не найден'}), 404


@app.route('/api/students/<sid>/rename', methods=['POST'])
def api_rename_student(sid):
    data = request.json
    new_name = (data.get('name') or '').strip()
    if not new_name:
        return jsonify({'error': 'Пустое имя'}), 400
    if sid not in state['students']:
        return jsonify({'error': 'Ученик не найден'}), 404
    old = state['students'][sid]['name']
    state['students'][sid]['name'] = new_name
    if state['teacher_sid']:
        socketio.emit('student_renamed', {
            'sid': sid, 'old_name': old, 'new_name': new_name
        }, to=state['teacher_sid'])
    return jsonify({'ok': True})


@app.route('/api/students/kick_all', methods=['POST'])
def api_kick_all():
    count = len(state['students'])
    for sid in list(state['students'].keys()):
        socketio.emit('kicked', {'reason': 'Учитель сбросил список'}, to=sid)
    state['students'].clear()
    if state['teacher_sid']:
        socketio.emit('all_students_kicked', to=state['teacher_sid'])
    return jsonify({'ok': True, 'count': count})


# ==================== SOCKET.IO ====================

@socketio.on('connect')
def on_connect():
    print(f"[+] Подключение {request.sid} от {request.remote_addr}")


@socketio.on('register_teacher')
def on_register_teacher():
    state['teacher_sid'] = request.sid
    emit('teacher_registered', {'ok': True})


@socketio.on('register_projector')
def on_register_projector(data):
    state['projector_sid'] = request.sid
    emit('projector_ok', {'ok': True})
    print(f"[P] Проектор подключён")


@socketio.on('register_student')
def on_register_student(data):
    sid = request.sid
    ip = request.remote_addr
    name = (data.get('name') or '').strip()

    if not name:
        emit('register_error', {'error': 'Введите имя'})
        return

    for old_sid in list(state['students'].keys()):
        if state['students'][old_sid]['name'].lower() == name.lower():
            del state['students'][old_sid]

    student = {
        'sid': sid,
        'name': name,
        'ip': ip,
        'joined_at': datetime.now().strftime('%H:%M:%S')
    }
    state['students'][sid] = student

    emit('register_ok', {'name': name})

    if state['teacher_sid']:
        emit('student_joined', student, to=state['teacher_sid'])

    if state['test_running'] and state['active_lesson_id']:
        send_test_to_student(sid, state['active_lesson_id'])

    print(f"[S] Ученик: {name} (IP {ip})")


@socketio.on('submit_answer')
def on_submit_answer(data):
    sid = request.sid
    student = state['students'].get(sid)
    if not student:
        emit('answer_rejected', {'reason': 'Вы не в уроке'})
        return

    aid = data.get('assignment_id')
    answer_raw = data.get('answer')
    lesson_id = state['active_lesson_id']

    if not lesson_id:
        emit('answer_rejected', {'reason': 'Тест не запущен'})
        return

    assignment = None
    for a in get_assignments(lesson_id):
        if a['id'] == aid:
            assignment = a
            break
    if not assignment:
        emit('answer_rejected', {'reason': 'Задание не найдено'})
        return

    qtype = assignment.get('qtype', 'single')
    is_correct = False
    points = 0
    answer_for_save = ''

    if qtype == 'single':
        answer_for_save = str(answer_raw).strip()
        is_correct = (answer_for_save == assignment['correct_answer'])
        points = assignment['points'] if is_correct else 0

    elif qtype == 'multiple':
        if not isinstance(answer_raw, list):
            answer_raw = []
        try:
            correct_list = json.loads(assignment['correct_answer'])
        except Exception:
            correct_list = []
        if set(answer_raw) == set(correct_list):
            is_correct = True
        points = assignment['points'] if is_correct else 0
        answer_for_save = json.dumps(answer_raw, ensure_ascii=False)

    elif qtype == 'open':
        answer_for_save = str(answer_raw).strip()
        is_correct = False
        points = 0

    elif qtype == 'poll':
        answer_for_save = str(answer_raw).strip()
        is_correct = False
        points = 0

    saved = save_answer(aid, lesson_id, student['name'],
                        student['ip'], answer_for_save, is_correct, points)

    emit('answer_saved', {
        'ok': True,
        'already_saved': saved is None,
        'is_correct': is_correct,
        'qtype': qtype
    })

    if saved is not None and state['teacher_sid']:
        emit('new_answer', {
            'assignment_id': aid,
            'student_name': student['name'],
            'student_ip': student['ip'],
            'answer': answer_for_save,
            'is_correct': is_correct,
            'points': points,
            'qtype': qtype,
            'answered_at': datetime.now().strftime('%H:%M:%S')
        }, to=state['teacher_sid'])

        if state['projector_sid']:
            socketio.emit('new_answer', {'assignment_id': aid}, to=state['projector_sid'])

    print(f"[A] Ответ: {student['name']} [{qtype}] → {answer_for_save[:40]}")


@socketio.on('finish_test')
def on_finish_test():
    sid = request.sid
    student = state['students'].get(sid)
    if not student or not state['active_lesson_id']:
        return
    mark_finished(state['active_lesson_id'], student['name'])
    results = get_lesson_results(state['active_lesson_id'])
    me = next((r for r in results if r['student_name'] == student['name']), None)
    if me:
        emit('your_result', {
            'correct': me['correct_count'],
            'total': me['answered_count'],
            'points': me['total_points']
        })


@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    if sid in state['students']:
        student = state['students'].pop(sid)
        if state['teacher_sid']:
            emit('student_left', student, to=state['teacher_sid'])
    if state['teacher_sid'] == sid:
        state['teacher_sid'] = None
    if state['projector_sid'] == sid:
        state['projector_sid'] = None


# ==================== ЗАПУСК ====================

if __name__ == '__main__':
    init_db()
    ip = get_local_ip()
    print()
    print("=" * 60)
    print("  CabiNet — сервер запущен")
    print("=" * 60)
    print(f"  Управление:   http://localhost:8080/manage")
    print(f"  Ученики:      http://{ip}:8080/join")
    print("=" * 60)
    print()

    # Автооткрытие браузера
    import webbrowser
    import threading
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open('http://localhost:8080')
    threading.Thread(target=open_browser, daemon=True).start()

    socketio.run(app, host='0.0.0.0', port=8080, debug=False,
                 allow_unsafe_werkzeug=True)