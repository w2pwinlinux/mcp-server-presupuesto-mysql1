import mysql.connector
from mysql.connector import Error
from decimal import Decimal
import json
from mysql_mcp_server_v2 import registrar_solicitud, get_estado_completo

# Configuración de la base de datos
db_config = {
    'host': '10.102.100.101',
    'port': 3306,
    'user': 'reporte',
    'password': 'rEP@RTE2@25',
    'database': 'SPPCUTA2025_REPORTE',
    'raise_on_warnings': True
}

def format_decimal(value):
    """Formatea un número decimal para mejor visualización"""
    return f"{Decimal(str(value)):,.2f}"

def test_registrar_solicitud():
    print("=== Test de Registro de Solicitudes ===")
    
    # Lista de casos de prueba: (código, monto, descripción)
    casos_prueba = [
        (1, 1000.00, "Solicitud válida - Monto pequeño"),
        (1, 5000.00, "Solicitud válida - Monto mediano"),
        (999, 1000.00, "Código de departamento inexistente"),
        (1, -1000.00, "Monto negativo (debería ser rechazado)"),
        (1, 0.00, "Monto cero"),
        (2, 10000.00, "Solicitud a otro departamento")
    ]
    
    for codigo, monto, descripcion in casos_prueba:
        print(f"\n--- Probando: {descripcion} ---")
        print(f"Código: {codigo}, Monto: {monto:,.2f}")
        
        # Obtener estado antes de la solicitud
        estado_antes = get_estado_completo(codigo)
        if "error" in estado_antes:
            print(f"Estado antes: {estado_antes['error']}")
        else:
            print("\nEstado antes de la solicitud:")
            print(f"Saldo inicial: {estado_antes['saldo']:,.2f}")
            print(f"Monto solicitado: {estado_antes['solicitado']:,.2f}")
        
        # Intentar registrar la solicitud
        resultado = registrar_solicitud(codigo, monto)
        
        if "error" in resultado:
            print(f"Error al registrar: {resultado['error']}")
        else:
            print(f"Resultado: {resultado['mensaje']}")
            
            # Obtener estado después de la solicitud
            estado_despues = get_estado_completo(codigo)
            if "error" in estado_despues:
                print(f"Estado después: {estado_despues['error']}")
            else:
                print("\nEstado después de la solicitud:")
                print(f"Saldo actual: {estado_despues['saldo']:,.2f}")
                print(f"Monto solicitado: {estado_despues['solicitado']:,.2f}")
                
                # Verificar que los cambios son correctos
                if "error" not in estado_antes:
                    diferencia_solicitado = estado_despues['solicitado'] - estado_antes['solicitado']
                    print(f"\nVerificación:")
                    print(f"Diferencia en solicitado: {diferencia_solicitado:,.2f}")
                    print(f"Monto esperado: {monto:,.2f}")
                    if abs(diferencia_solicitado - monto) < 0.01:  # Usar una pequeña tolerancia para comparaciones de punto flotante
                        print("✓ La diferencia coincide con el monto solicitado")
                    else:
                        print("✗ La diferencia no coincide con el monto solicitado")
        
        print("-" * 50)

def test_registrar_solicitud_multiple():
    print("\n=== Test de Registro de Solicitudes Múltiples ===")
    
    codigo = 1  # Usar un departamento existente
    montos = [1000.00, 2000.00, 3000.00]
    
    # Obtener estado inicial
    estado_inicial = get_estado_completo(codigo)
    if "error" in estado_inicial:
        print(f"Error al obtener estado inicial: {estado_inicial['error']}")
        return
    
    print(f"\nEstado inicial del departamento {codigo}:")
    print(f"Saldo: {estado_inicial['saldo']:,.2f}")
    print(f"Solicitado: {estado_inicial['solicitado']:,.2f}")
    
    # Registrar múltiples solicitudes
    for i, monto in enumerate(montos, 1):
        print(f"\n--- Registrando solicitud {i} de {len(montos)} ---")
        print(f"Monto: {monto:,.2f}")
        
        resultado = registrar_solicitud(codigo, monto)
        if "error" in resultado:
            print(f"Error: {resultado['error']}")
            break
        else:
            print(f"Resultado: {resultado['mensaje']}")
            
            # Verificar estado después de cada solicitud
            estado_actual = get_estado_completo(codigo)
            if "error" not in estado_actual:
                print(f"Estado actual:")
                print(f"Saldo: {estado_actual['saldo']:,.2f}")
                print(f"Solicitado: {estado_actual['solicitado']:,.2f}")
    
    print("\n=== Resumen de Test de Solicitudes Múltiples ===")
    estado_final = get_estado_completo(codigo)
    if "error" not in estado_final:
        print(f"\nEstado final del departamento {codigo}:")
        print(f"Saldo inicial: {estado_inicial['saldo']:,.2f}")
        print(f"Saldo final: {estado_final['saldo']:,.2f}")
        print(f"Solicitado inicial: {estado_inicial['solicitado']:,.2f}")
        print(f"Solicitado final: {estado_final['solicitado']:,.2f}")
        print(f"Total solicitado en este test: {sum(montos):,.2f}")
        print(f"Diferencia en solicitado: {estado_final['solicitado'] - estado_inicial['solicitado']:,.2f}")

if __name__ == "__main__":
    # Ejecutar ambos tests
    test_registrar_solicitud()
    test_registrar_solicitud_multiple() 