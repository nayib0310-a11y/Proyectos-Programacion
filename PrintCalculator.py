Bienvenida = print('Bienvenido, Realiza tu Calculo Aqui!')

while True:
    print("-" * 40)
    ecuacion = input("Escribe tu ecuación (o 'salir'): ").lower().strip()

    if ecuacion == 'salir':
        print('Gracias por su tiempo')
        break
    if ecuacion == "":
        continue

    ecuacion = ecuacion.replace('x', '*')
    for operador in ['+', '-', '*', '/']:
        ecuacion = ecuacion.replace(operador, f" {operador} ")

    elementos = ecuacion.split()

    try:
        i = 0
        while i < len(elementos):
            if elementos[i] in ['*', '/']:
                n1 = float(elementos[i - 1])
                n2 = float(elementos[i + 1])
                if elementos[i] == '*':
                    Resultado = n1 * n2
                else:
                    if n2 == 0:
                        raise ZeroDivisionError
                    Resultado = n1 / n2
                elementos[i - 1] = str(Resultado)
                del elementos[i:i + 2]
                i -= 1 
            i += 1
        i = 0
        while i < len(elementos):
            if elementos[i] in ['+', '-']:
                n1 = float(elementos[i - 1])
                n2 = float(elementos[i + 1])
                if elementos[i] == '+':
                    Resultado = n1 + n2
                else:
                    Resultado = n1 - n2
                elementos[i - 1] = str(Resultado)
                del elementos[i:i + 2]
                i -= 1
            i += 1

        # --- PASO 4: MOSTRAR RESULTADO ---
        resultadoF = elementos[0]
        print(f"\n✅ El resultado es: {resultadoF}")

    except ValueError:
        print('Los caracteres agregados no pertenecen al sistema, chao')
    except ZeroDivisionError:
        print('Matemáticamente imposible Joven (No se puede dividir por cero)')
    except Exception:
        print('La ecuación está incompleta o mal escrita')
