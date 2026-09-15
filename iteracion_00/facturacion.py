import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os



class Facturacion(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("FORMULARIO FACTURACIÓN")
        self.geometry("650x680")



        # =======================================
        #  ANCLAJE DE DIRECTORIO Y BASE DE DATOS
        # =======================================

        DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
        CARPETA_DB = os.path.join(DIRECTORIO_ACTUAL, "db")
        os.makedirs(CARPETA_DB, exist_ok=True)
        DB_PATH = os.path.join(CARPETA_DB, "frankie_gestor.db")

        # DDL: Inicializa la tabla de facturación si no existe.
        def crear_tabla_facturacion():
            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS facturacion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto TEXT,
                    cantidad TEXT,
                    valor TEXT,
                    descuento TEXT,
                    total TEXT
                )
            ''')

            conexion.commit()
            conexion.close()



        # =========================================================
        #  FUNCIONES DE EXTRACCIÓN DE DATOS MAESTROS (INTEGRACIÓN)
        # =========================================================

        def obtener_vendedores():
            lista = []
            if os.path.exists(DB_PATH):
                conexion = sqlite3.connect(DB_PATH)
                cursor = conexion.cursor()

                try:
                    # Nueva query que permite seleccionar, solamente a los empleados de Ventas.
                    cursor.execute("SELECT nombres, apellidos FROM empleados WHERE sector = 'Ventas'")
                    for fila in cursor.fetchall():
                        lista.append(f"{fila[1]}, {fila[0]}")
                except sqlite3.OperationalError:
                    pass

                conexion.close()

            return lista

        def obtener_clientes():
            lista = []
            if os.path.exists(DB_PATH):
                conexion = sqlite3.connect(DB_PATH)
                cursor = conexion.cursor()

                try:
                    cursor.execute("SELECT nombres, apellidos FROM clientes")
                    for fila in cursor.fetchall():
                        lista.append(f"{fila[1]}, {fila[0]}")
                except sqlite3.OperationalError:
                    pass

                conexion.close()

            return lista

        def obtener_productos():
            lista = []
            if os.path.exists(DB_PATH):
                conexion = sqlite3.connect(DB_PATH)
                cursor = conexion.cursor()

                try:
                    cursor.execute("SELECT codigo, descripcion FROM stock")
                    for fila in cursor.fetchall():
                        lista.append(f"{fila[0]} - {fila[1]}")
                except sqlite3.OperationalError:
                    pass

                conexion.close()

            return lista

        def autocompletar_precio(event):
            seleccion = caja_producto.get()
            if not seleccion: return

            codigo_prod = seleccion.split(" - ")[0]
            
            if os.path.exists(DB_PATH):
                conexion = sqlite3.connect(DB_PATH)
                cursor = conexion.cursor()

                try:
                    cursor.execute("SELECT precio_venta FROM stock WHERE codigo=?", (codigo_prod,))
                    resultado = cursor.fetchone()
                    if resultado:
                        caja_valor.config(state="normal")
                        caja_valor.delete(0, tk.END)
                        caja_valor.insert(0, resultado[0])
                        caja_valor.config(state="readonly")
                except sqlite3.OperationalError:
                    pass

                conexion.close()
        


        # =============================================
        #  FUNCIONALIDADES DE "FORMULARIO FACTURACIÓN"
        # =============================================

        def cargar_datos_db():
            for item in tabla.get_children():
                tabla.delete(item)
                
            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            cursor.execute("SELECT * FROM facturacion")
            filas = cursor.fetchall()
            
            for fila in filas:
                tabla.insert("", "end", iid=fila[0], values=fila[1:])

            conexion.close()
            
            actualizar_total_factura()
        
        def gestionar_stock(codigo_buscado, variacion):
            if not os.path.exists(DB_PATH):
                return False, "La base de datos maestra no existe."
            
            exito = False
            advertencia = ""

            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()
            
            try:
                cursor.execute("SELECT id, stock_actual, stock_minimo FROM stock WHERE codigo=?", (codigo_buscado,))
                resultado = cursor.fetchone()
                
                if resultado:
                    id_producto = resultado[0]
                    stock_actual = float(resultado[1])
                    stock_minimo = float(resultado[2])
                    nuevo_stock = stock_actual + variacion
                    
                    if nuevo_stock < 0:
                        conexion.close()
                        return False, f"Stock insuficiente. Quedan {int(stock_actual)} unidades."

                    if variacion < 0 and nuevo_stock <= stock_minimo:
                        advertencia = f"El producto llegó a su stock mínimo. Quedan {int(nuevo_stock)} unidades."
                    
                    cursor.execute("UPDATE stock SET stock_actual=? WHERE id=?", (str(nuevo_stock), id_producto))

                    conexion.commit()
                    exito = True
                    
            except sqlite3.OperationalError:
                pass
            finally:
                conexion.close()
            
            return exito, advertencia

        def limpiar_campos():
            caja_valor.config(state="normal")
            caja_producto.set("")
            caja_cantidad.delete(0, tk.END)
            caja_valor.delete(0, tk.END)
            caja_descuento.delete(0, tk.END)
            caja_valor.config(state="readonly")
            caja_producto.focus_set()

        def actualizar_total_factura():
            gran_total = 0.0
            for item in tabla.get_children():
                valores = tabla.item(item, "values")
                gran_total += float(valores[4])
            
            desc_porcentaje = 0.0
            try:
                if 'caja_calc_descuento' in locals() or 'caja_calc_descuento' in globals() or hasattr(self, 'children'):
                    desc_str = caja_calc_descuento.get()
                    if desc_str.strip():
                        desc_porcentaje = float(desc_str)
                        if not (0 <= desc_porcentaje <= 100):
                            desc_porcentaje = 0.0
            except Exception:
                pass
            
            total_final = gran_total * (1 - (desc_porcentaje / 100))
            
            label_total_factura.config(text=f"TOTAL FACTURA: $ {total_final:.2f}")
            
            try:
                label_resultado_desc.config(text=f"Total con descuento ({desc_porcentaje}%): $ {total_final:.2f}")
            except Exception:
                pass

        def guardar():
            try:
                producto = caja_producto.get()
                if not producto:
                    print("Error: Seleccione un producto de la lista.")
                    return

                cantidad = float(caja_cantidad.get())
                valor = float(caja_valor.get())
                descuento = float(caja_descuento.get())

                if descuento < 0 or descuento > 100:
                    messagebox.showerror("Validación", "El descuento por producto debe estar entre 0 y 100%.")
                    return 

                codigo_prod = producto.split(" - ")[0]
                exito, msj_stock = gestionar_stock(codigo_prod, -cantidad)

                if not exito:
                    messagebox.showerror("Transacción Rechazada", msj_stock)
                    return

                total_linea = (cantidad * valor) * (1 - (descuento / 100))
                total_formateado = f"{total_linea:.2f}"
                
                conexion = sqlite3.connect(DB_PATH)
                cursor = conexion.cursor()

                cursor.execute('''
                    INSERT INTO facturacion (producto, cantidad, valor, descuento, total)
                    VALUES (?, ?, ?, ?, ?)
                ''', (producto, str(cantidad), str(valor), str(descuento), total_formateado))

                conexion.commit()
                conexion.close()

                limpiar_campos()
                cargar_datos_db()

                if msj_stock:
                    messagebox.showwarning("Alerta de Reposición", msj_stock)
                
            except ValueError:
                messagebox.showerror("Error de Formato", "Ingrese valores numéricos válidos en Cantidad y Descuento.")

        def seleccionar_fila(event):
            seleccion = tabla.selection()
            if not seleccion:
                return
                
            valores = tabla.item(seleccion[0], "values")

            caja_valor.config(state="normal")
            caja_producto.set(valores[0])
            caja_cantidad.delete(0, tk.END)
            caja_cantidad.insert(0, valores[1])
            caja_valor.delete(0, tk.END)
            caja_valor.insert(0, valores[2])
            caja_descuento.delete(0, tk.END)
            caja_descuento.insert(0, valores[3])
            caja_valor.config(state="readonly")
            
        def modificar():
            seleccion = tabla.selection()
            if not seleccion:
                return
            
            try:
                id_factura = seleccion[0]
                producto_nuevo = caja_producto.get()
                
                if not producto_nuevo:
                    messagebox.showerror("Error de Carga", "Seleccione un producto de la lista.")
                    return

                cantidad_nueva = float(caja_cantidad.get())
                valor_nuevo = float(caja_valor.get())
                descuento = float(caja_descuento.get())

                if descuento < 0 or descuento > 100:
                    messagebox.showerror("Validación", "El descuento por producto debe estar entre 0 y 100%.")
                    return

                valores_viejos = tabla.item(seleccion[0], "values")
                producto_viejo = valores_viejos[0]
                codigo_viejo = producto_viejo.split(" - ")[0]
                cantidad_vieja = float(valores_viejos[1])
                codigo_nuevo = producto_nuevo.split(" - ")[0]

                # 1. Restituimos el stock viejo.
                gestionar_stock(codigo_viejo, +cantidad_vieja)

                # 2. Intentamos deducir el stock nuevo.
                exito, msj_stock = gestionar_stock(codigo_nuevo, -cantidad_nueva)

                if not exito:
                    gestionar_stock(codigo_viejo, -cantidad_vieja)
                    messagebox.showerror("Transacción Rechazada", "Stock insuficiente para la nueva cantidad. Se ha deshecho el cambio.")
                    return

                total_linea = (cantidad_nueva * valor_nuevo) * (1 - (descuento / 100))
                total_formateado = f"{total_linea:.2f}"

                conexion = sqlite3.connect(DB_PATH)
                cursor = conexion.cursor()

                cursor.execute('''
                    UPDATE facturacion SET 
                    producto=?, cantidad=?, valor=?, descuento=?, total=?
                    WHERE id=?
                ''', (producto_nuevo, str(cantidad_nueva), str(valor_nuevo), str(descuento), total_formateado, id_factura))

                conexion.commit()
                conexion.close()

                limpiar_campos()
                cargar_datos_db()

                if msj_stock:
                    messagebox.showwarning("Alerta de Reposición", msj_stock)
                
            except ValueError:
                messagebox.showerror("Error de Formato",  "Ingrese valores numéricos válidos en Cantidad y Descuento.")

        def eliminar():
            seleccion = tabla.selection()
            if not seleccion:
                return
                
            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()
                
            for item in seleccion:
                valores = tabla.item(item, "values")
                codigo_prod = valores[0].split(" - ")[0]
                cantidad_a_devolver = float(valores[1])

                gestionar_stock(codigo_prod, +cantidad_a_devolver)
                cursor.execute("DELETE FROM facturacion WHERE id=?", (item,))
            
            conexion.commit()
            conexion.close()
            
            limpiar_campos()
            cargar_datos_db()

        def calcular_descuento_final():
            try:
                desc_str = caja_calc_descuento.get()
                if desc_str.strip():
                    desc_porcentaje = float(desc_str)
                    if desc_porcentaje < 0 or desc_porcentaje > 100:
                        messagebox.showerror("Validación", "El descuento global debe estar entre 0 y 100%.")
                        return
                
                actualizar_total_factura()
                caja_calc_descuento.delete(0, tk.END)
            
            except ValueError:
                messagebox.showerror("Error", "Ingrese un porcentaje global válido.")



        # =====================================
        #  CAMPOS DEL "FORMULARIO FACTURACIÓN"
        # =====================================

        tk.Label(self, text="Datos del Vendedor").grid(row=1, column=0, pady=5, sticky="e", padx=5)
        caja_datos_vendedor = ttk.Combobox(self, values=obtener_vendedores(), state="readonly", width=25)
        caja_datos_vendedor.grid(row=1, column=1)

        tk.Label(self, text="Datos del Cliente").grid(row=2, column=0, pady=5, sticky="e", padx=5)
        caja_datos_cliente = ttk.Combobox(self, values=obtener_clientes(), state="readonly", width=25)
        caja_datos_cliente.grid(row=2, column=1)

        tk.Label(self, text="").grid(row=3, column=0) # Espaciador.
        
        tk.Label(self, text="Producto").grid(row=4, column=0, pady=5, sticky="e", padx=5)
        caja_producto = ttk.Combobox(self, values=obtener_productos(), state="readonly", width=25)
        caja_producto.grid(row=4, column=1)
        caja_producto.bind("<<ComboboxSelected>>", autocompletar_precio)

        tk.Label(self, text="Cantidad").grid(row=5, column=0, pady=5, sticky="e", padx=5)
        caja_cantidad = tk.Entry(self)
        caja_cantidad.grid(row=5, column=1)
        
        tk.Label(self, text="Valor en $").grid(row=6, column=0, pady=5, sticky="e", padx=5)
        caja_valor = tk.Entry(self)
        caja_valor.grid(row=6, column=1)
        caja_valor.config(state="readonly")

        tk.Label(self, text="Descuento en %").grid(row=7, column=0, pady=5, sticky="e", padx=5)
        caja_descuento = tk.Entry(self)
        caja_descuento.grid(row=7, column=1)



        # =========================================================
        #  BOTONES "GUARDAR, MODIFICAR, ELIMINAR Y CERRAR VENTANA"
        # =========================================================
        
        boton_guardar = tk.Button(self, text="Guardar Facturación", command=guardar, bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), width=18)
        boton_guardar.grid(row=4, column=3, padx=20)

        boton_modificar = tk.Button(self, text="Modificar Facturación", command=modificar, bg="#2196F3", fg="white", font=("Arial", 9, "bold"), width=18)
        boton_modificar.grid(row=5, column=3, padx=20)

        boton_eliminar = tk.Button(self, text="Eliminar Facturación", command=eliminar, bg="#F44336", fg="white", font=("Arial", 9, "bold"), width=18)
        boton_eliminar.grid(row=6, column=3, padx=20)

        boton_cerrar_ventana = tk.Button(self, text="Cerrar Ventana", command=self.destroy, bg="#9E9E9E", fg="white", font=("Arial", 9, "bold"), width=18)
        boton_cerrar_ventana.grid(row=7, column=3, padx=20)



        # ===============================
        #  TABLA DE DATOS DE FACTURACIÓN
        # ===============================

        columnas = ("Producto", "Cantidad", "Valor en $", "Descuento en %", "Total en $")

        tabla = ttk.Treeview(self, columns=columnas, show="headings", height=10)

        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, width=110)

        tabla.grid(row=8, column=0, columnspan=5, pady=20, padx=10)
        tabla.bind("<<TreeviewSelect>>", seleccionar_fila)



        # ===================================
        #  ETIQUETA GLOBAL: TOTAL DE FACTURA
        # ===================================

        label_total_factura = tk.Label(self, text="TOTAL FACTURA: $ 0.00", font=("Arial", 10, "bold"))
        label_total_factura.grid(row=9, column=0, columnspan=2, sticky="w", padx=10)



        # ======================================
        #  SECCIÓN: DESCUENTO GLOBAL DE FACTURA
        # ======================================

        tk.Label(self, text="APLICAR DESCUENTO GLOBAL", font=("Arial", 9, "bold")).grid(row=10, column=0, pady=10, columnspan=2)

        tk.Label(self, text="Descuento Global en %").grid(row=11, column=0, pady=5, sticky="e", padx=5)
        caja_calc_descuento = tk.Entry(self)
        caja_calc_descuento.grid(row=11, column=1)

        boton_calcular_desc = tk.Button(self, text="Calcular Descuento Final", command=calcular_descuento_final, bg="#FF9800", fg="white", font=("Arial", 9, "bold"))
        boton_calcular_desc.grid(row=11, column=3)



        # ==============================================
        #  ETIQUETA QUE MUESTRA RESULTANTE DE DESCUENTO
        # ==============================================

        label_resultado_desc = tk.Label(self, text="TOTAL CON DESCUENTO: $ 0.00", font=("Arial", 9, "bold"))
        label_resultado_desc.grid(row=12, column=0, columnspan=4, pady=15)



        # ========================
        #  CARGA INICIAL DE DATOS
        # ========================
        
        crear_tabla_facturacion()
        cargar_datos_db()