from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "clave_super_secreta"

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]

HORAS = [
    "07:00 - 07:45", "07:45 - 08:30", "08:30 - 09:15", 
    "09:15 - 10:00", "10:00 - 10:45", "10:45 - 11:30",
    "11:30 - 12:15", "12:15 - 13:00", "13:00 - 13:45",
    "13:45 - 14:30", "14:30 - 15:15", "15:15 - 16:00",
    "16:00 - 16:45", "16:45 - 17:30"
]

MATERIAS = {
    "MAT1": {"nombre": "Matemática I", "prelacion": None},
    "PROG1": {"nombre": "Programación I", "prelacion": None},
    "FIS1": {"nombre": "Física I", "prelacion": None},
    "ING1": {"nombre": "Inglés I", "prelacion": None},
    "DIN1": {"nombre": "Defensa Integral De La Nación I", "prelacion": None}
}

BASE_DATOS = {
    "estudiantes": {},
    "docentes": {
        "jose maldonado": {
            "password": "abcd", 
            "nombre_real": "Jose Maldonado",
            "disponibilidad": [[False for _ in range(len(HORAS))] for _ in range(len(DIAS))]
        },
        "juan ledezma": {
            "password": "abcd", 
            "nombre_real": "Juan Ledezma",
            "disponibilidad": [[False for _ in range(len(HORAS))] for _ in range(len(DIAS))]
        },
        "carlos adame": {
            "password": "abcd", 
            "nombre_real": "Carlos Adame",
            "disponibilidad": [[False for _ in range(len(HORAS))] for _ in range(len(DIAS))]
        },
        "juan carvajal": {
            "password": "abcd", 
            "nombre_real": "Juan Carvajal",
            "disponibilidad": [[False for _ in range(len(HORAS))] for _ in range(len(DIAS))]
        }
    },
    "coordinadores": {
        "admin": {"password": "admin", "nombre_real": "Coordinador General"}
    }
}

OFERTA_ACADEMICA = []

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        rol = request.form["rol"]
        usuario = request.form["usuario"].lower().strip()
        password = request.form["password"]

        if rol == "estudiantes" and usuario not in BASE_DATOS["estudiantes"]:
            BASE_DATOS["estudiantes"][usuario] = {
                "password": password,
                "nombre_real": usuario.title(),
                "aprobadas": [],
                "horario": [[None for _ in range(len(HORAS))] for _ in range(len(DIAS))]
            }

        if usuario in BASE_DATOS.get(rol, {}):
            if BASE_DATOS[rol][usuario]["password"] == password:
                session["usuario"] = usuario
                session["rol"] = rol
                session["nombre"] = BASE_DATOS[rol][usuario].get("nombre_real", usuario)
                return redirect(url_for(f"vista_{rol}"))
        flash("Credenciales incorrectas", "error")
    return render_template("login.html")

@app.route("/coordinador", methods=["GET", "POST"])
def vista_coordinadores():
    if session.get("rol") != "coordinadores": return redirect(url_for("login"))

    profesor_seleccionado = None
    id_profesor_sel = ""

    if request.args.get("ver_profesor"):
        id_profesor_sel = request.args.get("ver_profesor")
        if id_profesor_sel in BASE_DATOS["docentes"]:
            profesor_seleccionado = BASE_DATOS["docentes"][id_profesor_sel]

    if request.method == "POST":
        accion = request.form["accion"]
        
        if accion == "nuevo_docente":
            u = request.form["usuario_doc"].lower().strip()
            n = request.form["nombre_doc"]
            p = request.form["pass_doc"]
            if u not in BASE_DATOS["docentes"]:
                BASE_DATOS["docentes"][u] = {
                    "password": p, "nombre_real": n, 
                    "disponibilidad": [[False]*len(HORAS) for _ in range(len(DIAS))]
                }
                flash(f"Docente {n} registrado.", "success")
            else: 
                flash("Usuario ya existe.", "error")

        elif accion == "nueva_materia":
            c = request.form["cod_mat"].upper()
            n = request.form["nom_mat"]
            p = request.form.get("pre_mat") or None
            MATERIAS[c] = {"nombre": n, "prelacion": p}
            flash(f"Materia {n} creada.", "success")

        elif accion == "nueva_seccion":
            cod = request.form["codigo"]
            prof = request.form["profesor_user"]
            dia = int(request.form["dia_idx"])
            inicio = int(request.form["hora_inicio_idx"])
            fin = int(request.form["hora_fin_idx"])
            
            seccion_txt = request.form["seccion_txt"].upper()
            aula_txt = request.form["aula_txt"].upper()

            if inicio > fin:
                flash("Error: La hora de inicio debe ser menor a la final.", "error")
            else:
                profesor = BASE_DATOS["docentes"][prof]
                esta_libre = True
                
                for h in range(inicio, fin + 1):
                    if not profesor["disponibilidad"][dia][h]:
                        esta_libre = False
                        break
                
                if esta_libre:
                    nueva_seccion = {
                        "id": len(OFERTA_ACADEMICA),
                        "codigo": cod,
                        "materia": MATERIAS[cod]["nombre"],
                        "profesor": profesor["nombre_real"],
                        "dia_idx": dia,
                        "hora_inicio": inicio,
                        "hora_fin": fin,
                        "horario_txt": f"{DIAS[dia]} de {HORAS[inicio].split('-')[0]} a {HORAS[fin].split('-')[1]}",
                        "seccion": seccion_txt,
                        "aula": aula_txt
                    }
                    OFERTA_ACADEMICA.append(nueva_seccion)
                    flash(f"Sección {seccion_txt} creada en Aula {aula_txt}.", "success")
                else:
                    flash("Error: El profesor NO tiene disponibilidad en todo ese rango.", "error")
            
            id_profesor_sel = prof
            profesor_seleccionado = BASE_DATOS["docentes"][prof]

    return render_template("coordinador.html", 
                           materias=MATERIAS, docentes=BASE_DATOS["docentes"], 
                           dias=DIAS, horas=HORAS, oferta=OFERTA_ACADEMICA,
                           prof_sel=profesor_seleccionado, id_sel=id_profesor_sel)

