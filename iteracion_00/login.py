import tkinter as tk
from tkinter import messagebox
import sqlite3
import os



# =======================================
#  ANCLAJE DE DIRECTORIO Y BASE DE DATOS
# =======================================

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
CARPETA_DB = os.path.join(DIRECTORIO_ACTUAL, "db")
os.makedirs(CARPETA_DB, exist_ok=True)
DB_PATH = os.path.join(CARPETA_DB, "frankie_gestor.db")

def inicializar_seguridad():
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    
    # DDL: Tabla independiente de usuarios para el RBAC (Role-Based Access Control).
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            password TEXT,
            rol TEXT
        )
    ''')
    
    # Semilla (Seed) del sistema: Si la tabla está vacía, creamos el Administrador maestro.
    # Es imposible operar el sistema por primera vez sin este paso.
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO usuarios (usuario, password, rol) 
            VALUES ('admin', 'admin123', 'Administrador')
        ''')
    
    conexion.commit()
    conexion.close()

# Ejecutamos la inicialización al arrancar.
inicializar_seguridad()



# =====================================
#  CREACIÓN DE LA VENTANA RAÍZ "LOGIN"
# =====================================

ventana = tk.Tk()
ventana.title("FRANKIE GESTOR - ACCESO AL SISTEMA")
ventana.geometry("400x250")
ventana.eval('tk::PlaceWindow . center') # Centramos la ventana de login.
ventana.resizable(False, False)

# Variable global para el control de intentos.
intentos_fallidos = 0

def validar_ingreso():
    global intentos_fallidos
    
    usuario_ingresado = caja_usuario.get()
    password_ingresada = caja_password.get()
    
    if not usuario_ingresado or not password_ingresada:
        messagebox.showwarning("Validación", "Completá todos los campos.")
        return
        
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    
    # Prevención de Inyección SQL mediante paso de parámetros (?).
    cursor.execute("SELECT rol FROM usuarios WHERE usuario=? AND password=?", (usuario_ingresado, password_ingresada))
    resultado = cursor.fetchone()
    conexion.close()
    
    if resultado:
        rol_usuario = resultado[0]
        messagebox.showinfo("Acceso Concedido", f"Bienvenido/a. Rol: {rol_usuario}")
        
        # Limpieza de seguridad antes de ocultar la ventana.
        caja_usuario.delete(0, tk.END)
        caja_password.delete(0, tk.END)
        caja_usuario.focus_set()
        
        # Ocultamos la ventana de login, no la destruimos porque es el tk.Tk() principal.
        ventana.withdraw()
        
        # Lazy Import del futuro Panel de Control (panel_control).
        from panel_control import PanelControl
        # Le pasamos la ventana raíz y el rol validado para que el Panel de Control aplique las restricciones.
        PanelControl(ventana, rol_usuario)
    else:
        intentos_fallidos += 1
        intentos_restantes = 3 - intentos_fallidos
        
        # Vaciamos ambas cajas por seguridad y para forzar el reingreso.
        caja_usuario.delete(0, tk.END)
        caja_password.delete(0, tk.END)
        caja_usuario.focus_set()
        
        if intentos_restantes > 0:
            messagebox.showerror("Error de Autenticación", f"Credenciales incorrectas. Intentos restantes: {intentos_restantes}")
        else:
            messagebox.showerror("Bloqueo de Seguridad", "Superaste el límite de intentos fallidos. El sistema se cerrará.")
            ventana.destroy()



# ===================
#  INTERFAZ DE LOGIN
# ===================

tk.Label(ventana, text="SISTEMA DE GESTIÓN", font=("Arial", 12, "bold")).pack(pady=15)

tk.Label(ventana, text="Usuario:").pack()
caja_usuario = tk.Entry(ventana, width=30)
caja_usuario.pack(pady=5)

tk.Label(ventana, text="Contraseña:").pack()
# show="*" enmascara los caracteres tipeados para que no se vean en pantalla.
caja_password = tk.Entry(ventana, width=30, show="*")
caja_password.pack(pady=5)

boton_ingresar = tk.Button(ventana, text="Ingresar al Sistema", command=validar_ingreso, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
boton_ingresar.pack(pady=20)

# UX: Permite enviar el formulario presionando la tecla Enter.
ventana.bind('<Return>', lambda event: validar_ingreso())

ventana.mainloop()