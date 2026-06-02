Edades = [20, 23, 23, 21, 20, 21, 22, 19, 19, 20, 21, 23, 20, 21, 20, 23]

while True:
    try:
        G = input(
            f"\nLista actual: {Edades}\n¿Deseas agregar una nueva Edad? (si/no): ")

        if G.lower().strip() == "si":
              nueva_edad = int(input('Agregar nueva edad: '))
              Edades.append(nueva_edad)
              print(f"Edad agregada: {nueva_edad}")
        if G != "si" and G != "no":
             print("comando no valido, por favor agregar un comando valido")
             continue

        if G.lower().strip() == "no":
             print("\n--- Datos recolectados con éxito ---")
             break
        mayor = Edades[0]
        
        menor = Edades[0]
    except ValueError:
        print("Entrada no válida. Por favor, ingresa un número entero para la edad.")




for edad in Edades:
    if edad > mayor:
        mayor = edad

    if edad < menor:
        menor = edad

print("\n--- Resultados Finales ---")
print(f"La edad más ALTA de toda la lista es: {mayor}")
print(f"La edad más BAJA de toda la lista es: {menor}")
    
