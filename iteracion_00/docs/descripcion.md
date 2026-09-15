# Frankie Gestor - Documentación de Arquitectura (Iteración 00)

## Arquitectura del Sistema
Frankie Gestor es un sistema de gestión transaccional ligero, desarrollado bajo un paradigma modular. Esta Iteración 00 establece la arquitectura base del repositorio, garantizando una separación clara entre la capa de presentación (GUI), las reglas de negocio y la persistencia de datos.

* **Lenguaje Core:** Python 3.
* **Capa de Presentación:** Tkinter (renderizado de interfaz gráfica nativa).
* **Motor de Base de Datos:** SQLite3 (relacional, embebido y transaccional).
* **Gestión de Memoria:** Cierre de hilos y purgado de RAM automatizado mediante el protocolo `WM_DELETE_WINDOW` en la ventana raíz.

## Seguridad y Control de Acceso (RBAC)
El núcleo de la seguridad del sistema radica en un Control de Acceso Basado en Roles (RBAC) con barreras de validación tanto en el *frontend* (restricción visual) como en el *backend* (rechazo de transacciones SQL).

* **Administrador (Root):** Acceso irrestricto a todos los módulos. Cuenta con un seguro a nivel de base de datos para prevenir su autoeliminación.
* **Gerente:** Capacidad de gestión sobre registros operativos y cuentas subordinadas. Posee un bloqueo estricto (Anti-Escalada) que le impide modificar, eliminar o crear perfiles de igual o mayor jerarquía.
* **Empleados (Ventas / Compras):** Aislamiento de dominio operativo. El enrutador del sistema restringe su acceso únicamente a los módulos pertinentes a su sector.
* **Sandboxing SQL:** Consola de auditoría de solo lectura. Implementa un filtro restrictivo por expresiones regulares (Regex) que intercepta y aborta cualquier instrucción destructiva (`DROP`, `DELETE`, `UPDATE`, `INSERT`).

## Estructura de Módulos Operativos
Toda la navegación está centralizada en un Panel de Control dinámico que inyecta dependencias (Lazy Imports) según la sesión activa, reemplazando el enrutamiento rígido tradicional.

* **Gestión de Identidades:** Módulos de carga de usuarios (credenciales) y empleados (legajos de RRHH).
* **Cadena de Suministro:** Gestión de proveedores y control de stock (incluyendo prevención de quiebres de inventario mediante rollback lógico).
* **Ciclo de Ingresos:** Gestión de clientes y motor transaccional de facturación (operaciones ACID, cálculos de retenciones e integridad cruzada con stock).
* **Herramientas DBA:** Consola de auditoría SQL y generador automatizado de respaldos transaccionales (Backups) con marca de tiempo.