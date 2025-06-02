# Importación correcta basada en el servidor original
from mcp.server.fastmcp import FastMCP
import mysql.connector
from mysql.connector import Error
import asyncio
import socket
import time

# Crear una única instancia del servidor MCP
app = FastMCP("MySQLBudgetServer")

# Configuración para XAMPP
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'reporte',
    'password': 'reporte',
    'database': '_REPORTE',
    'raise_on_warnings': True,
    'connect_timeout': 30,  # Aumentado el timeout
    'autocommit': True,
    'pool_name': 'mcp_pool',
    'pool_size': 5,
    'get_warnings': True,
    'connection_timeout': 30,
    'use_pure': True,
    'consume_results': True
}

def test_mysql_connection():
    """Prueba la conexión al servidor MySQL y retorna información detallada"""
    try:
        # Primero probamos si podemos resolver el host
        try:
            ip = socket.gethostbyname(db_config['host'])
            print(f"Host {db_config['host']} resuelto a IP: {ip}")
        except socket.gaierror as e:
            print(f"Error al resolver el host {db_config['host']}: {e}")
            return False

        # Probamos si podemos conectarnos al puerto
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((db_config['host'], db_config['port']))
            sock.close()
            if result != 0:
                print(f"No se puede conectar al puerto {db_config['port']} en {db_config['host']}")
                return False
            print(f"Puerto {db_config['port']} está abierto en {db_config['host']}")
        except socket.error as e:
            print(f"Error al probar el puerto: {e}")
            return False

        # Intentamos la conexión MySQL
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"Conexión exitosa a MySQL. Versión: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"Error de MySQL: {e}")
        if e.errno == 2003:  # Can't connect to MySQL server
            print("No se puede conectar al servidor MySQL. Verifique que:")
            print("1. El servidor MySQL está ejecutándose")
            print("2. El host y puerto son correctos")
            print("3. El firewall permite la conexión")
            print("4. El usuario tiene permisos para conectarse desde este host")
        elif e.errno == 1045:  # Access denied
            print("Acceso denegado. Verifique usuario y contraseña")
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False

class DBConnection:
    def __init__(self):
        self.conn = None
        self.retry_count = 0
        self.max_retries = 3
        self.retry_delay = 2  # segundos

    def __enter__(self):
        while self.retry_count < self.max_retries:
            try:
                print(f"Intentando conectar a la base de datos (intento {self.retry_count + 1}/{self.max_retries})...")
                self.conn = mysql.connector.connect(**db_config)
                print("Conexión exitosa a la base de datos")
                return self.conn
            except Error as e:
                self.retry_count += 1
                print(f"Error de conexión (intento {self.retry_count}/{self.max_retries}): {e}")
                if self.retry_count < self.max_retries:
                    print(f"Reintentando en {self.retry_delay} segundos...")
                    time.sleep(self.retry_delay)
                else:
                    print("Se agotaron los intentos de conexión")
                    raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            try:
                print("Cerrando conexión a la base de datos")
                self.conn.close()
            except Error as e:
                print(f"Error al cerrar conexión: {e}")

@app.tool()
def get_estado_completo(codigo: int):
    print(f"Consultando estado para código: {codigo}")
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    codigo,
                    nombre,
                    inicial,
                    solicitado,
                    saldo,
                    pagado
                FROM departamentos
                WHERE codigo = %s
            """
            cursor.execute(query, (codigo,))
            result = cursor.fetchone()
            if result is None:
                print(f"No se encontró departamento con código {codigo}")
                return {"error": f"No se encontró el departamento con código {codigo}"}
            print(f"Resultado encontrado: {result}")
            return result
    except Error as e:
        print(f"Error de base de datos: {e}")
        return {"error": f"Error de base de datos: {str(e)}"}
    except Exception as e:
        print(f"Error inesperado: {e}")
        return {"error": f"Error inesperado: {str(e)}"}

@app.tool()
def registrar_solicitud(codigo: int, monto: float):
    print(f"Registrando solicitud para código: {codigo}, monto: {monto}")
    try:
        with DBConnection() as conn:
            cursor = conn.cursor()
            # Primero verificamos si el departamento existe
            cursor.execute("SELECT codigo FROM departamentos WHERE codigo = %s", (codigo,))
            if not cursor.fetchone():
                print(f"No se encontró departamento con código {codigo}")
                return {"error": f"No se encontró el departamento con código {codigo}"}
            
            cursor.execute(
                "UPDATE departamentos SET solicitado = solicitado + %s WHERE codigo = %s",
                (monto, codigo)
            )
            cursor.execute(
                "UPDATE departamentos SET saldo = inicial - solicitado - pagado WHERE codigo = %s",
                (codigo,)
            )
            conn.commit()
            print(f"Solicitud registrada exitosamente para código {codigo}")
            return {"actualizado": True, "mensaje": "Solicitud registrada exitosamente"}
    except Error as e:
        print(f"Error de base de datos: {e}")
        if conn:
            try:
                conn.rollback()
            except Error as rollback_error:
                print(f"Error al hacer rollback: {rollback_error}")
        return {"error": f"Error de base de datos: {str(e)}"}
    except Exception as e:
        print(f"Error inesperado: {e}")
        if conn:
            try:
                conn.rollback()
            except Error as rollback_error:
                print(f"Error al hacer rollback: {rollback_error}")
        return {"error": f"Error inesperado: {str(e)}"}

@app.tool()
def buscar_por_nombre(nombre: str):
    print(f"Buscando departamentos con nombre: {nombre}")
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    codigo,
                    nombre,
                    inicial,
                    solicitado,
                    saldo,
                    pagado
                FROM departamentos
                WHERE nombre LIKE %s
                ORDER BY nombre
            """
            # Usar % para búsqueda parcial
            cursor.execute(query, (f"%{nombre}%",))
            resultados = cursor.fetchall()
            
            if not resultados:
                print(f"No se encontraron departamentos con nombre que contenga '{nombre}'")
                return {"error": f"No se encontraron departamentos con nombre que contenga '{nombre}'"}
            
            print(f"Se encontraron {len(resultados)} departamentos")
            return {
                "total": len(resultados),
                "departamentos": resultados
            }
    except Error as e:
        print(f"Error de base de datos: {e}")
        return {"error": f"Error de base de datos: {str(e)}"}
    except Exception as e:
        print(f"Error inesperado: {e}")
        return {"error": f"Error inesperado: {str(e)}"}

if __name__ == "__main__":
    print("Iniciando servidor MCP MySQL...")
    print("\nProbando conexión a la base de datos...")
    if test_mysql_connection():
        print("\nConexión exitosa, iniciando servidor...")
        app.run()
    else:
        print("\nNo se pudo establecer la conexión con la base de datos.")
        print("Por favor, verifique la configuración y asegúrese de que el servidor MySQL esté accesible.")
        exit(1)