from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
from contextlib import AsyncExitStack

async def test_mcp_server():
    # Configura el cliente MCP para conectarse al servidor
    exit_stack = AsyncExitStack()
    try:
        # Configura los parámetros del servidor
        server_params = StdioServerParameters(
            command="python",
            args=["mysql_mcp_server_v2.py"],
            env=None
        )

        # Conecta al servidor
        stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await exit_stack.enter_async_context(ClientSession(stdio, write))
        await session.initialize()

        # Lista las herramientas disponibles
        response = await session.list_tools()
        print("\nHerramientas disponibles:", [tool.name for tool in response.tools])

        # Prueba get_estado_completo
        print("\nProbando get_estado_completo...")
        response = await session.call_tool("get_estado_completo", {"codigo": 101})
        print("Estado inicial:", response.content)

        # Prueba registrar_solicitud
        print("\nProbando registrar_solicitud...")
        response = await session.call_tool("registrar_solicitud", {"codigo": 101, "monto": 7500})
        print("Resultado solicitud:", response.content)

        # Verificar estado actualizado
        print("\nVerificando estado actualizado...")
        response = await session.call_tool("get_estado_completo", {"codigo": 101})
        print("Estado final:", response.content)

    except Exception as e:
        print(f"Error al llamar al servidor: {e}")
    finally:
        await exit_stack.aclose()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())