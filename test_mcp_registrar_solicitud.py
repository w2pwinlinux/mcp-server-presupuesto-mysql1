from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
from contextlib import AsyncExitStack
import json

def format_response(response):
    """Formatea la respuesta del servidor MCP para mejor visualización"""
    try:
        if hasattr(response, 'content') and isinstance(response.content, list):
            # Si content es una lista de TextContent
            for content in response.content:
                if hasattr(content, 'text'):
                    try:
                        # Intentar parsear el texto como JSON
                        return json.loads(content.text)
                    except json.JSONDecodeError:
                        # Si no es JSON válido, devolver el texto como está
                        return {"text": content.text}
        
        # Si la respuesta es directamente un diccionario
        if isinstance(response, dict):
            return response
            
        # Si la respuesta es una cadena
        if isinstance(response, str):
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"text": response}
        
        # Si no se pudo procesar la respuesta
        return {"error": f"Formato de respuesta no reconocido: {type(response)}"}
        
    except Exception as e:
        return {"error": f"Error al procesar respuesta: {str(e)}"}

async def test_mcp_registrar_solicitud():
    print("=== Test MCP de Registrar Solicitud ===")
    
    # Configura el cliente MCP para conectarse al servidor
    exit_stack = AsyncExitStack()
    try:
        # Configura los parámetros del servidor
        server_params = StdioServerParameters(
            command="python",
            args=["mysql_mcp_server_v2.py"],
            env=None
        )

        print("\nConectando al servidor MCP...")
        # Conecta al servidor
        stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await exit_stack.enter_async_context(ClientSession(stdio, write))
        await session.initialize()

        # Lista las herramientas disponibles
        response = await session.list_tools()
        print("\nHerramientas disponibles:", [tool.name for tool in response.tools])
        
        # Lista de casos de prueba: (código, monto, descripción)
        casos_prueba = [
            (101, 1000.00, "Solicitud válida - Monto pequeño"),
        ]
        
        for codigo, monto, descripcion in casos_prueba:
            print(f"\n--- Probando MCP: {descripcion} ---")
            print(f"Código: {codigo}, Monto: {monto:,.2f}")
            
            try:
                # Obtener estado antes de la solicitud
                print("\nConsultando estado inicial...")
                estado_antes = await session.call_tool("get_estado_completo", {"codigo": codigo})
                estado_antes = format_response(estado_antes)
                if "error" in estado_antes:
                    print(f"Error al obtener estado inicial: {estado_antes['error']}")
                    continue
                print(f"Estado inicial: {json.dumps(estado_antes, indent=2)}")
                
                # Intentar registrar la solicitud
                print("\nRegistrando solicitud...")
                resultado = await session.call_tool("registrar_solicitud", {
                    "codigo": codigo,
                    "monto": monto
                })
                resultado = format_response(resultado)
                if "error" in resultado:
                    print(f"Error al registrar solicitud: {resultado['error']}")
                    continue
                print(f"Resultado: {json.dumps(resultado, indent=2)}")
                
                # Obtener estado después de la solicitud
                print("\nConsultando estado final...")
                estado_despues = await session.call_tool("get_estado_completo", {"codigo": codigo})
                estado_despues = format_response(estado_despues)
                if "error" in estado_despues:
                    print(f"Error al obtener estado final: {estado_despues['error']}")
                    continue
                print(f"Estado final: {json.dumps(estado_despues, indent=2)}")
                
                # Verificar cambios si no hubo error
                if isinstance(estado_antes, dict) and isinstance(estado_despues, dict):
                    try:
                        diferencia_solicitado = float(estado_despues['solicitado']) - float(estado_antes['solicitado'])
                        print(f"\nVerificación:")
                        print(f"Diferencia en solicitado: {diferencia_solicitado:,.2f}")
                        print(f"Monto esperado: {monto:,.2f}")
                        if abs(diferencia_solicitado - monto) < 0.01:
                            print("✓ La diferencia coincide con el monto solicitado")
                        else:
                            print("✗ La diferencia no coincide con el monto solicitado")
                    except (KeyError, ValueError) as e:
                        print(f"Error al verificar cambios: {str(e)}")
            
            except Exception as e:
                print(f"Error durante la prueba: {str(e)}")
            
            print("-" * 50)
        
        # Test de solicitudes múltiples
        print("\n=== Test MCP de Solicitudes Múltiples ===")
        codigo = 101  # Usar el mismo código que en las pruebas individuales
        montos = [1000.00, 2000.00, 3000.00]
        
        # Obtener estado inicial
        print("\nConsultando estado inicial...")
        estado_inicial = await session.call_tool("get_estado_completo", {"codigo": codigo})
        print("DEBUG - Respuesta raw:", estado_inicial)
        estado_inicial = format_response(estado_inicial)
        print(f"Estado inicial: {json.dumps(estado_inicial, indent=2)}")
        
        # Registrar múltiples solicitudes
        for i, monto in enumerate(montos, 1):
            print(f"\n--- Registrando solicitud {i} de {len(montos)} ---")
            print(f"Monto: {monto:,.2f}")
            
            resultado = await session.call_tool("registrar_solicitud", {
                "codigo": codigo,
                "monto": monto
            })
            print("DEBUG - Respuesta raw:", resultado)
            resultado = format_response(resultado)
            print(f"Resultado: {json.dumps(resultado, indent=2)}")
            
            if "error" in resultado:
                print(f"Error en solicitud {i}, deteniendo test múltiple")
                break
            
            # Verificar estado después de cada solicitud
            estado_actual = await session.call_tool("get_estado_completo", {"codigo": codigo})
            print("DEBUG - Respuesta raw:", estado_actual)
            estado_actual = format_response(estado_actual)
            print(f"Estado actual: {json.dumps(estado_actual, indent=2)}")
        
        # Resumen final
        print("\n=== Resumen de Test Múltiple ===")
        estado_final = await session.call_tool("get_estado_completo", {"codigo": codigo})
        print("DEBUG - Respuesta raw:", estado_final)
        estado_final = format_response(estado_final)
        if "error" not in estado_final and "error" not in estado_inicial:
            print(f"\nEstado final del departamento {codigo}:")
            print(f"Saldo inicial: {float(estado_inicial['saldo']):,.2f}")
            print(f"Saldo final: {float(estado_final['saldo']):,.2f}")
            print(f"Solicitado inicial: {float(estado_inicial['solicitado']):,.2f}")
            print(f"Solicitado final: {float(estado_final['solicitado']):,.2f}")
            print(f"Total solicitado en este test: {sum(montos):,.2f}")
            print(f"Diferencia en solicitado: {float(estado_final['solicitado']) - float(estado_inicial['solicitado']):,.2f}")
    
    except Exception as e:
        print(f"\nError al llamar al servidor: {e}")
    finally:
        await exit_stack.aclose()
        print("\nConexión MCP cerrada")

if __name__ == "__main__":
    # Ejecutar el test asíncrono
    asyncio.run(test_mcp_registrar_solicitud()) 