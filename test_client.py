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
            args=["excel_mcp_server.py"],
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

        # Prueba el recurso budget
        response = await session.call_tool("get_budget_status", {"department": "Ventas"})
        print("\nEstado del presupuesto:", response.content)

        # Prueba la herramienta compare_budget
        response = await session.call_tool("compare_budget")
        print("\nComparación de presupuesto:", response.content)

        # Prueba la herramienta check_overbudget
        response = await session.call_tool("check_overbudget", {"threshold": 90})
        print("\nVerificación de sobregasto:", response.content)

    except Exception as e:
        print(f"Error al llamar al servidor: {e}")
    finally:
        await exit_stack.aclose()

# Ejecuta el cliente de prueba
if __name__ == "__main__":
    asyncio.run(test_mcp_server())