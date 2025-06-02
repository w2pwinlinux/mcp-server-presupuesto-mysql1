import os
from mcp.server.fastmcp import FastMCP
from openpyxl import load_workbook
import pandas as pd
from notifypy import Notify
from datetime import datetime

# Create an MCP server
mcp = FastMCP("ExcelBudgetServer")

@mcp.resource("budget://{department}")
def get_budget_status(department: str = None) -> dict:
    """Get the current budget status for a department or overall"""
    try:
        df = pd.read_excel('d:/docker/trae/mcp1/presupuesto.xlsx')
        
        if department:
            df = df[df['Departamento'] == department]
        
        status = {
            'total_presupuestado': float(df['Presupuesto'].sum()),
            'total_gastado': float(df['Gastos'].sum()),
            'balance': float(df['Presupuesto'].sum() - df['Gastos'].sum())
        }
        
        return status
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def compare_budget() -> list:
    """Compare current expenses with planned budget by department"""
    try:
        df = pd.read_excel('d:/docker/trae/mcp1/presupuesto.xlsx')
        comparison = df.groupby('Departamento').agg({
            'Presupuesto': 'sum',
            'Gastos': 'sum'
        }).reset_index()
        
        comparison['Diferencia'] = comparison['Presupuesto'] - comparison['Gastos']
        comparison['Porcentaje_Usado'] = (comparison['Gastos'] / comparison['Presupuesto'] * 100).round(2)
        
        return comparison.to_dict('records')
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def check_overbudget(threshold: float = 100) -> list:
    """Identify areas exceeding their budget threshold"""
    try:
        df = pd.read_excel('d:/docker/trae/mcp1/presupuesto.xlsx')
        
        df['Porcentaje_Usado'] = (df['Gastos'] / df['Presupuesto'] * 100).round(2)
        overbudget = df[df['Porcentaje_Usado'] > threshold]
        
        if not overbudget.empty:
            notification = Notify()
            notification.title = "¡Alerta de Presupuesto!"
            notification.message = f"Se han detectado {len(overbudget)} áreas que exceden el {threshold}% del presupuesto."
            notification.send()
        
        return overbudget.to_dict('records')
    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    mcp.run()