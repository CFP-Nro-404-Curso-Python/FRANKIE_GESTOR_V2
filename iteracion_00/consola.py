import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
# Se importa para trabajar con expresiones regulares.
import re



class ConsolaSQL(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("CONSOLA SQL - AUDITORÍA (SOLO LECTURA)")
        self.geometry("600x600")
        


        # =======================================
        #  ANCLAJE DE DIRECTORIO Y BASE DE DATOS
        # =======================================

        DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
        DB_PATH = os.path.join(DIRECTORIO_ACTUAL, "db", "frankie_gestor.db")



        # ======================================
        #  MOTOR DE EJECUCIÓN AISLADA (SANDBOX)
        # ======================================

        def ejecutar_query():
            # Extraemos el texto crudo del widget Text.
            query_cruda = caja_query.get("1.0", tk.END).strip()
            
            if not query_cruda:
                return

            # 1. Filtro Restrictivo de Solo Lectura.
            # Usamos Regex para buscar palabras reservadas destructivas con límites de palabra (\b).
            patron_prohibido = r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|REPLACE|GRANT|REVOKE)\b'
            
            if re.search(patron_prohibido, query_cruda, re.IGNORECASE):
                messagebox.showerror("Bloqueo de Seguridad", "Transacción abortada. Operación destructiva detectada.\nEsta consola es de Solo Lectura (SELECT).")
                label_estado.config(text="Estado: Query bloqueada por Sandboxing.", fg="red")
                return
            
            # 2. Inyección de Paginación Forzada.
            # Limpiamos el punto y coma final si existe para poder concatenar.
            query_segura = query_cruda.rstrip(';')
            
            if not re.search(r'\bLIMIT\b', query_segura, re.IGNORECASE):
                query_segura += " LIMIT 1000"

            # 3. Ejecución Dinámica.
            try:
                conexion = sqlite3.connect(DB_PATH)
                cursor = conexion.cursor()

                cursor.execute(query_segura)
                
                # Extraemos los nombres de las columnas desde la metadata del cursor.
                nombres_columnas = [descripcion[0] for descripcion in cursor.description] if cursor.description else []
                filas = cursor.fetchall()
                
                conexion.close()
                
                renderizar_grilla(nombres_columnas, filas)
                label_estado.config(text=f"Estado: Ejecución exitosa. Filas recuperadas: {len(filas)}", fg="green")
                
            except sqlite3.Error as e:
                label_estado.config(text=f"Error SQL: {e}", fg="red")

        def renderizar_grilla(columnas, filas):
            # Limpiamos los datos y la estructura anterior.
            tabla.delete(*tabla.get_children())
            tabla["columns"] = columnas
            
            # Configuramos las nuevas cabeceras.
            for col in columnas:
                tabla.heading(col, text=col.upper())
                tabla.column(col, width=120, anchor="center")
                
            # Insertamos los registros.
            for fila in filas:
                tabla.insert("", "end", values=fila)

        def limpiar_consola():
            caja_query.delete("1.0", tk.END)
            tabla.delete(*tabla.get_children())
            tabla["columns"] = ()
            label_estado.config(text="Estado: Esperando consulta...", fg="black")



        # =====================
        #  INTERFAZ DE USUARIO
        # =====================

        tk.Label(self, text="Ingresá tu sentencia SQL (SELECT):", font=("Arial", 10, "bold")).pack(pady=(10, 0), anchor="w", padx=20)
        
        # Caja de texto multilínea para la query.
        caja_query = tk.Text(self, height=6, font=("Consolas", 11), bg="#2b2b2b", fg="#a9b7c6", insertbackground="white")
        caja_query.pack(fill="x", padx=20, pady=5)
        
        frame_botones = tk.Frame(self)
        frame_botones.pack(pady=5)
        
        tk.Button(frame_botones, text="Ejecutar Consulta", command=ejecutar_query, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=20).grid(row=0, column=0, padx=10)
        tk.Button(frame_botones, text="Limpiar Consola", command=limpiar_consola, bg="#9E9E9E", fg="white", font=("Arial", 10, "bold"), width=15).grid(row=0, column=1, padx=10)
        
        label_estado = tk.Label(self, text="Estado: Esperando consulta...", font=("Arial", 9, "italic"))
        label_estado.pack(anchor="w", padx=20)

        # Grilla para resultados dinámicos.
        frame_tabla = tk.Frame(self)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Agregamos scrollbars por si la tabla devuelve muchas columnas o filas.
        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical")
        scroll_y.pack(side="right", fill="y")
        
        scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal")
        scroll_x.pack(side="bottom", fill="x")
        
        tabla = ttk.Treeview(frame_tabla, show="headings", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        tabla.pack(fill="both", expand=True)
        
        scroll_y.config(command=tabla.yview)
        scroll_x.config(command=tabla.xview)