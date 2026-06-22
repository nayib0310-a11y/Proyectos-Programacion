from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# Archivos de base de datos
USERS_FILE = 'users.txt'
SCHEDULES_FILE = 'schedules.txt'
DATABASE_FILE = 'subjects.txt'
ENROLLMENTS_FILE = 'enrollments.txt' # Nuevo archivo para inscripciones

# --- Funciones para manejar archivos ---

def read_users():
    users = []
    try:
        with open(USERS_FILE, 'r') as f:
            for line in f:
                username, password, role, fullname = line.strip().split('|')
                users.append({
                    'username': username,
                    'password': password,
                    'role': role,
                    'fullname': fullname
                })
    except FileNotFoundError:
        pass
    return users

def write_user(username, password, role, fullname):
    with open(USERS_FILE, 'a') as f:
        f.write(f"{username}|{password}|{role}|{fullname}\n")

def read_schedules():
    schedules = []
    try:
        with open(SCHEDULES_FILE, 'r') as f:
            for i, line in enumerate(f):
                parts = line.strip().split('|')
                if len(parts) == 7: # Formato esperado: teacher|day|start_time|end_time|semester|classroom|subject
                    teacher, day, start_time, end_time, semester, classroom, subject = parts
                    schedules.append({
                        'id': i,
                        'teacher': teacher,
                        'day': day,
                        'start_time': start_time,
                        'end_time': end_time,
                        'semester': semester,
                        'classroom': classroom,
                        'subject': subject
                    })
    except FileNotFoundError:
        pass
    return schedules

def write_all_schedules(schedules):
    with open(SCHEDULES_FILE, 'w') as f:
        for s in schedules:
            f.write(f"{s['teacher']}|{s['day']}|{s['start_time']}|{s['end_time']}|{s['semester']}|{s['classroom']}|{s['subject']}\n")

