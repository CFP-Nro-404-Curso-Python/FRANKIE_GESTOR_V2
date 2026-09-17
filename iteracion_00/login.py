import hashlib
import os
import sqlite3
import sys
import tkinter as tk
from tkinter import messagebox

# =======================================
#  CONFIGURACIÓN DE RUTAS Y BASE DE DATOS
# =======================================

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
CARPETA_DB = os.path.join(DIRECTORIO_ACTUAL, "db")
os.makedirs(CARPETA_DB, exist_ok=True)
DB_PATH = os.path.join(CARPETA_DB, "frankie_gestor.db")


def hash_password(password: str) -> bytes:
    """Genera un hash SHA-256 en formato binario (bytes)."""
    return hashlib.sha256(password.encode("utf-8")).digest()


def inicializar_seguridad():
    """Crea la estructura de usuarios e inserta el admin maestro si no existe."""
    with sqlite3.connect(DB_PATH) as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombres TEXT,
                apellidos TEXT,
                usuario TEXT UNIQUE,
                password BLOB,
                rol TEXT
            )
        """
        )

        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            # Se guarda la contraseña en binario (bytes) en la columna BLOB
            admin_pass_bytes = hash_password("admin123")
            cursor.execute(
                """
                INSERT INTO usuarios (nombres, apellidos, usuario, password, rol) 
                VALUES ('David Hernan', 'Bravo', 'admin', ?, 'Administrador')
            """,
                (admin_pass_bytes,),
            )
        conexion.commit()


# =======================================
#  CLASE DE LA INTERFAZ DE LOGIN (GUI)
# =======================================


class LoginApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("FRANKIE GESTOR - ACCESO AL SISTEMA")
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        self.root.eval("tk::PlaceWindow . center")

        self.intentos_fallidos = 0
        self.max_intentos = 3

        self._crear_widgets()

    def _crear_widgets(self):
        tk.Label(
            self.root, text="SISTEMA DE GESTIÓN", font=("Arial", 12, "bold")
        ).pack(pady=15)

        tk.Label(self.root, text="Usuario:").pack()
        self.caja_usuario = tk.Entry(self.root, width=30)
        self.caja_usuario.pack(pady=5)
        self.caja_usuario.focus_set()

        tk.Label(self.root, text="Contraseña:").pack()
        self.caja_password = tk.Entry(self.root, width=30, show="*")
        self.caja_password.pack(pady=5)

        self.boton_ingresar = tk.Button(
            self.root,
            text="Ingresar al Sistema",
            command=self.validar_ingreso,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
        )
        self.boton_ingresar.pack(pady=20)

        self.root.bind("<Return>", lambda event: self.validar_ingreso())

    def limpiar_campos(self):
        self.caja_usuario.delete(0, tk.END)
        self.caja_password.delete(0, tk.END)
        self.caja_usuario.focus_set()

    def autenticar_usuario(self, usuario: str, password_plana: str):
        """Consulta la base de datos comparando los bytes del hash."""
        password_binaria = hash_password(password_plana)
        with sqlite3.connect(DB_PATH) as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT nombres, rol FROM usuarios WHERE usuario=? AND password=?",
                (usuario, password_binaria),
            )
            return cursor.fetchone()

    def validar_ingreso(self):
        usuario = self.caja_usuario.get().strip()
        password = self.caja_password.get().strip()

        if not usuario or not password:
            messagebox.showwarning(
                "Validación", "Por favor, completá todos los campos."
            )
            return

        resultado = self.autenticar_usuario(usuario, password)

        if resultado:
            nombres_usuario, rol_usuario = resultado
            self.intentos_fallidos = 0

            messagebox.showinfo(
                "Acceso Concedido",
                f"Bienvenido/a, {nombres_usuario}.\nRol: {rol_usuario}",
            )

            self.limpiar_campos()
            self.root.withdraw()

            try:
                from panel_control import PanelControl

                PanelControl(self.root, rol_usuario, nombres_usuario)
            except ImportError:
                messagebox.showerror(
                    "Error de Módulo",
                    "No se encontró el archivo 'panel_control.py'.",
                )
                self.root.deiconify()
        else:
            self.intentos_fallidos += 1
            intentos_restantes = self.max_intentos - self.intentos_fallidos
            self.limpiar_campos()

            if intentos_restantes > 0:
                messagebox.showerror(
                    "Error de Autenticación",
                    f"Credenciales incorrectas.\nIntentos restantes: {intentos_restantes}",
                )
            else:
                messagebox.showerror(
                    "Bloqueo de Seguridad",
                    "Superaste el límite de intentos fallidos. El sistema se cerrará.",
                )
                self.root.destroy()


# =======================================
#  PUNTO DE ENTRADA PRINCIPAL
# =======================================

if __name__ == "__main__":
    inicializar_seguridad()
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
