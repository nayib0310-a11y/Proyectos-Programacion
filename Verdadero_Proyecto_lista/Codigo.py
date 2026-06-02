from flask import Flask, render_template, request
import PyPDF2



app = Flask(__name__)
estudiantes = []          
asistencia_diaria = []  
  

def extraer_datos_archivo(archivo):
    nombre_archivo = archivo.filename.lower()
    texto_extraido = ""
    
    if nombre_archivo.endswith('.txt'):
        texto_extraido = archivo.read().decode('utf-8')
    elif nombre_archivo.endswith('.pdf'):
        lector_pdf = PyPDF2.PdfReader(archivo)
        for pagina in lector_pdf.pages:
            texto_extraido += pagina.extract_text() + "\n"
    else:
        raise ValueError("Formato no válido. Por favor, suba únicamente archivos .txt o .pdf")
            
    if not texto_extraido.strip():
        raise ValueError("El documento está vacío.")
            
    lista_cruda = texto_extraido.split('\n')
    lista_procesada = []
    
    for linea in lista_cruda:
        linea = linea.strip()
        if linea != "":
            # Cortamos la línea en una lista de palabras separadas
            palabras = linea.split()
            cedula = "Sin Cédula"
            nombre_partes = []
            for palabra in palabras:
                tiene_numero = False
                for letra in palabra:
                    if letra.isdigit():
                        tiene_numero = True
                        break 
                
                # CLASIFICACIÓN DE LA PALABRA
                if tiene_numero:
                    cedula_limpia = palabra.replace('-', '').replace('.', '').upper()
                    if not cedula_limpia.startswith('V') and not cedula_limpia.startswith('E'):
                        cedula = 'V' + cedula_limpia
                    else:
                        cedula = cedula_limpia
                        
                elif palabra.upper() in ['V', 'E', 'V-', 'E-']:
                    continue
                    
                else:
                    nombre_partes.append(palabra)
            
            nombre = " ".join(nombre_partes)
            
            lista_procesada.append((nombre, cedula))
            
    lista_final_ordenada = sorted(lista_procesada)
            
    return lista_final_ordenada

#  RUTAS DE LA APLICACIÓN

total_clases = 0
historial_asistencia = {}
ultimo_reporte_diario = []
fecha_ultimo_reporte = ""


@app.route('/')
def index():
    global estudiantes
    if estudiantes:
        lista_con_estado = [(i, nombre, cedula, "Sin Registrar")
                            for i, (nombre, cedula) in enumerate(estudiantes)]
        return render_template('html.html', lista_enviada=lista_con_estado, base_cargada=True)
    else:
        return render_template('html.html', base_cargada=False)


@app.route('/subir_general', methods=['POST'])
def subir_general():
    try:
        global estudiantes
        if 'archivo_general' not in request.files or request.files['archivo_general'].filename == '':
            return render_template('html.html', mensaje_error="Aviso: No seleccionó la Lista General.", base_cargada=False)

        archivo = request.files['archivo_general']
        estudiantes = extraer_datos_archivo(archivo)

        lista_con_estado = [(i, nombre, cedula,  "Sin Registrar")
                            for i, (nombre, cedula) in enumerate(estudiantes)]

        return render_template('html.html', lista_enviada=lista_con_estado, base_cargada=True)

    except Exception as ex:
        return render_template('html.html', mensaje_error=f"Error en Lista General: {str(ex)}", base_cargada=False)


@app.route('/subir_clase', methods=['POST'])
def subir_clase():
    try:
        global estudiantes
        global asistencia_diaria

        if not estudiantes:
            return render_template('html.html', mensaje_error="Error: Suba la Lista General primero.", base_cargada=False)

        if 'archivo_clase' not in request.files or request.files['archivo_clase'].filename == '':
            lista_con_estado = [(i, nombre, cedula, "Sin Registrar")
                                for i, (nombre, cedula) in enumerate(estudiantes)]
            return render_template('html.html', lista_enviada=lista_con_estado, mensaje_error="Aviso: No seleccionó la Asistencia.", base_cargada=True)

        archivo = request.files['archivo_clase']
        asistencia_diaria = extraer_datos_archivo(archivo)

        cedulas_hoy = [cedula for nombre, cedula in asistencia_diaria]
        resultados_asistencia = []

        for i, (nombre, cedula) in enumerate(estudiantes):
            if cedula in cedulas_hoy:
                resultados_asistencia.append((i, nombre, cedula, "Presente"))
            else:
                resultados_asistencia.append((i, nombre, cedula, "Ausente"))

        return render_template('html.html', lista_enviada=resultados_asistencia, base_cargada=True)

    except Exception as ex:
        return render_template('html.html', mensaje_error=f"Error al procesar asistencia: {str(ex)}", base_cargada=bool(estudiantes))


@app.route('/buscar', methods=['POST'])
def buscar_estudiante():
    try:
        palabra_cruda = request.form.get('palabra_buscada')
        if not palabra_cruda or palabra_cruda.strip() == "":
            return render_template('html.html',
                                   lista_enviada=list(enumerate(estudiantes)),
                                   mensaje_error="Aviso: El campo de búsqueda está vacío.")

        palabra = palabra_cruda.strip().lower()
        resultados_busqueda = []
        for indice, estudiante in enumerate(estudiantes):
            if palabra in estudiante.lower():
                resultados_busqueda.append((indice, estudiante))

        if len(resultados_busqueda) > 0:
            return render_template('html.html', lista_enviada=resultados_busqueda)
        else:
            return render_template('html.html',
                                   lista_enviada=list(enumerate(estudiantes)),
                                   mensaje_error=f"Aviso: Ningún alumno coincide con la búsqueda '{palabra_cruda}'.")

    except Exception as ex:
        return render_template('html.html',
                               lista_enviada=list(enumerate(estudiantes)),
                               mensaje_error=f"Error interno del buscador: {str(ex)}")


@app.route('/eliminar/<int:id>')
def eliminar_estudiante(id):

    if 0 <= id < len(estudiantes):
        estudiantes.pop(id)
    return render_template('html.html', lista_enviada=list(enumerate(estudiantes)))


@app.route('/editar/<int:id>', methods=['POST'])
def editar_estudiante(id):

    if 0 <= id < len(estudiantes):
        nombre_actualizado = request.form['nuevo_nombre'].title().strip()
        estudiantes[id] = nombre_actualizado
        estudiantes.sort()
    return render_template('html.html', lista_enviada=list(enumerate(estudiantes)))


@app.route('/agregar', methods=['POST'])
def agregar_estudiante():
    nuevo_nombre = request.form['nombre_ingresado'].strip().title()
    if nuevo_nombre != "" and nuevo_nombre not in estudiantes:
        estudiantes.append(nuevo_nombre)
        estudiantes.sort()

    return render_template('html.html', lista_enviada=list(enumerate(estudiantes)))


if __name__ == '__main__':

    app.run(debug=True)
