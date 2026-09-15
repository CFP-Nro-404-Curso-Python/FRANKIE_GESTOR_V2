import tkinter as tk
from tkinter import messagebox
import os
# Carga un módulo de la biblioteca estándar dedicado a realizar operaciones de alto nivel en archivos y directorios.
import shutil
from datetime import datetime



class PanelControl(tk.Toplevel):
    def __init__(self, parent, rol_usuario, nombres_usuario):
        super().__init__(parent)
        
        self.title(f"PANEL DE CONTROL - {rol_usuario.upper()}")
        self.geometry("650x550")
        self.resizable(False, False)
        # Aplicamos un color de fondo neutro para resaltar los botones.
        self.configure(bg="#f0f2f5")

        # Al cerrar esta ventana con la "X", cerramos toda la aplicación (mata el root).
        self.protocol("WM_DELETE_WINDOW", parent.destroy)



        # ======================================
        #  RUTINAS DE NAVEGACIÓN (LAZY IMPORTS)
        # ======================================

        def abrir_clientes():
            from clientes import Cliente
            Cliente(self)

        def abrir_empleados():
            from empleados import Empleado
            Empleado(self)

        def abrir_proveedores():
            from proveedores import Proveedor
            Proveedor(self)

        def abrir_stock():
            from stock import Stock
            Stock(self)

        def abrir_facturacion():
            from facturacion import Facturacion
            Facturacion(self)
            
        def abrir_usuarios():
            from usuarios import Usuario
            Usuario(self, rol_usuario)
            
        def abrir_consola():
            from consola import ConsolaSQL
            ConsolaSQL(self)
            
        def generar_backup():
            try:
                directorio_actual = os.path.dirname(os.path.abspath(__file__))
                ruta_db = os.path.join(directorio_actual, "db", "frankie_gestor.db")
                
                if not os.path.exists(ruta_db):
                    messagebox.showerror("Error", "No se encontró la base de datos para respaldar.")
                    return
                
                # Creamos la carpeta de backups si no existe.
                carpeta_backup = os.path.join(directorio_actual, "backups")
                os.makedirs(carpeta_backup, exist_ok=True)
                
                # Generamos un nombre de archivo con marca de tiempo.
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") # Patrón de formato de fecha y hora.
                nombre_backup = f"backup_frankie_{timestamp}.db"
                ruta_destino = os.path.join(carpeta_backup, nombre_backup)
                
                shutil.copy2(ruta_db, ruta_destino)
                messagebox.showinfo("Backup Exitoso", f"Copia de seguridad guardada como:\n{nombre_backup}")
            except Exception as e:
                messagebox.showerror("Error de Backup", f"Fallo al generar la copia: {e}")

        def cerrar_sesion():
            self.destroy()
            parent.deiconify() # Vuelve a mostrar el login original.



        # ===========================
        #  MATRIZ DE PERMISOS (RBAC)
        # ===========================

        # Definimos qué roles tienen acceso normal a cada módulo. Si el rol no está en la lista, queda DISABLED.
        p_clientes = tk.NORMAL if rol_usuario in ["Administrador", "Gerente", "Empleado - Ventas"] else tk.DISABLED
        p_facturacion = tk.NORMAL if rol_usuario in ["Administrador", "Gerente", "Empleado - Ventas"] else tk.DISABLED
        
        p_proveedores = tk.NORMAL if rol_usuario in ["Administrador", "Gerente", "Empleado - Compras"] else tk.DISABLED
        p_stock = tk.NORMAL if rol_usuario in ["Administrador", "Gerente", "Empleado - Compras"] else tk.DISABLED
        
        p_empleados = tk.NORMAL if rol_usuario in ["Administrador", "Gerente"] else tk.DISABLED
        p_usuarios = tk.NORMAL if rol_usuario in ["Administrador", "Gerente"] else tk.DISABLED
        
        p_root = tk.NORMAL if rol_usuario == "Administrador" else tk.DISABLED



        # ============================
        #  INTERFAZ GRÁFICA Y ESTILOS
        # ============================

        tk.Label(self, text=f"BIENVENIDO/A, {nombres_usuario.upper()}", font=("Arial", 16, "bold"), bg="#f0f2f5", fg="#333333").pack(pady=(20, 5))
        tk.Label(self, text=f"Rol Activo: {rol_usuario}", font=("Arial", 11, "italic"), bg="#f0f2f5", fg="#666666").pack(pady=(0, 20))

        # Contenedor para la grilla de botones.
        frame_botones = tk.Frame(self, bg="#f0f2f5")
        frame_botones.pack(expand=True)

        # Configuración visual de botones estándar (Azul corporativo).
        estilo_btn = {"font": ("Arial", 11, "bold"), "bg": "#2196F3", "fg": "white", "width": 20, "height": 2}
        
        # Fila 1: Operaciones de Ventas.
        tk.Button(frame_botones, text="Gestión de Clientes", command=abrir_clientes, state=p_clientes, **estilo_btn).grid(row=0, column=0, padx=15, pady=15)
        tk.Button(frame_botones, text="Facturación", command=abrir_facturacion, state=p_facturacion, **estilo_btn).grid(row=0, column=1, padx=15, pady=15)

        # Fila 2: Operaciones de Compras.
        tk.Button(frame_botones, text="Gestión de Proveedores", command=abrir_proveedores, state=p_proveedores, **estilo_btn).grid(row=1, column=0, padx=15, pady=15)
        tk.Button(frame_botones, text="Control de Stock", command=abrir_stock, state=p_stock, **estilo_btn).grid(row=1, column=1, padx=15, pady=15)

        # Fila 3: Recursos Humanos y Accesos (Tonos anaranjados/violetas para diferenciar).
        tk.Button(frame_botones, text="Recursos Humanos", command=abrir_empleados, state=p_empleados, font=("Arial", 11, "bold"), bg="#FF9800", fg="white", width=20, height=2).grid(row=2, column=0, padx=15, pady=15)
        tk.Button(frame_botones, text="Gestión de Usuarios", command=abrir_usuarios, state=p_usuarios, font=("Arial", 11, "bold"), bg="#9C27B0", fg="white", width=20, height=2).grid(row=2, column=1, padx=15, pady=15)

        # Fila 4: Herramientas ROOT (Tonos oscuros/grises).
        tk.Button(frame_botones, text="Consola SQL (Auditoría)", command=abrir_consola, state=p_root, font=("Arial", 11, "bold"), bg="#607D8B", fg="white", width=20, height=2).grid(row=3, column=0, padx=15, pady=15)
        tk.Button(frame_botones, text="Generar Backup DB", command=generar_backup, state=p_root, font=("Arial", 11, "bold"), bg="#37474F", fg="white", width=20, height=2).grid(row=3, column=1, padx=15, pady=15)

        # Botón de Cerrar Sesión (Rojo).
        tk.Button(self, text="Cerrar Sesión", command=cerrar_sesion, font=("Arial", 10, "bold"), bg="#F44336", fg="white", width=15).pack(pady=20)