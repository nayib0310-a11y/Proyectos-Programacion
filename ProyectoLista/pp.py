from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Nuestro diccionario ahora guardará: {"Nombre": ["Documento", "Estado"]}
registro_asistencia = {}
ruta = r"C:\Users\nayib\OneDrive\Desktop\Proyectos Programacion\ProyectoLista\lista_Estudiantes.txt"


def sincronizar_txt_con_diccionario():
    with open(ruta, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            # Validamos que la línea tenga una coma para evitar errores
            if "," in linea:
                # .split(",") corta el texto en dos partes
                partes = linea.split(",")

                nombre = partes[0].strip()
                documento = partes[1].strip()

                # Guardamos al alumno asignándole una lista con su documento y estado inicial
                if nombre != "" and nombre not in registro_asistencia:
                    registro_asistencia[nombre] = [documento, "Pendiente"]


@app.route("/")
def inicio():
    sincronizar_txt_con_diccionario()

    busqueda = request.args.get("palabra")
    diccionario_filtrado = {}

    if busqueda:
        # Ahora 'datos' es una lista: datos[0] es la cédula, datos[1] es el estado
        for nombre, datos in registro_asistencia.items():
            # Buscamos coincidencias en el nombre O en el documento
            if busqueda.lower() in nombre.lower() or busqueda.lower() in datos[0].lower():
                diccionario_filtrado[nombre] = datos
    else:
        diccionario_filtrado = registro_asistencia

    return render_template("index.html", lista_html=diccionario_filtrado)


@app.route("/marcar/<nombre_alumno>/<nuevo_estado>")
def marcar_asistencia(nombre_alumno, nuevo_estado):
    if nombre_alumno in registro_asistencia:
        # Accedemos al índice [1] que es donde vive el "Estado" y lo actualizamos
        registro_asistencia[nombre_alumno][1] = nuevo_estado

    return redirect("/")


@app.route("/agregar")
def agregar_alumno():
    nuevo_nombre = request.args.get("nuevo_nombre")
    tipo_doc = request.args.get("tipo_doc")  # Recibe V, E, o P
    num_doc = request.args.get("num_doc")   # Recibe el número

    if nuevo_nombre and num_doc:
        # Armamos el texto exacto como lo queremos en el TXT (Ej: "Carlos, V-1234567")
        documento_completo = f"{tipo_doc}-{num_doc}"
        linea_nueva = f"{nuevo_nombre}, {documento_completo}"

        with open(ruta, "a", encoding="utf-8") as archivo:
            archivo.write("\n" + linea_nueva)

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
