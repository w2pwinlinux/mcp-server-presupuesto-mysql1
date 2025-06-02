# test_direct_registrar.py
from mysql_mcp_server_v2 import registrar_solicitud

if __name__ == "__main__":
    # Cambia estos valores por los que quieras probar
    codigo = 101
    monto = 5000.00
    resultado = registrar_solicitud(codigo, monto)
    print("Resultado:", resultado)