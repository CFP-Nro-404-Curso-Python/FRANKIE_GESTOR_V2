# 🧪 Plan de Pruebas Integrales (QA Testing) - Iteración 00

## FASE 1: Ciclo de Vida y Autenticación
1. **Borrado de Estado:** Eliminá la base de datos `frankie_gestor.db` de la carpeta `/db` (si existe) para forzar el disparo del DDL y el sembrado automático del usuario maestro.
2. **Prueba de Fuerza Bruta:** Ejecutá `login.py`. Ingresá credenciales erróneas 3 veces seguidas. El sistema debe emitir la alerta de bloqueo y el proceso de Python debe finalizar por completo en tu terminal.
3. **Ingreso Maestro:** Reabrí el programa e iniciá sesión con `admin` / `admin123`.

## FASE 2: Gestión de Jerarquías (Administrador)
4. **Poblado de Perfiles:** Ingresá a "Gestión de Usuarios". Creá tres cuentas operativas: 
   * `gerente_test` (Rol: Gerente)
   * `ventas_test` (Rol: Empleado - Ventas)
   * `compras_test` (Rol: Empleado - Compras)
5. **Seguro de Autoeliminación:** Seleccioná a `admin` en la grilla e intentá eliminarlo. El sistema debe bloquear la acción, preservando la única cuenta raíz. Cerrá sesión.

## FASE 3: Aislamiento y Prevención de Escalada (Gerente)
6. **Limitación de Interfaz:** Logueate como `gerente_test`. Verificá que los botones "Consola SQL" y "Generar Backup" estén en estado inhabilitado (gris).
7. **Bloqueo Front-End:** Abrí "Gestión de Usuarios". El menú desplegable no debe permitir la selección de roles "Administrador" ni "Gerente" para nuevos ingresos.
8. **Bloqueo Back-End (Anti-Escalada):** Seleccioná al `admin` desde la grilla. Modificá su contraseña y clickeá "Modificar". El sistema debe rechazar la transacción por jerarquía insuficiente. Repetí la prueba intentando eliminarlo. Cerrá sesión.

## FASE 4: Restricción de Dominio (Empleados)
9. **Módulos de Ventas:** Logueate como `ventas_test`. Confirmá el acceso exclusivo a "Clientes" y "Facturación". El resto debe estar inhabilitado. Cerrá sesión.
10. **Módulos de Compras:** Logueate como `compras_test`. Confirmá el acceso exclusivo a "Proveedores" y "Stock". Cerrá sesión.

## FASE 5: Integridad Referencial Cruzada
11. **Poblado de Maestros:** Iniciá como `admin`. Creá 1 Cliente, 1 Empleado y 1 Proveedor en sus respectivos módulos.
12. **Lectura de Llaves Foráneas (UI):** Abrí "Stock". El menú desplegable de Proveedor debe traer al proveedor creado. Creá un producto asignándole 10 unidades de "Stock Actual".

## FASE 6: Flujo de Datos desde Gerencia
* **Alta de Subordinados:** Logueate como `gerente_test`. Ingresá a "Gestión de Usuarios" y creá un usuario de menor jerarquía (ej. `ventas_aux` / Rol: Empleado - Ventas). El sistema debe permitir la creación sin errores de escalada.
* **Carga de Datos Maestros:** Abrí "Gestión de Clientes" y creá el cliente "Empresa Test SA". Luego, abrí "Gestión de Proveedores" y creá el proveedor "Insumos Test SRL". Esto asegura que el Gerente inyecta datos operativos correctamente a la base compartida. Cerrá sesión.

## FASE 7: Continuidad y Acceso Operativo (Empleados)
* **Herencia y Modificación en Ventas:** Logueate con `ventas_aux` (la cuenta creada por el gerente en el paso anterior). Ingresá a "Gestión de Clientes". Verificá que "Empresa Test SA" figure en la grilla. Seleccionalo, modificá un dato (como el teléfono) y presioná "Modificar". El sistema debe actualizar el dato, validando que el rango inferior puede operar sobre registros generados por la jerarquía superior. Cerrá sesión.
* **Herencia y Modificación en Compras:** Logueate como `compras_test`. Ingresá a "Gestión de Proveedores". Comprobá que "Insumos Test SRL" esté disponible en la tabla y que podés interactuar con ese registro sin restricciones de autoría. Cerrá sesión.

## FASE 8: Motor Transaccional y Reglas de Negocio
13. **Lectura Compleja:** Abrí "Facturación". Los selectores de Vendedor, Cliente y Producto deben autocompletarse con los datos creados. Al seleccionar el producto, el "Valor en $" debe inyectarse solo.
14. **Rollback por Quiebre de Stock:** Intentá facturar 15 unidades del producto. El sistema debe calcular que 15 > 10, abortar la transacción (`ROLLBACK` lógico) y mostrar la alerta correspondiente.
15. **Operación ACID Exitosa:** Facturá 2 unidades aplicando un descuento del 10%. Verificá la exactitud matemática del Total.
16. **Deducción de Inventario:** Volvé a "Stock". Verificá que el producto ahora tenga 8 unidades de stock actual.

## FASE 9: Sandboxing SQL y Destrucción de Memoria
17. **Consulta Lícita:** En el Panel, abrí "Consola SQL". Tipeá `SELECT * FROM facturacion;`. La grilla debe estructurarse y poblarse dinámicamente.
18. **Inyección Bloqueada:** Tipeá `DELETE FROM usuarios;`. El motor de expresiones regulares debe abortar la ejecución antes de tocar el driver de SQLite.
19. **Generación de Backup:** Clickeá "Generar Backup DB". Confirmá que se haya creado el archivo `.db` en la carpeta `/backups` con el timestamp exacto.
20. **Limpieza de RAM:** Con el Panel de Control abierto, cerrá la ventana desde la "X" superior. Confirmá que el proceso finalice en tu terminal, demostrando la eficacia del protocolo `WM_DELETE_WINDOW`.