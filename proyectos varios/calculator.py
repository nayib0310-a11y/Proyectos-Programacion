import tkinter as tk



ventana = tk.Tk()
ventana.title("La real Calculadora")
ventana.geometry("300x400")

pantalla = tk.Entry(ventana,
                    font=("Arial", 20), borderwidth=5, relief="flat")

pantalla.grid(row=0, column=0, columnspan=4, padx=10,
              pady=10)

botones = {
    '1', '5', '9', '+',
    '2', '6', '0', '-',
    '3', '7', 'C', '*',
    '4', '8', '=', '/'}


def click_boton(valor):
    actual = pantalla.get()
    pantalla.delete(0, tk.END)
    pantalla.insert(0, str(actual) + str(valor))


fila_actual = 1
columna_actual = 0

for boton in botones:
    tk.Button(ventana, text=boton, width=5, height=2,
              command=lambda t=boton: click_boton(t)).grid(sticky="nsew",
                                                           row=fila_actual, column=columna_actual)
    columna_actual += 1
    if columna_actual > 2:
        columna_actual = 0
        fila_actual += 1


ventana.mainloop()