@app.route("/docente", methods=["GET", "POST"])
def vista_docentes():
    if session.get("rol") != "docentes": return redirect(url_for("login"))
    
    perfil = BASE_DATOS["docentes"][session["usuario"]]

    if request.method == "POST":
        perfil["disponibilidad"] = [[False for _ in range(len(HORAS))] for _ in range(len(DIAS))]
        
        marcadas = request.form.getlist("casillas")
        
        for item in marcadas:
            partes = item.split("_")
            d = int(partes[0])
            h = int(partes[1])
            perfil["disponibilidad"][d][h] = True
            
        flash("Disponibilidad guardada correctamente.", "success")

    return render_template("docente.html", perfil=perfil, dias=DIAS, horas=HORAS)

@app.route("/estudiante", methods=["GET", "POST"])
def vista_estudiantes():
    if session.get("rol") != "estudiantes": return redirect(url_for("login"))
    
    perfil = BASE_DATOS["estudiantes"][session["usuario"]]

    if request.method == "POST":
        sel = OFERTA_ACADEMICA[int(request.form["oferta_id"])]
        req = MATERIAS[sel["codigo"]]["prelacion"]
        
        if req and req not in perfil["aprobadas"]:
            flash(f"Requiere aprobar {MATERIAS[req]['nombre']}", "error")
        else:
            choque = False
            for h in range(sel["hora_inicio"], sel["hora_fin"] + 1):
                if perfil["horario"][sel["dia_idx"]][h] is not None:
                    choque = True
                    break
            
            if choque:
                flash("Error: Choque de horario con otra materia.", "error")
            else:
                for h in range(sel["hora_inicio"], sel["hora_fin"] + 1):
                    perfil["horario"][sel["dia_idx"]][h] = {
                        "materia": sel["materia"],
                        "profesor": sel["profesor"],
                        "seccion": sel["seccion"],
                        "aula": sel["aula"]
                    }
                flash("Inscrito exitosamente", "success")

    return render_template("estudiante.html", estudiante=perfil, oferta=OFERTA_ACADEMICA, dias=DIAS, horas=HORAS)

@app.route("/estudiante/comprobante")
def comprobante():
    if session.get("rol") != "estudiantes": return redirect(url_for("login"))
    perfil = BASE_DATOS["estudiantes"][session["usuario"]]
    
    inscritas_resumen = []
    vistas = set()

    for d in range(len(DIAS)):
        for h in range(len(HORAS)):
            celda = perfil["horario"][d][h]
            if celda:
                clave = f"{celda['materia']}-{d}"
                if clave not in vistas:
                    inscritas_resumen.append({
                        "materia": celda["materia"],
                        "profesor": celda["profesor"],
                        "dia": DIAS[d],
                        "seccion": celda.get("seccion", "N/A"),
                        "aula": celda.get("aula", "N/A")
                    })
                    vistas.add(clave)

    return render_template("comprobante.html", estudiante=perfil, lista=inscritas_resumen, dias=DIAS, horas=HORAS, fecha=datetime.now().strftime("%d/%m/%Y"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
