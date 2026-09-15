import tkinter as tk
from tkinter import ttk
import sqlite3
import os



class Cliente(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("FORMULARIO CLIENTES")
        self.geometry("1005x550")
        


        # =======================================
        #  ANCLAJE DE DIRECTORIO Y BASE DE DATOS
        # =======================================

        DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
        DB_PATH = os.path.join(DIRECTORIO_ACTUAL, "db", "frankie_gestor.db")



        # ==========================================
        #  FUNCIONALIDADES DE "FORMULARIO CLIENTES"
        # ==========================================
        
        # Nota: La creación de la tabla (DDL) se omitió acá porque tenemos que asegurarnos de que las tablas maestras 
        # se creen al iniciar o mantener el DDL si este módulo es el único responsable de esta tabla.
        # Por seguridad y atomicidad, mantenemos la función DDL.
        def crear_tabla_clientes():
            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombres TEXT,
                    apellidos TEXT,
                    dni TEXT,
                    edad TEXT,
                    telefono TEXT,
                    email TEXT,
                    domicilio TEXT,
                    ciudad TEXT,
                    provincia TEXT,
                    codigo_postal TEXT
                )
            ''')

            conexion.commit()
            conexion.close()

        def cargar_datos_db():
            for item in tabla.get_children():
                tabla.delete(item)
                
            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            cursor.execute("SELECT * FROM clientes")
            filas = cursor.fetchall()
            
            for fila in filas:
                tabla.insert("", "end", iid=fila[0], values=fila[1:])

            conexion.close()

        def limpiar_campos():
            cajas = [caja_nombres, caja_apellidos, caja_dni, caja_edad, caja_telefono, caja_email, 
                     caja_domicilio, caja_ciudad, caja_provincia, caja_codigo_postal]
                     
            for caja in cajas:
                caja.delete(0, tk.END)
            caja_nombres.focus_set()

        def guardar():
            nombres = caja_nombres.get()
            apellidos = caja_apellidos.get()
            dni = caja_dni.get()
            edad = caja_edad.get()
            telefono = caja_telefono.get()
            email = caja_email.get()
            domicilio = caja_domicilio.get()
            ciudad = caja_ciudad.get()
            provincia = caja_provincia.get()
            codigo_postal = caja_codigo_postal.get()

            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            cursor.execute('''
                INSERT INTO clientes (nombres, apellidos, dni, edad, telefono, email, domicilio, ciudad, provincia, codigo_postal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nombres, apellidos, dni, edad, telefono, email, domicilio, ciudad, provincia, codigo_postal))
            
            conexion.commit()
            conexion.close()
            
            limpiar_campos()
            cargar_datos_db()

        def seleccionar_fila(event):
            seleccion = tabla.selection()
            if not seleccion:
                return
                
            valores = tabla.item(seleccion[0], "values")
            
            cajas = [caja_nombres, caja_apellidos, caja_dni, caja_edad, caja_telefono, caja_email, 
                     caja_domicilio, caja_ciudad, caja_provincia, caja_codigo_postal]
                     
            for i, caja in enumerate(cajas):
                caja.delete(0, tk.END)
                caja.insert(0, valores[i])

        def modificar():
            seleccion = tabla.selection()
            if not seleccion:
                return
            
            id_cliente = seleccion[0]
            
            nombres = caja_nombres.get()
            apellidos = caja_apellidos.get()
            dni = caja_dni.get()
            edad = caja_edad.get()
            telefono = caja_telefono.get()
            email = caja_email.get()
            domicilio = caja_domicilio.get()
            ciudad = caja_ciudad.get()
            provincia = caja_provincia.get()
            codigo_postal = caja_codigo_postal.get()

            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            cursor.execute('''
                UPDATE clientes SET 
                nombres=?, apellidos=?, dni=?, edad=?, telefono=?, email=?, domicilio=?, ciudad=?, provincia=?, codigo_postal=?
                WHERE id=?
            ''', (nombres, apellidos, dni, edad, telefono, email, domicilio, ciudad, provincia, codigo_postal, id_cliente))
            
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
                cursor.execute("DELETE FROM clientes WHERE id=?", (item,))
                
            conexion.commit()
            conexion.close()
            
            limpiar_campos()
            cargar_datos_db()



        # ==================================
        #  CAMPOS DEL "FORMULARIO CLIENTES"
        # ==================================

        tk.Label(self, text="Nombres").grid(row=1, column=0, pady=5, sticky="e", padx=5)
        caja_nombres = tk.Entry(self)
        caja_nombres.grid(row=1, column=1)

        tk.Label(self, text="Apellidos").grid(row=2, column=0, pady=5, sticky="e", padx=5)
        caja_apellidos = tk.Entry(self)
        caja_apellidos.grid(row=2, column=1)

        tk.Label(self, text="DNI").grid(row=3, column=0, pady=5, sticky="e", padx=5)
        caja_dni = tk.Entry(self)
        caja_dni.grid(row=3, column=1)

        tk.Label(self, text="Edad").grid(row=4, column=0, pady=5, sticky="e", padx=5)
        caja_edad = tk.Entry(self)
        caja_edad.grid(row=4, column=1)

        tk.Label(self, text="Teléfono").grid(row=5, column=0, pady=5, sticky="e", padx=5)
        caja_telefono = tk.Entry(self)
        caja_telefono.grid(row=5, column=1)

        tk.Label(self, text="Email").grid(row=6, column=0, pady=5, sticky="e", padx=5)
        caja_email = tk.Entry(self)
        caja_email.grid(row=6, column=1)

        tk.Label(self, text="Domicilio").grid(row=7, column=0, pady=5, sticky="e", padx=5)
        caja_domicilio = tk.Entry(self)
        caja_domicilio.grid(row=7, column=1)

        tk.Label(self, text="Ciudad").grid(row=8, column=0, pady=5, sticky="e", padx=5)
        caja_ciudad = tk.Entry(self)
        caja_ciudad.grid(row=8, column=1)

        tk.Label(self, text="Provincia").grid(row=9, column=0, pady=5, sticky="e", padx=5)
        caja_provincia = tk.Entry(self)
        caja_provincia.grid(row=9, column=1)

        tk.Label(self, text="Código Postal").grid(row=10, column=0, pady=5, sticky="e", padx=5)
        caja_codigo_postal = tk.Entry(self)
        caja_codigo_postal.grid(row=10, column=1)



        # =========================================================
        #  BOTONES "GUARDAR, MODIFICAR, ELIMINAR Y CERRAR VENTANA"
        # =========================================================

        boton_guardar = tk.Button(self, text="Guardar Cliente", command=guardar, bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), width=15)
        boton_guardar.grid(row=3, column=3, padx=20)

        boton_modificar = tk.Button(self, text="Modificar Cliente", command=modificar, bg="#2196F3", fg="white", font=("Arial", 9, "bold"), width=15)
        boton_modificar.grid(row=5, column=3, padx=20)

        boton_eliminar = tk.Button(self, text="Eliminar Cliente", command=eliminar, bg="#F44336", fg="white", font=("Arial", 9, "bold"), width=15)
        boton_eliminar.grid(row=7, column=3, padx=20)

        boton_cerrar_ventana = tk.Button(self, text="Cerrar Ventana", command=self.destroy, bg="#9E9E9E", fg="white", font=("Arial", 9, "bold"), width=15)
        boton_cerrar_ventana.grid(row=9, column=3, padx=20)



        # ============================
        #  TABLA DE DATOS DE CLIENTES
        # ============================
        
        columnas = ("Nombres", "Apellidos", "DNI", "Edad", "Teléfono", "Email", "Domicilio", "Ciudad", "Provincia", "Código Postal")

        tabla = ttk.Treeview(self, columns=columnas, show="headings", height=10)

        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, width=100)

        tabla.grid(row=11, column=0, columnspan=5, pady=20, padx=10)
        tabla.bind("<<TreeviewSelect>>", seleccionar_fila)



        # ========================
        #  CARGA INICIAL DE DATOS
        # ========================
        
        crear_tabla_clientes()
        cargar_datos_db()