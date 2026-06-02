def calculadora():
    print('Bienvenido a nuestra calculadora')

    while True:
         print("-" * 30)
         print('selecciona operacion')
         print('si deseas cerrar sesion coloca, ("salir")')

         operacion = input("> ").lower()
         if operacion == 'salir':
            print('gracias por su tiempo')
            break
         if operacion == " ":
            continue

         try:
            resultado = eval(operacion)
            print(f"el resultado es: {resultado}")
         except ZeroDivisionError:
            print('matematicamente imposible Joven')
         except NameError:
             print('los caracteres agregados no corresponden a este sistema, chao')
         except SyntaxError:
             print('la ecuacion esta incompleta o mal escrita')
         except Exception as e:
             print("y este error?: {e}")

calculadora()