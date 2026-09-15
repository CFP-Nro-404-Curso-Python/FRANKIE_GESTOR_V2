import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os



class Usuario(tk.Toplevel):
    def __init__(self, parent, rol_actual):
        super().__init__(parent)
        
        self.title("GESTIÓN DE USUARIOS")
        self.geometry("750x500")
        


        # =======================================
        #  ANCLAJE DE DIRECTORIO Y BASE DE DATOS
        # =======================================

        DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
        DB_PATH = os.path.join(DIRECTORIO_ACTUAL, "db", "frankie_gestor.db")



        # ==================================
        #  FUNCIONALIDADES DE BASE DE DATOS
        # ==================================

        def cargar_datos_db():
            for item in tabla.get_children():
                tabla.delete(item)
                
            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            # Por seguridad, NUNCA traemos la contraseña a la interfaz visual (Treeview).
            cursor.execute("SELECT id, nombres, apellidos, usuario, rol FROM usuarios")
            filas = cursor.fetchall()
            
            for fila in filas:
                # fila[0] es el ID oculto.
                tabla.insert("", "end", iid=fila[0], values=(fila[1], fila[2], fila[3], fila[4]))
            
            conexion.close()

        def limpiar_campos():
            caja_nombres.delete(0, tk.END)
            caja_apellidos.delete(0, tk.END)
            caja_usuario.delete(0, tk.END)
            caja_password.delete(0, tk.END)
            caja_rol.set("")
            caja_nombres.focus_set()

        def guardar():
            nombres = caja_nombres.get().strip()
            apellidos = caja_apellidos.get().strip()
            usuario = caja_usuario.get().strip()
            password = caja_password.get().strip()
            rol = caja_rol.get()

            if not nombres or not apellidos or not usuario or not password or not rol:
                messagebox.showwarning("Validación", "Todos los campos son obligatorios.")
                return
            
            # BARRERA RBAC FRONT-TO-BACK: Bloquea la creación de roles superiores heredados de la grilla.
            if rol_actual == "Gerente" and rol in ["Administrador", "Gerente"]:
                messagebox.showerror("Acceso Denegado", "Privilegios insuficientes para crear perfiles de esta jerarquía.")
                limpiar_campos()
                return

            try:
                conexion = sqlite3.connect(DB_PATH)
                cursor = conexion.cursor()

                cursor.execute('''
                    INSERT INTO usuarios (nombres, apellidos, usuario, password, rol)
                    VALUES (?, ?, ?, ?, ?)
                ''', (nombres, apellidos, usuario, password, rol))
                
                conexion.commit()
            
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "El nombre de usuario ya existe. Elegí otro.")
            finally:
                conexion.close()
                
            limpiar_campos()
            cargar_datos_db()

        def seleccionar_fila(event):
            seleccion = tabla.selection()
            if not seleccion:
                return
                
            valores = tabla.item(seleccion[0], "values")

            caja_nombres.delete(0, tk.END)
            caja_nombres.insert(0, valores[0])

            caja_apellidos.delete(0, tk.END)
            caja_apellidos.insert(0, valores[1])

            caja_usuario.delete(0, tk.END)
            caja_usuario.insert(0, valores[2])

            caja_rol.set(valores[3])
            
            # La contraseña se deja en blanco por seguridad. Si quieren modificarla, deben tipearla.
            caja_password.delete(0, tk.END)

        def modificar():
            seleccion = tabla.selection()
            if not seleccion:
                return
            
            id_usuario = seleccion[0]
            nombres = caja_nombres.get().strip()
            apellidos = caja_apellidos.get().strip()
            usuario = caja_usuario.get().strip()
            password = caja_password.get().strip()
            rol = caja_rol.get()

            if not usuario or not rol:
                messagebox.showwarning("Validación", "Usuario y Rol son obligatorios.")
                return

            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()

            # BARRERA RBAC: Evita que un Gerente modifique cuentas de igual o mayor jerarquía.
            cursor.execute("SELECT rol FROM usuarios WHERE id=?", (id_usuario,))
            rol_target = cursor.fetchone()[0]
            
            if rol_actual == "Gerente" and rol_target in ["Administrador", "Gerente"]:
                messagebox.showerror("Acceso Denegado", "Privilegios insuficientes para modificar a este usuario.")
                
                conexion.close()
                return
            
            try:
                # Lógica bifurcada: Si tipeó contraseña nueva, se actualiza. Si la dejó en blanco, se mantiene la vieja.
                if password:
                    cursor.execute("UPDATE usuarios SET nombres=?, apellidos=?, usuario=?, password=?, rol=? WHERE id=?", 
                                   (nombres, apellidos, usuario, password, rol, id_usuario))
                else:
                    cursor.execute("UPDATE usuarios SET nombres=?, apellidos=?, usuario=?, rol=? WHERE id=?", 
                                   (nombres, apellidos, usuario, rol, id_usuario))
                
                conexion.commit()

            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "El nombre de usuario ya está en uso.")
            finally:
                conexion.close()

            limpiar_campos()
            cargar_datos_db()

        def eliminar():
            seleccion = tabla.selection()
            if not seleccion:
                return
                
            id_usuario = seleccion[0]
            
            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()
            
            # Obtenemos el rol del usuario que se intentó seleccionar.
            cursor.execute("SELECT rol FROM usuarios WHERE id=?", (id_usuario,))
            rol_a_borrar = cursor.fetchone()[0]

            # BARRERA RBAC: Evita que un Gerente elimine cuentas de igual o mayor jerarquía.
            if rol_actual == "Gerente" and rol_a_borrar in ["Administrador", "Gerente"]:
                messagebox.showerror("Acceso Denegado", "Privilegios insuficientes para eliminar a este usuario.")
                
                conexion.close()
                return

            if rol_a_borrar == "Administrador":
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol='Administrador'")
                total_admins = cursor.fetchone()[0]
                if total_admins <= 1:
                    messagebox.showerror("Operación Bloqueada", "No podés eliminar al único Administrador del sistema.")
                    
                    conexion.close()
                    return

            cursor.execute("DELETE FROM usuarios WHERE id=?", (id_usuario,))
            
            conexion.commit()
            conexion.close()
            
            limpiar_campos()
            cargar_datos_db()



        # =====================
        #  INTERFAZ DE USUARIO
        # =====================

        frame_form = tk.Frame(self)
        frame_form.pack(pady=20)

        tk.Label(frame_form, text="Nombres:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        caja_nombres = tk.Entry(frame_form, width=25)
        caja_nombres.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(frame_form, text="Apellidos:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        caja_apellidos = tk.Entry(frame_form, width=25)
        caja_apellidos.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(frame_form, text="Usuario:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        caja_usuario = tk.Entry(frame_form, width=25)
        caja_usuario.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(frame_form, text="Contraseña:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        caja_password = tk.Entry(frame_form, width=25, show="*")
        caja_password.grid(row=3, column=1, padx=10, pady=5)
        
        tk.Label(frame_form, text="Rol Asignado:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        
        # Filtro de seguridad visual basado en rol.
        roles_permitidos = ["Empleado - Ventas", "Empleado - Compras"]
        if rol_actual == "Administrador":
            roles_permitidos = ["Administrador", "Gerente"] + roles_permitidos
            
        caja_rol = ttk.Combobox(frame_form, values=roles_permitidos, state="readonly", width=22)
        caja_rol.grid(row=4, column=1, padx=10, pady=5)

        # Botonera.
        frame_botones = tk.Frame(self)
        frame_botones.pack(pady=10)

        tk.Button(frame_botones, text="Guardar", command=guardar, bg="#4CAF50", fg="white", width=12).grid(row=0, column=0, padx=5)
        tk.Button(frame_botones, text="Modificar", command=modificar, bg="#2196F3", fg="white", width=12).grid(row=0, column=1, padx=5)
        tk.Button(frame_botones, text="Eliminar", command=eliminar, bg="#F44336", fg="white", width=12).grid(row=0, column=2, padx=5)

        # Grilla de Usuarios.
        columnas = ("Nombres", "Apellidos", "Usuario", "Rol")
        tabla = ttk.Treeview(self, columns=columnas, show="headings", height=8)
        tabla.heading("Nombres", text="Nombres")
        tabla.heading("Apellidos", text="Apellidos")
        tabla.heading("Usuario", text="Nombre de Usuario")
        tabla.heading("Rol", text="Rol del Sistema")
        tabla.pack(pady=10)
        
        tabla.bind("<<TreeviewSelect>>", seleccionar_fila)

        cargar_datos_db()