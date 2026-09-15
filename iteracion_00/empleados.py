import tkinter as tk
from tkinter import ttk
import sqlite3
import os



class Empleado(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("FORMULARIO EMPLEADOS")
        self.geometry("1005x550")



        # =======================================
        #  ANCLAJE DE DIRECTORIO Y BASE DE DATOS
        # =======================================
        
        DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
        CARPETA_DB = os.path.join(DIRECTORIO_ACTUAL, "db")
        os.makedirs(CARPETA_DB, exist_ok=True)
        DB_PATH = os.path.join(CARPETA_DB, "frankie_gestor.db")



        # ===========================================
        #  FUNCIONALIDADES DE "FORMULARIO EMPLEADOS"
        # ===========================================

        def crear_tabla_empleados():
            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS empleados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombres TEXT,
                    apellidos TEXT,
                    dni TEXT,
                    telefono TEXT,
                    email TEXT,
                    domicilio TEXT,
                    legajo TEXT,
                    cargo TEXT,
                    sector TEXT,
                    sueldo TEXT
                )
            ''')

            conexion.commit()
            conexion.close()

        def cargar_datos_db():
            for item in tabla.get_children():
                tabla.delete(item)
                
            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            cursor.execute("SELECT * FROM empleados")
            filas = cursor.fetchall()
            
            for fila in filas:
                tabla.insert("", "end", iid=fila[0], values=fila[1:])

            conexion.close()

        def limpiar_campos():
            cajas = [caja_nombres, caja_apellidos, caja_dni, caja_telefono, caja_email, caja_domicilio, caja_legajo, caja_cargo, caja_sector, caja_sueldo]
            for caja in cajas:
                caja.delete(0, tk.END)
            caja_nombres.focus_set()

        def guardar():
            nombres = caja_nombres.get()
            apellidos = caja_apellidos.get()
            dni = caja_dni.get()
            telefono = caja_telefono.get()
            email = caja_email.get()
            domicilio = caja_domicilio.get()
            legajo = caja_legajo.get()
            cargo = caja_cargo.get()
            sector = caja_sector.get()
            sueldo = caja_sueldo.get()

            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            cursor.execute('''
                INSERT INTO empleados (nombres, apellidos, dni, telefono, email, domicilio, legajo, cargo, sector, sueldo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nombres, apellidos, dni, telefono, email, domicilio, legajo, cargo, sector, sueldo))

            conexion.commit()
            conexion.close()

            limpiar_campos()
            cargar_datos_db()

        def seleccionar_fila(event):
            seleccion = tabla.selection()
            if not seleccion:
                return
                
            valores = tabla.item(seleccion[0], "values")
            
            cajas = [caja_nombres, caja_apellidos, caja_dni, caja_telefono, caja_email, caja_domicilio, caja_legajo, caja_cargo, caja_sector, caja_sueldo]
                     
            for i, caja in enumerate(cajas):
                caja.delete(0, tk.END)
                caja.insert(0, valores[i])

        def modificar():
            seleccion = tabla.selection()
            if not seleccion:
                return
            
            id_empleado = seleccion[0]
            
            nombres = caja_nombres.get()
            apellidos = caja_apellidos.get()
            dni = caja_dni.get()
            telefono = caja_telefono.get()
            email = caja_email.get()
            domicilio = caja_domicilio.get()
            legajo = caja_legajo.get()
            cargo = caja_cargo.get()
            sector = caja_sector.get()
            sueldo = caja_sueldo.get()

            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            cursor.execute('''
                UPDATE empleados SET 
                nombres=?, apellidos=?, dni=?, telefono=?, email=?, domicilio=?, legajo=?, cargo=?, sector=?, sueldo=?
                WHERE id=?
            ''', (nombres, apellidos, dni, telefono, email, domicilio, legajo, cargo, sector, sueldo, id_empleado))
            
            conexion.commit()
            conexion.close()

            limpiar_campos()
            cargar_datos_db()

        def eliminar():
            seleccion = tabla.selection()
            if not seleccion:
                return
                
            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()
            
            for item in seleccion:
                cursor.execute("DELETE FROM empleados WHERE id=?", (item,))
                
            conexion.commit()
            conexion.close()
            
            limpiar_campos()
            cargar_datos_db()



        # ===================================
        #  CAMPOS DEL "FORMULARIO EMPLEADOS"
        # ===================================

        tk.Label(self, text="Nombres").grid(row=1, column=0, pady=5, sticky="e", padx=5)
        caja_nombres = tk.Entry(self)
        caja_nombres.grid(row=1, column=1)

        tk.Label(self, text="Apellidos").grid(row=2, column=0, pady=5, sticky="e", padx=5)
        caja_apellidos = tk.Entry(self)
        caja_apellidos.grid(row=2, column=1)

        tk.Label(self, text="DNI").grid(row=3, column=0, pady=5, sticky="e", padx=5)
        caja_dni = tk.Entry(self)
        caja_dni.grid(row=3, column=1)

        tk.Label(self, text="Teléfono").grid(row=4, column=0, pady=5, sticky="e", padx=5)
        caja_telefono = tk.Entry(self)
        caja_telefono.grid(row=4, column=1)

        tk.Label(self, text="Email").grid(row=5, column=0, pady=5, sticky="e", padx=5)
        caja_email = tk.Entry(self)
        caja_email.grid(row=5, column=1)

        tk.Label(self, text="Domicilio").grid(row=6, column=0, pady=5, sticky="e", padx=5)
        caja_domicilio = tk.Entry(self)
        caja_domicilio.grid(row=6, column=1)

        tk.Label(self, text="Legajo").grid(row=7, column=0, pady=5, sticky="e", padx=5)
        caja_legajo = tk.Entry(self)
        caja_legajo.grid(row=7, column=1)

        tk.Label(self, text="Cargo").grid(row=8, column=0, pady=5, sticky="e", padx=5)
        caja_cargo = tk.Entry(self)
        caja_cargo.grid(row=8, column=1)

        tk.Label(self, text="Sector").grid(row=9, column=0, pady=5, sticky="e", padx=5)
        caja_sector = tk.Entry(self)
        caja_sector.grid(row=9, column=1)

        tk.Label(self, text="Sueldo").grid(row=10, column=0, pady=5, sticky="e", padx=5)
        caja_sueldo = tk.Entry(self)
        caja_sueldo.grid(row=10, column=1)



        # =========================================================
        #  BOTONES "GUARDAR, MODIFICAR, ELIMINAR Y CERRAR VENTANA"
        # =========================================================

        boton_guardar = tk.Button(self, text="Guardar Empleado", command=guardar, bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), width=15)
        boton_guardar.grid(row=3, column=3, padx=20)

        boton_modificar = tk.Button(self, text="Modificar Empleado", command=modificar, bg="#2196F3", fg="white", font=("Arial", 9, "bold"), width=15)
        boton_modificar.grid(row=5, column=3, padx=20)

        boton_eliminar = tk.Button(self, text="Eliminar Empleado", command=eliminar, bg="#F44336", fg="white", font=("Arial", 9, "bold"), width=15)
        boton_eliminar.grid(row=7, column=3, padx=20)

        boton_cerrar_ventana = tk.Button(self, text="Cerrar Ventana", command=self.destroy, bg="#9E9E9E", fg="white", font=("Arial", 9, "bold"), width=15)
        boton_cerrar_ventana.grid(row=9, column=3, padx=20)



        # =============================
        #  TABLA DE DATOS DE EMPLEADOS
        # =============================

        columnas = ("Nombres", "Apellidos", "DNI", "Teléfono", "Email", "Domicilio", "Legajo", "Cargo", "Sector", "Sueldo")

        tabla = ttk.Treeview(self, columns=columnas, show="headings", height=10)

        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, width=100)

        tabla.grid(row=11, column=0, columnspan=5, pady=20, padx=10)
        tabla.bind("<<TreeviewSelect>>", seleccionar_fila)



        # ========================
        #  CARGA INICIAL DE DATOS
        # ========================
        
        crear_tabla_empleados()
        cargar_datos_db()