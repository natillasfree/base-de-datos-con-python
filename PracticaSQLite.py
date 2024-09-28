import sqlite3
import re
import os

def filtrar_datos_usuario(nombre, edad, email, contrasena, dni, rol, fecha_nacimiento, telefono):
    if not all(isinstance(i, str) for i in [nombre, email, contrasena, dni, rol, fecha_nacimiento, telefono]) or not isinstance(edad, int):
        raise ValueError("Tipos de datos incorrectos")

    nombre = re.sub(r"[^a-zA-Z0-9 ]", "", nombre)
    email = re.sub(r"[^a-zA-Z0-9@.]", "", email)
    dni = re.sub(r"[^a-zA-Z0-9]", "", dni)
    rol = re.sub(r"[^a-zA-Z]", "", rol)
    fecha_nacimiento = re.sub(r"[^0-9-]", "", fecha_nacimiento)
    telefono = re.sub(r"[^0-9]", "", telefono)

    return nombre, edad, email, contrasena, dni, rol, fecha_nacimiento, telefono

def crear_usuario():
    nombre = input("Nombre: ")
    while not nombre.strip():
        print("El nombre no puede estar vacío. Inténtalo de nuevo.")
        nombre = input("Nombre: ")

    edad = -1
    while edad < 0 or edad > 120:
        try:
            edad = int(input("Edad: "))
        except ValueError:
            print("La edad debe ser un número entero. Inténtalo de nuevo.")

    email = input("Email: ")
    while not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        print("El email no es válido. Inténtalo de nuevo.")
        email = input("Email: ")

    contrasena = input("Contraseña: ")
    while len(contrasena) < 8:
        print("La contraseña debe tener al menos 8 caracteres. Inténtalo de nuevo.")
        contrasena = input("Contraseña: ")

    dni = input("DNI: ")
    while not dni.isdigit() or len(dni) != 8:
        print("El DNI debe ser un número de 8 dígitos. Inténtalo de nuevo.")
        dni = input("DNI: ")
        
    usuario_existente = buscar_usuario_por_dni(dni)

    if usuario_existente:
        print("Error: Ya existe un usuario con el mismo DNI.")
        input("Continuar...")
        limpiar_pantalla()
        return

    rol = input("Rol (Administrador/Usuario): ")
    while rol.lower() not in ["administrador", "usuario"]:
        print("El rol debe ser 'Administrador' o 'Usuario'. Inténtalo de nuevo.")
        rol = input("Rol: ")

    fecha_nacimiento = input("Fecha de Nacimiento (YYYY-MM-DD): ")
    while not re.match(r"^\d{4}-\d{2}-\d{2}$", fecha_nacimiento):
        print("La fecha de nacimiento debe estar en formato 'YYYY-MM-DD'. Inténtalo de nuevo.")
        fecha_nacimiento = input("Fecha de Nacimiento: ")

    telefono = input("Teléfono: ")
    while not telefono.isdigit():
        print("El teléfono debe ser un número. Inténtalo de nuevo.")
        telefono = input("Teléfono: ")

    nombre, edad, email, contrasena, dni, rol, fecha_nacimiento, telefono = filtrar_datos_usuario(
        nombre, edad, email, contrasena, dni, rol, fecha_nacimiento, telefono
    )

    # Conectar a la base de datos SQLite
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    # Crear la tabla si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            nombre TEXT,
            edad INTEGER,
            email TEXT,
            contrasena TEXT,
            dni TEXT PRIMARY KEY,
            rol TEXT,
            fecha_nacimiento TEXT,
            telefono TEXT
        )
    ''')

    # Insertar datos en la tabla
    cursor.execute('''
        INSERT INTO usuarios VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nombre, edad, email, contrasena, dni, rol, fecha_nacimiento, telefono))

    # Confirmar cambios y cerrar la conexión
    conn.commit()
    conn.close()

    limpiar_pantalla()

def validar_rol(rol):
    if rol.lower() == "administrador" or rol.lower() == "usuario":
        return True
    else:
        return False
    
def listar_usuarios():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM usuarios')
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    conn.close()
    input("Continua...")
    limpiar_pantalla()

def buscar_usuario_por_dni(dni):
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM usuarios WHERE dni = ?', (dni,))
    row = cursor.fetchone()

    conn.close()
    return row

