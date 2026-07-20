from flask import Flask, render_template, request, redirect, url_for, session
import os
import time

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# Archivos de base de datos
USERS_FILE = 'users.txt'
SCHEDULES_FILE = 'schedules.txt'
DATABASE_FILE = 'subjects.txt'
ENROLLMENTS_FILE = 'enrollments.txt'

# --- Funciones para manejar archivos ---

def read_users():
    users = []
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    username, password, role, fullname = line.strip().split('|')
                    users.append(
                        {'username': username, 'password': password, 'role': role, 'fullname': fullname})
    return users


def write_user(username, password, role, fullname):
    with open(USERS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{username}|{password}|{role}|{fullname}\n")


def read_schedules():
    schedules = []
    if os.path.exists(SCHEDULES_FILE):
        with open(SCHEDULES_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                # Compatibilidad: si el archivo viejo tiene 8 campos, asigna 'confirmado' por defecto
                if len(parts) >= 8:
                    sch_id = parts[0]
                    teacher = parts[1]
                    day = parts[2]
                    start_time = parts[3]
                    end_time = parts[4]
                    semester = parts[5]
                    classroom = parts[6]
                    subject = parts[7]
                    status = parts[8] if len(parts) == 9 else 'confirmado'
                    
                    schedules.append({
                        'id': int(sch_id), 'teacher': teacher, 'day': day,
                        'start_time': start_time, 'end_time': end_time,
                        'semester': semester, 'classroom': classroom, 'subject': subject,
                        'status': status
                    })
    return schedules


def write_all_schedules(schedules):
    with open(SCHEDULES_FILE, 'w', encoding='utf-8') as f:
        for s in schedules:
            # Añadimos el estado (status) al final de la línea.
            status = s.get('status', 'pendiente')
            f.write(
                f"{s['id']}|{s['teacher']}|{s['day']}|{s['start_time']}|{s['end_time']}|{s['semester']}|{s['classroom']}|{s['subject']}|{status}\n")


def read_subjects():
    subjects = []
    if not os.path.exists(DATABASE_FILE):
        default_subjects = [
            {'code': 'MAT101', 'name': 'Matemáticas Básicas'},
            {'code': 'PROG101', 'name': 'Programación I'},
            {'code': 'BD101', 'name': 'Bases de Datos'},
            {'code': 'FIS101', 'name': 'Física General'},
            {'code': 'CAL101', 'name': 'Cálculo I'},
            {'code': 'ALG101', 'name': 'Álgebra Lineal'}
        ]
        with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
            for sub in default_subjects:
                f.write(f"{sub['code']}|{sub['name']}\n")

    with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                code, name = line.strip().split('|')
                subjects.append({'code': code, 'name': name})
    return subjects


def read_enrollments():
    enrollments = []
    if os.path.exists(ENROLLMENTS_FILE):
        with open(ENROLLMENTS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 2:
                    enrollments.append(
                        {'student_username': parts[0], 'schedule_id': int(parts[1])})
    return enrollments


def write_enrollment(student_username, schedule_id):
    with open(ENROLLMENTS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{student_username}|{schedule_id}\n")


def write_all_enrollments(enrollments):
    with open(ENROLLMENTS_FILE, 'w', encoding='utf-8') as f:
        for e in enrollments:
            f.write(f"{e['student_username']}|{e['schedule_id']}\n")

# --- Generador de IDs Seguros ---

def generate_safe_id():
    return int(time.time() * 1000)

# --- Rutas de la aplicación ---

@app.route('/')
def home():
    if 'username' in session:
        role_routes = {'coordinator': 'coordinator_dashboard',
                       'teacher': 'teacher_dashboard', 'student': 'student_dashboard'}
        return redirect(url_for(role_routes.get(session['role'], 'login')))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        for user in read_users():
            if user['username'] == username and user['password'] == password:
                session.update(
                    {'username': username, 'role': user['role'], 'fullname': user['fullname']})
                return redirect(url_for('home'))
        return render_template('login.html', error='Usuario o contraseña incorrectos')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        fullname, role = request.form['fullname'], request.form['role']

        if any(u['username'] == username for u in read_users()):
            return render_template('register.html', error='El usuario ya existe')

        write_user(username, password, role, fullname)
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/coordinator', methods=['GET'])
def coordinator_dashboard():
    if session.get('role') != 'coordinator':
        return redirect(url_for('login'))

    all_schedules = read_schedules()
    enrollments = read_enrollments()

    # Conteo de inscripciones
    schedule_enrollment_counts = {s['id']: 0 for s in all_schedules}
    for e in enrollments:
        if e['schedule_id'] in schedule_enrollment_counts:
            schedule_enrollment_counts[e['schedule_id']] += 1

    selected_semester = request.args.get('semester_filter', '')
    
    # Filtra los horarios por semestre si hay uno seleccionado
    schedules = [s for s in all_schedules if s['semester'] ==
                 selected_semester] if selected_semester else all_schedules
                 
    available_semesters = sorted(
        list(set(s['semester'] for s in all_schedules)))
    return render_template('coordinator_dashboard.html', 
                           fullname=session['fullname'], 
                           schedules=schedules,
                           enrollment_counts=schedule_enrollment_counts,
                           available_semesters=available_semesters, 
                           selected_semester=selected_semester)

@app.route('/teacher', methods=['GET', 'POST'])
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))

    teacher_name = session['fullname']
    all_schedules = read_schedules()

    if request.method == 'POST':
        new_schedule = {
            'id': generate_safe_id(),
            'teacher': teacher_name, 'day': request.form['day'],
            'start_time': request.form['start_time'], 'end_time': request.form['end_time'],
            'semester': request.form['semester'], 'classroom': request.form['classroom'],
            'subject': request.form['subject'],
            'status': 'pendiente' # El profesor lo crea en estado pendiente de revisión
        }
        all_schedules.append(new_schedule)
        write_all_schedules(all_schedules)
        return redirect(url_for('teacher_dashboard'))

    return render_template('teacher_dashboard.html', fullname=teacher_name,
                           schedules=[
                               s for s in all_schedules if s['teacher'] == teacher_name],
                           subjects=read_subjects())


@app.route('/student', methods=['GET', 'POST'])
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    all_schedules = read_schedules()
    enrollments = read_enrollments()

    enrolled_schedule_ids = {e['schedule_id']
                             for e in enrollments if e['student_username'] == session['username']}

    if request.method == 'POST':
        schedule_id_to_enroll = int(request.form['schedule_id'])
        if schedule_id_to_enroll not in enrolled_schedule_ids:
            write_enrollment(session['username'], schedule_id_to_enroll)
        return redirect(url_for('student_dashboard'))

    # Se filtran los horarios disponibles: no inscritos y con status 'confirmado'
    return render_template('student_dashboard.html', fullname=session['fullname'],
                           available_schedules=[
                               s for s in all_schedules if s['id'] not in enrolled_schedule_ids and s['status'] == 'confirmado'],
                           student_schedules=[s for s in all_schedules if s['id'] in enrolled_schedule_ids])

@app.route('/update_schedule_status/<int:schedule_id>/<string:new_status>', methods=['POST'])
def update_schedule_status(schedule_id, new_status):
    if session.get('role') != 'coordinator':
        return redirect(url_for('login'))
        
    if new_status not in ['confirmado', 'denegado']:
        return redirect(url_for('coordinator_dashboard'))

    schedules = read_schedules()
    for s in schedules:
        if s['id'] == schedule_id:
            s['status'] = new_status
            break
            
    write_all_schedules(schedules)
    return redirect(url_for('coordinator_dashboard'))


@app.route('/delete_schedule/<int:schedule_id>', methods=['POST'])
def delete_schedule(schedule_id):
    if session.get('role') not in ['coordinator', 'teacher']:
        return redirect(url_for('login'))

    write_all_schedules(
        [s for s in read_schedules() if s['id'] != schedule_id])
    write_all_enrollments([e for e in read_enrollments()
                          if e['schedule_id'] != schedule_id])

    return redirect(url_for(f"{session['role']}_dashboard"))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    read_subjects()
    app.run(debug=True)