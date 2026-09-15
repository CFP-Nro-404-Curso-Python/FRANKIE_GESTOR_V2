import tkinter as tk
from tkinter import ttk
import sqlite3
import os



class Proveedor(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("FORMULARIO PROVEEDORES")
        self.geometry("1005x550")



        # =======================================
        #  ANCLAJE DE DIRECTORIO Y BASE DE DATOS
        # =======================================

        DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
        CARPETA_DB = os.path.join(DIRECTORIO_ACTUAL, "db")
        os.makedirs(CARPETA_DB, exist_ok=True)
        DB_PATH = os.path.join(CARPETA_DB, "frankie_gestor.db")



        # =============================================
        #  FUNCIONALIDADES DE "FORMULARIO PROVEEDORES"
        # =============================================

        def crear_tabla_proveedores():
            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS proveedores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    razon_social TEXT,
                    cuit TEXT,
                    telefono TEXT,
                    email TEXT,
                    domicilio TEXT,
                    ciudad TEXT,
                    provincia TEXT,
                    codigo_postal TEXT,
                    rubro TEXT,
                    contacto TEXT
                )
            ''')

            conexion.commit()
            conexion.close()

        def cargar_datos_db():
            for item in tabla.get_children():
                tabla.delete(item)
                
            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            cursor.execute("SELECT * FROM proveedores")
            filas = cursor.fetchall()
            
            for fila in filas:
                tabla.insert("", "end", iid=fila[0], values=fila[1:])

            conexion.close()

        def limpiar_campos():
            cajas = [caja_razon_social, caja_cuit, caja_telefono, caja_email, caja_domicilio, caja_ciudad, caja_provincia, caja_codigo_postal, caja_rubro, caja_contacto]
                     
            for caja in cajas:
                caja.delete(0, tk.END)
            
            caja_razon_social.focus_set()

        def guardar():
            razon_social = caja_razon_social.get()
            cuit = caja_cuit.get()
            telefono = caja_telefono.get()
            email = caja_email.get()
            domicilio = caja_domicilio.get()
            ciudad = caja_ciudad.get()
            provincia = caja_provincia.get()
            codigo_postal = caja_codigo_postal.get()
            rubro = caja_rubro.get()
            contacto = caja_contacto.get()

            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            cursor.execute('''
                INSERT INTO proveedores (razon_social, cuit, telefono, email, domicilio, ciudad, provincia, codigo_postal, rubro, contacto)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (razon_social, cuit, telefono, email, domicilio, ciudad, provincia, codigo_postal, rubro, contacto))

            conexion.commit()
            conexion.close()

            limpiar_campos()
            cargar_datos_db()

        def seleccionar_fila(event):
            seleccion = tabla.selection()
            if not seleccion:
                return
                
            valores = tabla.item(seleccion[0], "values")
            
            cajas = [caja_razon_social, caja_cuit, caja_telefono, caja_email, caja_domicilio, caja_ciudad, caja_provincia, caja_codigo_postal, caja_rubro, caja_contacto]
                     
            for i, caja in enumerate(cajas):
                caja.delete(0, tk.END)
                caja.insert(0, valores[i])
        
        def modificar():
            seleccion = tabla.selection()
            if not seleccion:
                return
            
            id_proveedor = seleccion[0]
            
            razon_social = caja_razon_social.get()
            cuit = caja_cuit.get()
            telefono = caja_telefono.get()
            email = caja_email.get()
            domicilio = caja_domicilio.get()
            ciudad = caja_ciudad.get()
            provincia = caja_provincia.get()
            codigo_postal = caja_codigo_postal.get()
            rubro = caja_rubro.get()
            contacto = caja_contacto.get()

            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            cursor.execute('''
                UPDATE proveedores SET 
                razon_social=?, cuit=?, telefono=?, email=?, domicilio=?, ciudad=?, provincia=?, codigo_postal=?, rubro=?, contacto=?
                WHERE id=?
            ''', (razon_social, cuit, telefono, email, domicilio, ciudad, provincia, codigo_postal, rubro, contacto, id_proveedor))
            
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
                cursor.execute("DELETE FROM proveedores WHERE id=?", (item,))
                
            conexion.commit()
            conexion.close()
            
            limpiar_campos()
            cargar_datos_db()



        # =====================================
        #  CAMPOS DEL "FORMULARIO PROVEEDORES"
        # =====================================

        tk.Label(self, text="Razón Social").grid(row=1, column=0, pady=5, sticky="e", padx=5)
        caja_razon_social = tk.Entry(self)
        caja_razon_social.grid(row=1, column=1)

        tk.Label(self, text="CUIT").grid(row=2, column=0, pady=5, sticky="e", padx=5)
        caja_cuit = tk.Entry(self)
        caja_cuit.grid(row=2, column=1)

        tk.Label(self, text="Teléfono").grid(row=3, column=0, pady=5, sticky="e", padx=5)
        caja_telefono = tk.Entry(self)
        caja_telefono.grid(row=3, column=1)

        tk.Label(self, text="Email").grid(row=4, column=0, pady=5, sticky="e", padx=5)
        caja_email = tk.Entry(self)
        caja_email.grid(row=4, column=1)

        tk.Label(self, text="Domicilio").grid(row=5, column=0, pady=5, sticky="e", padx=5)
        caja_domicilio = tk.Entry(self)
        caja_domicilio.grid(row=5, column=1)

        tk.Label(self, text="Ciudad").grid(row=6, column=0, pady=5, sticky="e", padx=5)
        caja_ciudad = tk.Entry(self)
        caja_ciudad.grid(row=6, column=1)

        tk.Label(self, text="Provincia").grid(row=7, column=0, pady=5, sticky="e", padx=5)
        caja_provincia = tk.Entry(self)
        caja_provincia.grid(row=7, column=1)

        tk.Label(self, text="Código Postal").grid(row=8, column=0, pady=5, sticky="e", padx=5)
        caja_codigo_postal = tk.Entry(self)
        caja_codigo_postal.grid(row=8, column=1)

        tk.Label(self, text="Rubro").grid(row=9, column=0, pady=5, sticky="e", padx=5)
        caja_rubro = tk.Entry(self)
        caja_rubro.grid(row=9, column=1)

        tk.Label(self, text="Contacto").grid(row=10, column=0, pady=5, sticky="e", padx=5)
        caja_contacto = tk.Entry(self)
        caja_contacto.grid(row=10, column=1)



        # =========================================================
        #  BOTONES "GUARDAR, MODIFICAR, ELIMINAR Y CERRAR VENTANA"
        # =========================================================

        boton_guardar = tk.Button(self, text="Guardar Proveedor", command=guardar, bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), width=15)
        boton_guardar.grid(row=3, column=3, padx=20)

        boton_modificar = tk.Button(self, text="Modificar Proveedor", command=modificar, bg="#2196F3", fg="white", font=("Arial", 9, "bold"), width=15)
        boton_modificar.grid(row=5, column=3, padx=20)

        boton_eliminar = tk.Button(self, text="Eliminar Proveedor", command=eliminar, bg="#F44336", fg="white", font=("Arial", 9, "bold"), width=15)
        boton_eliminar.grid(row=7, column=3, padx=20)

        boton_cerrar_ventana = tk.Button(self, text="Cerrar Ventana", command=self.destroy, bg="#9E9E9E", fg="white", font=("Arial", 9, "bold"), width=15)
        boton_cerrar_ventana.grid(row=9, column=3, padx=20)



        # ===============================
        #  TABLA DE DATOS DE PROVEEDORES
        # ===============================

        columnas = ("Razón Social", "CUIT", "Teléfono", "Email", "Domicilio", "Ciudad", "Provincia", "Código Postal", "Rubro", "Contacto")

        tabla = ttk.Treeview(self, columns=columnas, show="headings", height=10)

        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, width=100)

        tabla.grid(row=11, column=0, columnspan=5, pady=20, padx=10)
        tabla.bind("<<TreeviewSelect>>", seleccionar_fila)



        # ========================
        #  CARGA INICIAL DE DATOS
        # ========================
        
        crear_tabla_proveedores()
        cargar_datos_db()