import mysql.connector
from mysql.connector import Error
import time

def test_mysql_connection():
    # Configuración para XAMPP
    db_config = {
        'host': '10.102.100.101',  # Usando IP en lugar de localhost
        'port': 3306,
        'user': 'reporte',
        'password': 'rEP@RTE2@25',
        'database': 'SPPCUTA2025_REPORTE',
        'raise_on_warnings': True
    }

    print("=== Iniciando prueba de conexión MySQL ===")
    print(f"Configuración de conexión: {db_config}")
    
    try:
        print("\n1. Intentando conectar a MySQL...")
        conn = mysql.connector.connect(**db_config)
        
        if conn.is_connected():
            print("✓ Conexión exitosa a MySQL!")
            db_info = conn.get_server_info()
            print(f"Versión del servidor MySQL: {db_info}")
            
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            database = cursor.fetchone()
            print(f"Base de datos conectada: {database[0]}")
            
            print("\n2. Verificando tabla departamentos...")
            cursor.execute("SHOW TABLES LIKE 'departamentos';")
            if cursor.fetchone():
                print("✓ Tabla 'departamentos' existe")
                
                print("\n3. Verificando estructura de la tabla...")
                cursor.execute("DESCRIBE departamentos;")
                columns = cursor.fetchall()
                print("Columnas en la tabla:")
                for column in columns:
                    print(f"  - {column[0]}: {column[1]}")
                
                print("\n4. Probando consulta simple...")
                cursor.execute("SELECT COUNT(*) FROM departamentos;")
                count = cursor.fetchone()
                print(f"Total de registros en departamentos: {count[0]}")
                
                if count[0] > 0:
                    print("\n5. Mostrando primer registro...")
                    cursor.execute("SELECT * FROM departamentos LIMIT 1;")
                    record = cursor.fetchone()
                    print(f"Primer registro: {record}")
            else:
                print("✗ Tabla 'departamentos' no existe")
            
    except Error as e:
        print(f"\n✗ Error de conexión: {e}")
        print("\nDetalles adicionales:")
        print(f"- Código de error: {e.errno}")
        print(f"- Mensaje SQL: {e.msg}")
        print(f"- Estado SQL: {e.sqlstate}")
        
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    test_mysql_connection() 