def read_subjects():
    subjects = []
    try:
        with open(DATABASE_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 2:
                    code, name = parts
                    subjects.append({
                        'code': code,
                        'name': name
                    })
    except FileNotFoundError:
        # Si el archivo no existe, crea unas materias por defecto
        subjects = [
            {'code': 'MAT101', 'name': 'Matemáticas Básicas'},
            {'code': 'PROG101', 'name': 'Programación I'},
            {'code': 'BD101', 'name': 'Bases de Datos'},
            {'code': 'FIS101', 'name': 'Física General'},
            {'code': 'CAL101', 'name': 'Cálculo I'},
            {'code': 'ALG101', 'name': 'Álgebra Lineal'}
        ]
        with open(DATABASE_FILE, 'w') as f:
            for subject in subjects:
                f.write(f"{subject['code']}|{subject['name']}\n")
    return subjects

def read_enrollments():
    enrollments = []
    try:
        with open(ENROLLMENTS_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 2: # student_username|schedule_id
                    enrollments.append({
                        'student_username': parts[0],
                        'schedule_id': int(parts[1])
                    })
    except FileNotFoundError:
        pass
    return enrollments

def write_enrollment(student_username, schedule_id):
    with open(ENROLLMENTS_FILE, 'a') as f:
        f.write(f"{student_username}|{schedule_id}\n")

def write_all_enrollments(enrollments):
    with open(ENROLLMENTS_FILE, 'w') as f:
        for e in enrollments:
            f.write(f"{e['student_username']}|{e['schedule_id']}\n")


# --- Rutas de la aplicación ---

@app.route('/')
def home():
    if 'username' in session:
        if session['role'] == 'coordinator':
            return redirect(url_for('coordinator_dashboard'))
        elif session['role'] == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        elif session['role'] == 'student':
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = read_users()
        for user in users:
            if user['username'] == username and user['password'] == password:
                session['username'] = username
                session['role'] = user['role']
                session['fullname'] = user['fullname']
                return redirect(url_for('home'))
        
        return render_template('login.html', error='Usuario o contraseña incorrectos')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        role = request.form['role']
        
        users = read_users()
        for user in users:
            if user['username'] == username:
                return render_template('register.html', error='El usuario ya existe')
        
        write_user(username, password, role, fullname)
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/coordinator', methods=['GET', 'POST'])
def coordinator_dashboard():
    if 'username' not in session or session['role'] != 'coordinator':
        return redirect(url_for('login'))
    
    all_schedules = read_schedules()
    users = read_users()
    teachers = [user for user in users if user['role'] == 'teacher']
    subjects = read_subjects()
    enrollments = read_enrollments()

    # Calcular cuántos estudiantes hay por materia (por horario específico)
    schedule_enrollment_counts = {}
    for schedule in all_schedules:
        count = 0
        for enrollment in enrollments:
            if enrollment['schedule_id'] == schedule['id']:
                count += 1
        schedule_enrollment_counts[schedule['id']] = count
    
    # Manejar el filtro de semestre
    selected_semester = request.args.get('semester_filter', '')
    if selected_semester:
        schedules = [s for s in all_schedules if s['semester'] == selected_semester]
    else:
        schedules = all_schedules

    # Obtener una lista de semestres únicos para el filtro
    available_semesters = sorted(list(set([s['semester'] for s in all_schedules])))

    if request.method == 'POST':
        teacher = request.form['teacher']
        day = request.form['day']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        semester = request.form['semester'] # Ahora el coordinador especifica el semestre
        classroom = request.form['classroom']
        subject = request.form['subject']
        
        # Reescribe todos los horarios para generar un nuevo ID si es necesario, o añade uno nuevo
        current_schedules = read_schedules() # Lee de nuevo para asegurar el ID correcto
        next_id = len(current_schedules) if current_schedules else 0
        new_schedule = {
            'id': next_id,
            'teacher': teacher,
            'day': day,
            'start_time': start_time,
            'end_time': end_time,
            'semester': semester,
            'classroom': classroom,
            'subject': subject
        }
        current_schedules.append(new_schedule)
        write_all_schedules(current_schedules) # Escribir la lista actualizada
        return redirect(url_for('coordinator_dashboard', semester_filter=selected_semester)) # Redirigir manteniendo el filtro

    return render_template('coordinator_dashboard.html',
                           fullname=session['fullname'],
                           schedules=schedules,
                           teachers=teachers,
                           subjects=subjects,
                           enrollment_counts=schedule_enrollment_counts,
                           available_semesters=available_semesters,
                           selected_semester=selected_semester)

@app.route('/teacher', methods=['GET', 'POST'])
def teacher_dashboard():
    if 'username' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    teacher_name = session['fullname']
    # Ahora los profesores también pueden proponer horarios con semestre
    all_schedules = read_schedules()
    schedules = [s for s in all_schedules if s['teacher'] == teacher_name]
    
    if request.method == 'POST':
        day = request.form['day']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        semester = request.form['semester'] # Profesor también puede proponer semestre
        classroom = request.form['classroom']
        subject = request.form['subject']
        
        current_schedules = read_schedules()
        next_id = len(current_schedules) if current_schedules else 0
        new_schedule = {
            'id': next_id,
            'teacher': teacher_name,
            'day': day,
            'start_time': start_time,
            'end_time': end_time,
            'semester': semester,
            'classroom': classroom,
            'subject': subject
        }
        current_schedules.append(new_schedule)
        write_all_schedules(current_schedules)
        return redirect(url_for('teacher_dashboard'))
    
    subjects = read_subjects()
    return render_template('teacher_dashboard.html',
                           fullname=teacher_name,
                           schedules=schedules,
                           subjects=subjects)

@app.route('/student', methods=['GET', 'POST'])
def student_dashboard():
    if 'username' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    student_username = session['username']
    all_schedules = read_schedules()
    enrollments = read_enrollments()
    
    # Obtener los IDs de los horarios en los que el estudiante ya está inscrito
    enrolled_schedule_ids = {e['schedule_id'] for e in enrollments if e['student_username'] == student_username}
    
    # Horarios disponibles para inscripción (que no sean los ya inscritos)
    available_schedules = [s for s in all_schedules if s['id'] not in enrolled_schedule_ids]
    
    # Horarios del estudiante (inscritos)
    student_schedules = [s for s in all_schedules if s['id'] in enrolled_schedule_ids]

    if request.method == 'POST':
        schedule_id_to_enroll = int(request.form['schedule_id'])
        
        # Verificar si el estudiante ya está inscrito para evitar duplicados
        already_enrolled = False
        for e in enrollments:
            if e['student_username'] == student_username and e['schedule_id'] == schedule_id_to_enroll:
                already_enrolled = True
                break
        
        if not already_enrolled:
            write_enrollment(student_username, schedule_id_to_enroll)
        
        return redirect(url_for('student_dashboard'))
    
    return render_template('student_dashboard.html',
                           fullname=session['fullname'],
                           available_schedules=available_schedules,
                           student_schedules=student_schedules)

# --- Nueva ruta para eliminar horario ---
@app.route('/delete_schedule/<int:schedule_id>', methods=['POST'])
def delete_schedule(schedule_id):
    if 'username' not in session or session['role'] not in ['coordinator', 'teacher']:
        return redirect(url_for('login'))

    all_schedules = read_schedules()
    updated_schedules = [s for s in all_schedules if s['id'] != schedule_id]
    
    write_all_schedules(updated_schedules) # Reescribe el archivo sin el horario eliminado

    # También eliminar inscripciones asociadas a este horario
    all_enrollments = read_enrollments()
    updated_enrollments = [e for e in all_enrollments if e['schedule_id'] != schedule_id]
    write_all_enrollments(updated_enrollments)
    
    if session['role'] == 'coordinator':
        return redirect(url_for('coordinator_dashboard'))
    else: # if session['role'] == 'teacher':
        return redirect(url_for('teacher_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Asegúrate de que los archivos existan
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            pass
    if not os.path.exists(SCHEDULES_FILE):
        with open(SCHEDULES_FILE, 'w') as f:
            pass
    if not os.path.exists(DATABASE_FILE):
        # Esta función ya crea el archivo con datos por defecto si no existe
        read_subjects()
    if not os.path.exists(ENROLLMENTS_FILE):
        with open(ENROLLMENTS_FILE, 'w') as f:
            pass

    app.run(debug=True)
