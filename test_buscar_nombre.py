from mysql_mcp_server_v2 import buscar_por_nombre

def test_buscar_nombre():
    print("=== Test de Búsqueda por Nombre ===")
    
    # Lista de nombres para probar
    nombres_prueba = [
        "ventas",      # Búsqueda común
        "admin",       # Búsqueda parcial
        "xyz123",      # Nombre que no existe
        "finanzas",    # Otro departamento común
        "a"           # Búsqueda muy general
    ]
    
    for nombre in nombres_prueba:
        print(f"\n--- Probando búsqueda: '{nombre}' ---")
        resultado = buscar_por_nombre(nombre)
        
        if "error" in resultado:
            print(f"Error: {resultado['error']}")
        else:
            print(f"Total encontrados: {resultado['total']}")
            print("\nDepartamentos encontrados:")
            for depto in resultado['departamentos']:
                print(f"\nCódigo: {depto['codigo']}")
                print(f"Nombre: {depto['nombre']}")
                print(f"Presupuesto inicial: {depto['inicial']:,.2f}")
                print(f"Solicitado: {depto['solicitado']:,.2f}")
                print(f"Saldo: {depto['saldo']:,.2f}")
                print(f"Pagado: {depto['pagado']:,.2f}")
                print("-" * 30)

if __name__ == "__main__":
    test_buscar_nombre() 