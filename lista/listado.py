Edades = [20, 23, 23, 21, 20, 21, 22, 19, 19, 20, 21, 23, 20, 21, 20, 23]
Nuevas_edades = []

while True:
    G = input(f"\nLista actual: {Edades + Nuevas_edades}\n¿Deseas agregar una nueva Edad? (si/no): ")
    
    if G.lower().strip() == "si":
        nueva_edad = int(input('Agregar nueva edad: '))
        Nuevas_edades.append(nueva_edad)
        print(f"Edad agregada: {nueva_edad}")
    else:
        print("\n--- Datos Agragados a la Lista ---")
        break

Edades = Edades + Nuevas_edades 

promedio = sum(Edades) / len(Edades)
print(f"\nEl nuevo promedio de todas las edades es: {promedio:.2f}") 

mayores = []
menores = []
iguales = []

for edad in Edades:
    if edad > promedio:
        mayores.append(edad)
    elif edad < promedio:  
        menores.append(edad)
    else:                  
        iguales.append(edad)

print("\n--- Resultados de la Clasificación ---")
print(f"Edades Mayores al promedio: {mayores}")
print(f"Edades Menores al promedio: {menores}")
print(f"Edades Iguales al promedio: {iguales}")