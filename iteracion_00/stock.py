import tkinter as tk
from tkinter import ttk
import sqlite3
import os



class Stock(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("FORMULARIO STOCK")
        self.geometry("1005x550")



        # =======================================
        #  ANCLAJE DE DIRECTORIO Y BASE DE DATOS
        # =======================================

        DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
        CARPETA_DB = os.path.join(DIRECTORIO_ACTUAL, "db")
        os.makedirs(CARPETA_DB, exist_ok=True)
        DB_PATH = os.path.join(CARPETA_DB, "frankie_gestor.db")



        # =======================================
        #  FUNCIONALIDADES DE "FORMULARIO STOCK"
        # =======================================

        def crear_tabla_stock():
            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT,
                    descripcion TEXT,
                    categoria TEXT,
                    proveedor TEXT,
                    stock_actual TEXT,
                    stock_minimo TEXT,
                    precio_costo TEXT,
                    precio_venta TEXT,
                    ubicacion TEXT,
                    vencimiento TEXT
                )
            ''')

            conexion.commit()
            conexion.close()

        def obtener_proveedores():
            lista_provs = []
            if os.path.exists(DB_PATH):
                conexion = sqlite3.connect(DB_PATH)
                cursor = conexion.cursor()

                try:
                    cursor.execute("SELECT razon_social FROM proveedores")
                    filas = cursor.fetchall()
                    for fila in filas:
                        lista_provs.append(fila[0])
                except sqlite3.OperationalError:
                    pass

                conexion.close()

            return lista_provs

        def cargar_datos_db():
            for item in tabla.get_children():
                tabla.delete(item)
                
            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            cursor.execute("SELECT * FROM stock")
            filas = cursor.fetchall()
            
            for fila in filas:
                tabla.insert("", "end", iid=fila[0], values=fila[1:])

            conexion.close()

        def limpiar_campos():
            cajas = [caja_codigo, caja_descripcion, caja_categoria, caja_stock_actual, caja_stock_minimo, caja_precio_costo, 
                     caja_precio_venta, caja_ubicacion, caja_vencimiento]
                     
            for caja in cajas:
                caja.delete(0, tk.END)
            
            caja_proveedor.set("")
            caja_codigo.focus_set()
        
        def guardar():
            codigo = caja_codigo.get()
            descripcion = caja_descripcion.get()
            categoria = caja_categoria.get()
            proveedor = caja_proveedor.get()
            stock_actual = caja_stock_actual.get()
            stock_minimo = caja_stock_minimo.get()
            precio_costo = caja_precio_costo.get()
            precio_venta = caja_precio_venta.get()
            ubicacion = caja_ubicacion.get()
            vencimiento = caja_vencimiento.get()

            if not proveedor:
                print("Error: Debe seleccionar un proveedor.")
                return

            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            cursor.execute('''
                INSERT INTO stock (codigo, descripcion, categoria, proveedor, stock_actual, stock_minimo, precio_costo, precio_venta, ubicacion, vencimiento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (codigo, descripcion, categoria, proveedor, stock_actual, stock_minimo, precio_costo, precio_venta, ubicacion, vencimiento))

            conexion.commit()
            conexion.close()

            limpiar_campos()
            cargar_datos_db()

        def seleccionar_fila(event):
            seleccion = tabla.selection()
            if not seleccion:
                return
                
            valores = tabla.item(seleccion[0], "values")

            cajas = [caja_codigo, caja_descripcion, caja_categoria, caja_stock_actual, caja_stock_minimo, caja_precio_costo, 
                     caja_precio_venta, caja_ubicacion, caja_vencimiento]
            indices = [0, 1, 2, 4, 5, 6, 7, 8, 9]
                     
            for caja, idx in zip(cajas, indices):
                caja.delete(0, tk.END)
                caja.insert(0, valores[idx])

            caja_proveedor.set(valores[3])

        def modificar():
            seleccion = tabla.selection()
            if not seleccion:
                return
            
            id_stock = seleccion[0]
            
            codigo = caja_codigo.get()
            descripcion = caja_descripcion.get()
            categoria = caja_categoria.get()
            proveedor = caja_proveedor.get()
            stock_actual = caja_stock_actual.get()
            stock_minimo = caja_stock_minimo.get()
            precio_costo = caja_precio_costo.get()
            precio_venta = caja_precio_venta.get()
            ubicacion = caja_ubicacion.get()
            vencimiento = caja_vencimiento.get()

            if not proveedor:
                print("Error: Debe seleccionar un proveedor.")
                return

            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            cursor.execute('''
                UPDATE stock SET 
                codigo=?, descripcion=?, categoria=?, proveedor=?, stock_actual=?, stock_minimo=?, precio_costo=?, precio_venta=?, ubicacion=?, vencimiento=?
                WHERE id=?
            ''', (codigo, descripcion, categoria, proveedor, stock_actual, stock_minimo, precio_costo, precio_venta, ubicacion, vencimiento, id_stock))

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
                cursor.execute("DELETE FROM stock WHERE id=?", (item,))
                
            conexion.commit()
            conexion.close()
            
            limpiar_campos()
            cargar_datos_db()



        # ===============================
        #  CAMPOS DEL "FORMULARIO STOCK"
        # ===============================

        tk.Label(self, text="Código").grid(row=1, column=0, pady=5, sticky="e", padx=5)
        caja_codigo = tk.Entry(self)
        caja_codigo.grid(row=1, column=1)

        tk.Label(self, text="Descripción").grid(row=2, column=0, pady=5, sticky="e", padx=5)
        caja_descripcion = tk.Entry(self)
        caja_descripcion.grid(row=2, column=1)

        tk.Label(self, text="Categoría").grid(row=3, column=0, pady=5, sticky="e", padx=5)
        caja_categoria = tk.Entry(self)
        caja_categoria.grid(row=3, column=1)

        tk.Label(self, text="Proveedor").grid(row=4, column=0, pady=5, sticky="e", padx=5)
        lista_proveedores = obtener_proveedores()
        caja_proveedor = ttk.Combobox(self, values=lista_proveedores, state="readonly", width=17)
        caja_proveedor.grid(row=4, column=1)

        tk.Label(self, text="Stock Actual").grid(row=5, column=0, pady=5, sticky="e", padx=5)
        caja_stock_actual = tk.Entry(self)
        caja_stock_actual.grid(row=5, column=1)

        tk.Label(self, text="Stock Mínimo").grid(row=6, column=0, pady=5, sticky="e", padx=5)
        caja_stock_minimo = tk.Entry(self)
        caja_stock_minimo.grid(row=6, column=1)

        tk.Label(self, text="Precio Costo").grid(row=7, column=0, pady=5, sticky="e", padx=5)
        caja_precio_costo = tk.Entry(self)
        caja_precio_costo.grid(row=7, column=1)

        tk.Label(self, text="Precio Venta").grid(row=8, column=0, pady=5, sticky="e", padx=5)
        caja_precio_venta = tk.Entry(self)
        caja_precio_venta.grid(row=8, column=1)

        tk.Label(self, text="Ubicación").grid(row=9, column=0, pady=5, sticky="e", padx=5)
        caja_ubicacion = tk.Entry(self)
        caja_ubicacion.grid(row=9, column=1)

        tk.Label(self, text="Vencimiento").grid(row=10, column=0, pady=5, sticky="e", padx=5)
        caja_vencimiento = tk.Entry(self)
        caja_vencimiento.grid(row=10, column=1)



        # =========================================================
        #  BOTONES "GUARDAR, MODIFICAR, ELIMINAR Y CERRAR VENTANA"
        # =========================================================

        boton_guardar = tk.Button(self, text="Guardar Producto", command=guardar, bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), width=16)
        boton_guardar.grid(row=3, column=3, padx=20)

        boton_modificar = tk.Button(self, text="Modificar Producto", command=modificar, bg="#2196F3", fg="white", font=("Arial", 9, "bold"), width=16)
        boton_modificar.grid(row=5, column=3, padx=20)

        boton_eliminar = tk.Button(self, text="Eliminar Producto", command=eliminar, bg="#F44336", fg="white", font=("Arial", 9, "bold"), width=16)
        boton_eliminar.grid(row=7, column=3, padx=20)

        boton_cerrar_ventana = tk.Button(self, text="Cerrar Ventana", command=self.destroy, bg="#9E9E9E", fg="white", font=("Arial", 9, "bold"), width=16)
        boton_cerrar_ventana.grid(row=9, column=3, padx=20)



        # =========================
        #  TABLA DE DATOS DE STOCK
        # =========================

        columnas = ("Código", "Descripción", "Categoría", "Proveedor", "Stock Actual", "Stock Mínimo", "Precio Costo", "Precio Venta", "Ubicación", "Vencimiento")

        tabla = ttk.Treeview(self, columns=columnas, show="headings", height=10)

        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, width=100)

        tabla.grid(row=11, column=0, columnspan=5, pady=20, padx=10)
        tabla.bind("<<TreeviewSelect>>", seleccionar_fila)



        # ========================
        #  CARGA INICIAL DE DATOS
        # ========================
        
        crear_tabla_stock()
        cargar_datos_db()