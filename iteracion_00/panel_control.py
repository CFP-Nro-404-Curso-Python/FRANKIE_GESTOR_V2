from datetime import datetime
import os
import shutil
import sqlite3
import tkinter as tk
from tkinter import messagebox


class PanelControl(tk.Toplevel):

    def __init__(self, parent, rol_usuario, nombres_usuario):
        super().__init__(parent)

        self.parent = parent
        self.rol_usuario = rol_usuario
        self.nombres_usuario = nombres_usuario

        # Configuración principal de la ventana
        self.title(f"PANEL DE CONTROL - {self.rol_usuario.upper()}")
        self.geometry("650x580")
        self.resizable(False, False)
        self.configure(bg="#f0f2f5")

        # Al cerrar con la "X", finalizamos toda la aplicación
        self.protocol("WM_DELETE_WINDOW", self.parent.destroy)

        # Matriz de Permisos (RBAC)
        self._evaluar_permisos()

        # Construcción gráfica
        self._crear_interfaz()

    def _evaluar_permisos(self):
        """Asigna los estados de los botones según el rol del usuario."""
        rol = self.rol_usuario

        self.p_clientes = (
            tk.NORMAL
            if rol in ["Administrador", "Gerente", "Empleado - Ventas"]
            else tk.DISABLED
        )
        self.p_facturacion = (
            tk.NORMAL
            if rol in ["Administrador", "Gerente", "Empleado - Ventas"]
            else tk.DISABLED
        )

        self.p_proveedores = (
            tk.NORMAL
            if rol in ["Administrador", "Gerente", "Empleado - Compras"]
            else tk.DISABLED
        )
        self.p_stock = (
            tk.NORMAL
            if rol in ["Administrador", "Gerente", "Empleado - Compras"]
            else tk.DISABLED
        )

        self.p_empleados = (
            tk.NORMAL if rol in ["Administrador", "Gerente"] else tk.DISABLED
        )
        self.p_usuarios = (
            tk.NORMAL if rol in ["Administrador", "Gerente"] else tk.DISABLED
        )

        self.p_root = tk.NORMAL if rol == "Administrador" else tk.DISABLED

    def _crear_interfaz(self):
        """Construye las etiquetas, contenedores y grilla de botones."""
        # Encabezado
        tk.Label(
            self,
            text=f"BIENVENIDO/A, {self.nombres_usuario.upper()}",
            font=("Arial", 16, "bold"),
            bg="#f0f2f5",
            fg="#333333",
        ).pack(pady=(20, 5))

        tk.Label(
            self,
            text=f"Rol Activo: {self.rol_usuario}",
            font=("Arial", 11, "italic"),
            bg="#f0f2f5",
            fg="#666666",
        ).pack(pady=(0, 20))

        # Contenedor de botones
        frame_botones = tk.Frame(self, bg="#f0f2f5")
        frame_botones.pack(expand=True)

        # Estilo base
        base_btn = {"font": ("Arial", 11, "bold"), "width": 20, "height": 2}

        # Fila 1: Operaciones de Ventas (Azul)
        self._crear_boton(
            frame_botones,
            "Gestión de Clientes",
            self._abrir_clientes,
            self.p_clientes,
            "#2196F3",
            0,
            0,
            base_btn,
        )
        self._crear_boton(
            frame_botones,
            "Facturación",
            self._abrir_facturacion,
            self.p_facturacion,
            "#2196F3",
            0,
            1,
            base_btn,
        )

        # Fila 2: Operaciones de Compras (Azul)
        self._crear_boton(
            frame_botones,
            "Gestión de Proveedores",
            self._abrir_proveedores,
            self.p_proveedores,
            "#2196F3",
            1,
            0,
            base_btn,
        )
        self._crear_boton(
            frame_botones,
            "Control de Stock",
            self._abrir_stock,
            self.p_stock,
            "#2196F3",
            1,
            1,
            base_btn,
        )

        # Fila 3: Recursos Humanos y Usuarios (Naranja / Violeta)
        self._crear_boton(
            frame_botones,
            "Recursos Humanos",
            self._abrir_empleados,
            self.p_empleados,
            "#FF9800",
            2,
            0,
            base_btn,
        )
        self._crear_boton(
            frame_botones,
            "Gestión de Usuarios",
            self._abrir_usuarios,
            self.p_usuarios,
            "#9C27B0",
            2,
            1,
            base_btn,
        )

        # Fila 4: Herramientas ROOT (Grises)
        self._crear_boton(
            frame_botones,
            "Consola SQL (Auditoría)",
            self._abrir_consola,
            self.p_root,
            "#607D8B",
            3,
            0,
            base_btn,
        )
        self._crear_boton(
            frame_botones,
            "Generar Backup DB",
            self._generar_backup,
            self.p_root,
            "#37474F",
            3,
            1,
            base_btn,
        )

        # Botón de Cerrar Sesión (Rojo)
        tk.Button(
            self,
            text="Cerrar Sesión",
            command=self._cerrar_sesion,
            font=("Arial", 10, "bold"),
            bg="#F44336",
            fg="white",
            width=15,
            cursor="hand2",
        ).pack(pady=20)

    def _crear_boton(
        self, parent, text, command, state, bg_color, row, col, base_style
    ):
        """Helper para empaquetar botones con estado y estilos uniformes."""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            state=state,
            bg=bg_color,
            fg="white",
            disabledforeground="#a1a1a1",
            cursor="hand2" if state == tk.NORMAL else "arrow",
            **base_style,
        )
        btn.grid(row=row, column=col, padx=15, pady=12)
        return btn

    # ======================================
    #  RUTINAS DE NAVEGACIÓN Y ACCIONES
    # ======================================

    def _abrir_clientes(self):
        from clientes import Cliente

        Cliente(self)

    def _abrir_empleados(self):
        from empleados import Empleado

        Empleado(self)

    def _abrir_proveedores(self):
        from proveedores import Proveedor

        Proveedor(self)

    def _abrir_stock(self):
        from stock import Stock

        Stock(self)

    def _abrir_facturacion(self):
        from facturacion import Facturacion

        Facturacion(self)

    def _abrir_usuarios(self):
        from usuarios import Usuario

        Usuario(self, self.rol_usuario)

    def _abrir_consola(self):
        from consola import ConsolaSQL

        ConsolaSQL(self)

    def _generar_backup(self):
        """Realiza un respaldo seguro mediante SQLite Backup API."""
        try:
            dir_actual = os.path.dirname(os.path.abspath(__file__))
            ruta_db = os.path.join(dir_actual, "db", "frankie_gestor.db")

            if not os.path.exists(ruta_db):
                messagebox.showerror(
                    "Error", "No se encontró la base de datos original."
                )
                return

            carpeta_backup = os.path.join(dir_actual, "backups")
            os.makedirs(carpeta_backup, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_backup = f"backup_frankie_{timestamp}.db"
            ruta_destino = os.path.join(carpeta_backup, nombre_backup)

            # Uso de sqlite3.backup para garantizar consistencia si la DB está en uso
            with (
                sqlite3.connect(ruta_db) as origen,
                sqlite3.connect(ruta_destino) as destino,
            ):
                origen.backup(destino)

            messagebox.showinfo(
                "Backup Exitoso",
                f"Copia de seguridad consistente generada:\n{nombre_backup}",
            )
        except Exception as e:
            messagebox.showerror(
                "Error de Backup", f"Fallo al generar la copia: {e}"
            )

    def _cerrar_sesion(self):
        self.destroy()
        self.parent.deiconify()
