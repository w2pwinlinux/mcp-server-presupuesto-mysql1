# MySQL MCP Server v2

Este servidor MCP (Message Control Protocol) proporciona una interfaz para gestionar y consultar información de presupuestos departamentales a través de una base de datos MySQL.

## Características

- Conexión segura a base de datos MySQL
- Gestión de presupuestos departamentales
- Consultas por código de departamento
- Búsqueda por nombre de departamento
- Registro de solicitudes de presupuesto
- Manejo robusto de errores y conexiones

## Requisitos

- Python 3.6 o superior
- MySQL Server (XAMPP o similar)
- Paquetes Python requeridos:
  - mcp
  - mysql-connector-python

## Instalación

1. Clonar el repositorio
2. Instalar las dependencias:
```bash
pip install mcp mysql-connector-python
```

## Configuración

El servidor está configurado para conectarse a una base de datos MySQL con los siguientes parámetros por defecto:

```python
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'reporte',
    'password': 'reporte',
    'database': '_REPORTE',
    'raise_on_warnings': True
}
```

Ajusta estos parámetros según tu configuración de base de datos.

## Funcionalidades

### 1. Consulta de Estado Completo
```python
get_estado_completo(codigo: int)
```
Retorna la información completa de un departamento por su código, incluyendo:
- Código
- Nombre
- Presupuesto inicial
- Monto solicitado
- Saldo disponible
- Monto pagado

### 2. Registro de Solicitudes
```python
registrar_solicitud(codigo: int, monto: float)
```
Registra una nueva solicitud de presupuesto para un departamento:
- Actualiza el monto solicitado
- Recalcula el saldo disponible
- Maneja transacciones de forma segura

### 3. Búsqueda por Nombre
```python
buscar_por_nombre(nombre: str)
```
Busca departamentos por nombre:
- Búsqueda parcial (usando LIKE)
- Retorna múltiples resultados
- Incluye información completa de cada departamento encontrado

## Pruebas

El proyecto incluye scripts de prueba para verificar la funcionalidad:

- `test_buscar_nombre.py`: Prueba la funcionalidad de búsqueda por nombre
- Ejecuta las pruebas con:
```bash
python test_buscar_nombre.py
```

## Manejo de Errores

El servidor implementa un manejo robusto de errores:
- Errores de conexión a la base de datos
- Errores de consulta
- Validación de datos
- Rollback automático en caso de errores en transacciones

## Estructura de la Base de Datos

La tabla principal `departamentos` contiene los siguientes campos:
- `codigo` (int): Identificador único del departamento
- `nombre` (varchar): Nombre del departamento
- `inicial` (decimal): Presupuesto inicial
- `solicitado` (decimal): Monto solicitado
- `saldo` (decimal): Saldo disponible
- `pagado` (decimal): Monto pagado

## Ejecución

Para iniciar el servidor:
```bash
python mysql_mcp_server_v2.py
```

## Notas de Seguridad

- Las credenciales de la base de datos están hardcodeadas en el código. En un entorno de producción, se recomienda usar variables de entorno o un archivo de configuración seguro.
- Se implementa manejo de conexiones seguro usando el patrón context manager.
- Las transacciones se manejan con commit/rollback apropiados.

## Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.