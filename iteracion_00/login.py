import hashlib
import os
import sqlite3
import tkinter as tk
from tkinter import messagebox


# =======================================
# CONFIGURACIÓN DE RUTAS Y BASE DE DATOS
# =======================================

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
CARPETA_DB = os.path.join(DIRECTORIO_ACTUAL, "db")
DB_PATH = os.path.join(CARPETA_DB, "frankie_gestor.db")


def hash_password(password: str) -> bytes:
    """Genera un hash SHA-256 en formato binario."""
    return hashlib.sha256(password.encode("utf-8")).digest()


def inicializar_seguridad():
    """Crea la tabla de usuarios y agrega o migra el usuario administrador."""
    os.makedirs(CARPETA_DB, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conexion:
        cursor = conexion.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombres TEXT NOT NULL,
                apellidos TEXT NOT NULL,
                usuario TEXT UNIQUE NOT NULL,
                password BLOB NOT NULL,
                rol TEXT NOT NULL
            )
            """
        )

        # Migra contraseñas antiguas almacenadas como texto plano.
        cursor.execute("SELECT id, password FROM usuarios")
        usuarios = cursor.fetchall()

        for usuario_id, password in usuarios:
            if isinstance(password, str):
                cursor.execute(
                    """
                    UPDATE usuarios
                    SET password = ?
                    WHERE id = ?
                    """,
                    (hash_password(password), usuario_id),
                )

        # Crea el administrador inicial si no existe ningún usuario.
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        cantidad_usuarios = cursor.fetchone()[0]

        if cantidad_usuarios == 0:
            cursor.execute(
                """
                INSERT INTO usuarios
                    (nombres, apellidos, usuario, password, rol)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "David Hernan",
                    "Bravo",
                    "admin",
                    hash_password("admin123"),
                    "Administrador",
                ),
            )

        conexion.commit()


class LoginApp:
    """Interfaz gráfica y lógica de autenticación."""

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
            self.root,
            text="SISTEMA DE GESTIÓN",
            font=("Arial", 12, "bold"),
        ).pack(pady=15)

        tk.Label(self.root, text="Usuario:").pack()

        self.caja_usuario = tk.Entry(self.root, width=30)
        self.caja_usuario.pack(pady=5)
        self.caja_usuario.focus_set()

        tk.Label(self.root, text="Contraseña:").pack()

        self.caja_password = tk.Entry(
            self.root,
            width=30,
            show="*",
        )
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

        self.root.bind("<Return>", self._ingresar_con_enter)

    def _ingresar_con_enter(self, event=None):
        self.validar_ingreso()

    def limpiar_campos(self):
        """Limpia los campos del formulario."""
        self.caja_usuario.delete(0, tk.END)
        self.caja_password.delete(0, tk.END)
        self.caja_usuario.focus_set()

    def autenticar_usuario(
        self,
        usuario: str,
        password_plana: str,
    ):
        """Busca el usuario comparando el hash de la contraseña."""
        try:
            password_hash = hash_password(password_plana)

            with sqlite3.connect(DB_PATH) as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    SELECT nombres, rol
                    FROM usuarios
                    WHERE usuario = ?
                      AND password = ?
                    """,
                    (usuario, password_hash),
                )

                return cursor.fetchone()

        except sqlite3.Error as error:
            messagebox.showerror(
                "Error de consulta",
                f"Ocurrió un error al autenticar:\n{error}",
            )
            return None

    def validar_ingreso(self):
        """Valida las credenciales ingresadas por el usuario."""
        usuario = self.caja_usuario.get().strip()
        password = self.caja_password.get().strip()

        if not usuario or not password:
            messagebox.showwarning(
                "Validación",
                "Por favor, completá todos los campos.",
            )
            return

        resultado = self.autenticar_usuario(usuario, password)

        if resultado:
            nombres_usuario, rol_usuario = resultado
            self.intentos_fallidos = 0

            messagebox.showinfo(
                "Acceso concedido",
                f"Bienvenido/a, {nombres_usuario}.\n"
                f"Rol: {rol_usuario}",
            )

            self.limpiar_campos()
            self.root.withdraw()

            try:
                from panel_control import PanelControl

                PanelControl(
                    self.root,
                    rol_usuario,
                    nombres_usuario,
                )

            except Exception as error:
                messagebox.showerror(
                    "Error al cargar el panel",
                    f"No se pudo abrir 'panel_control.py':\n{error}",
                )
                self.root.deiconify()

        else:
            self.intentos_fallidos += 1
            intentos_restantes = (
                self.max_intentos - self.intentos_fallidos
            )

            self.limpiar_campos()

            if intentos_restantes > 0:
                messagebox.showerror(
                    "Error de autenticación",
                    "Credenciales incorrectas.\n"
                    f"Intentos restantes: {intentos_restantes}",
                )
            else:
                messagebox.showerror(
                    "Bloqueo de seguridad",
                    "Superaste el límite de intentos fallidos. "
                    "El sistema se cerrará.",
                )
                self.root.destroy()


if __name__ == "__main__":
    try:
        root = tk.Tk()
        inicializar_seguridad()
        app = LoginApp(root)
        root.mainloop()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Error de base de datos",
            f"No se pudo inicializar la base de datos:\n{error}",
        )