def modificar_usuario():
    dni = input("Ingrese el DNI del usuario que desea modificar: ")
    usuario_existente = buscar_usuario_por_dni(dni)

    if usuario_existente:
        print("Usuario encontrado. Proporcione la nueva información:")
        nombre = input("Nuevo nombre: ")
        edad = int(input("Nueva edad: "))
        contrasena = input("Nueva contraseña: ")
        
        while True:
            dni = input("Nuevo DNI: ")
            if dni.isdigit() and len(dni) == 8:
                break
            else:
                print("DNI inválido. Intentelo de nuevo.")

        rol = input("Nuevo rol (Administrador/Usuario): ")
        fecha_nacimiento = input("Nueva fecha de Nacimiento (YYYY-MM-DD): ")
        telefono = input("Nuevo teléfono: ")

        nombre, edad, email, contrasena, dni, rol, fecha_nacimiento, telefono = filtrar_datos_usuario(
            nombre, edad, usuario_existente[2], contrasena, dni, rol, fecha_nacimiento, telefono
        )

        with sqlite3.connect('usuarios.db') as conn:
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE usuarios
                SET nombre=?, edad=?, contrasena=?, email=?, dni=?, rol=?, fecha_nacimiento=?, telefono=?
                WHERE dni=?
            ''', (nombre, edad, contrasena, email, dni, rol, fecha_nacimiento, telefono, usuario_existente[4]))

            conn.commit()

            print("Usuario modificado exitosamente.")
    else:
        print("Usuario no encontrado.")

    input("Continua...")
    limpiar_pantalla()

def eliminar_usuario():
    dni = input("Ingrese el DNI del usuario que desea eliminar: ")
    usuario_existente = buscar_usuario_por_dni(dni)

    if usuario_existente:
        with sqlite3.connect('usuarios.db') as conn:
            cursor = conn.cursor()

            cursor.execute('DELETE FROM usuarios WHERE dni=?', (dni,))

            conn.commit()

            print("Usuario eliminado exitosamente.")
    else:
        print("Usuario no encontrado.")

    input("Continua...")
    limpiar_pantalla()

def iniciar_sesion():
    dni = input("DNI: ")
    usuario_existente = buscar_usuario_por_dni(dni)

    if usuario_existente:
        email = input("Email: ")
        contrasena = input("Contraseña: ")

        if usuario_existente[2] == email and usuario_existente[3] == contrasena:
            print("Inicio de sesión exitoso.")
        else:
            print("Credenciales incorrectas.")
    else:
        print("Usuario no encontrado.")

    input("Continua...")
    limpiar_pantalla()


def comprobar_edad_usuario():
    dni = input("Ingrese el DNI del usuario para comprobar la edad: ")
    usuario_existente = buscar_usuario_por_dni(dni)

    if usuario_existente:
        print(f"La edad del usuario {usuario_existente[0]} es: {usuario_existente[1]} años.")
    else:
        print("Usuario no encontrado.")

    input("Continua...")
    limpiar_pantalla()

def recuperar_contrasena():
    dni = input("Ingrese el DNI del usuario para recuperar la contraseña: ")
    usuario_existente = buscar_usuario_por_dni(dni)

    if usuario_existente:
        print(f"La contraseña del usuario {usuario_existente[0]} es: {usuario_existente[3]}")
    else:
        print("Usuario no encontrado.")

    input("Continua...")
    limpiar_pantalla()


def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def menu():
    while True:
        print("1. Crear usuario")
        print("2. Modificar Usuario")
        print("3. Eliminar Usuario")
        print("4. Iniciar sesión")
        print("5. Comprobar la edad de un usuario")
        print("6. Recuperar contraseña")
        print("7. Listado de usuarios")
        print("8. Salir")
        opcion = input("Elige una opción: ")

        if opcion == '1':
            crear_usuario()
        elif opcion == '2':
            modificar_usuario()
        elif opcion == '3':
            eliminar_usuario()
        elif opcion == '4':
            iniciar_sesion()
        elif opcion == '5':
            comprobar_edad_usuario()
        elif opcion == '6':
            recuperar_contrasena()
        elif opcion == '7':
            listar_usuarios()
        elif opcion == '8':
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")

menu()
