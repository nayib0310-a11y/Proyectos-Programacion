import tkinter as tk

ventana = tk.Tk()
ventana.title("Ventana Existente")
ventana.geometry("300x400")
pantalla = tk.Entry(ventana,
                    font=("Arial", 20), borderwidth=5, relief="flat")


etiqueta = tk.Label (ventana, text = "Estoy cansado jefe")
etiqueta.pack (fill=tk.BOTH)



ventana.mainloop()
