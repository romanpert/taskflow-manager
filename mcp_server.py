# mcp_server.py
import asyncio
import logging
from fastmcp import FastMCP, MCPError
from api import app as fastapi_app
from backend.project_service import ProjectService
from backend.task_service import TaskService

# Configuración de logging para monitorización (stderr redirigido a tu sistema de logs)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

ps = ProjectService()
ts = TaskService(ps)

# 1) Clonar la API REST como recursos y tools MCP, con versionado
mcp = FastMCP.from_fastapi(
    fastapi_app,
    name="taskflow-mcp",
    version="0.1.0",
    description="MCP for project management"
)

# Ejemplo de composición futura (múltiples MCP)
# other_mcp = FastMCP(name="finanzas-mcp", version="0.1.0")
# mcp.mount("finanzas", other_mcp)

# Helper para correr funciones síncronas con timeout (rate‑limit / timeouts)
async def _run_sync(fn, timeout: float = 5.0):
    loop = asyncio.get_event_loop()
    return await asyncio.wait_for(loop.run_in_executor(None, fn), timeout)

# ─────────── Tools de Proyectos ───────────

@mcp.tool()
async def list_projects_llm() -> list[dict]:
    """Lista todos los proyectos."""
    try:
        return await _run_sync(lambda: [p.dict(by_alias=True) for p in ps.projects.values()])
    except asyncio.TimeoutError:
        raise MCPError("Timeout en list_projects_llm")

@mcp.tool()
async def get_project_llm(id: str) -> dict:
    """Recupera un proyecto por ID."""
    try:
        return await _run_sync(lambda: ps.projects[id].dict(by_alias=True))
    except KeyError:
        raise MCPError(f"Proyecto '{id}' no encontrado")
    except asyncio.TimeoutError:
        raise MCPError("Timeout en get_project_llm")

@mcp.tool()
async def create_project_llm(
    id: str,
    nombre: str,
    descripcion: str = "",
    responsables: list[str] = [],
    etiquetas: list[str] = []
) -> dict:
    """Crea un proyecto evitando duplicados. (Nota: podrías añadir token en args)."""
    payload = {
        "id": id, "nombre": nombre, "descripcion": descripcion,
        "responsables": responsables, "etiquetas": etiquetas
    }
    try:
        proj = await _run_sync(lambda: ps.create(payload, user="llm"))
        return proj.dict(by_alias=True)
    except ValueError as e:
        raise MCPError(str(e))
    except asyncio.TimeoutError:
        raise MCPError("Timeout en create_project_llm")

@mcp.tool()
async def update_project_llm(id: str, updates: dict) -> dict:
    """Actualiza campos de un proyecto."""
    try:
        proj = await _run_sync(lambda: ps.update(id, updates, user="llm"))
        return proj.dict(by_alias=True)
    except KeyError:
        raise MCPError(f"Proyecto '{id}' no encontrado")
    except asyncio.TimeoutError:
        raise MCPError("Timeout en update_project_llm")

@mcp.tool()
async def close_project_llm(id: str) -> dict:
    """Marca un proyecto como cerrado."""
    try:
        proj = await _run_sync(lambda: ps.close(id, user="llm"))
        return proj.dict(by_alias=True)
    except KeyError:
        raise MCPError(f"Proyecto '{id}' no encontrado")
    except asyncio.TimeoutError:
        raise MCPError("Timeout en close_project_llm")

@mcp.tool()
async def delete_project_llm(id: str) -> str:
    """Elimina un proyecto con todo su contenido."""
    try:
        await _run_sync(lambda: ps.delete(id, user="llm"))
        return id
    except KeyError:
        raise MCPError(f"Proyecto '{id}' no encontrado")
    except asyncio.TimeoutError:
        raise MCPError("Timeout en delete_project_llm")

# ─────────── Tools de Tareas ───────────

@mcp.tool()
async def add_task_llm(project_id: str, payload: dict) -> dict:
    """Añade una tarea a un proyecto."""
    try:
        task = await _run_sync(lambda: ts.add_task(project_id, payload, user="llm"))
        return task.dict(by_alias=True)
    except KeyError:
        raise MCPError(f"Proyecto '{project_id}' no encontrado")
    except ValueError as e:
        raise MCPError(str(e))
    except asyncio.TimeoutError:
        raise MCPError("Timeout en add_task_llm")

@mcp.tool()
async def update_task_llm(project_id: str, task_id: str, updates: dict) -> dict:
    """Actualiza campos de una tarea."""
    try:
        task = await _run_sync(lambda: ts.update_task(project_id, task_id, updates, user="llm"))
        return task.dict(by_alias=True)
    except KeyError:
        raise MCPError(f"Tarea '{task_id}' no encontrada")
    except asyncio.TimeoutError:
        raise MCPError("Timeout en update_task_llm")

@mcp.tool()
async def close_task_llm(project_id: str, task_id: str) -> dict:
    """Marca una tarea como completada."""
    try:
        task = await _run_sync(lambda: ts.close_task(project_id, task_id, user="llm"))
        return task.dict(by_alias=True)
    except KeyError:
        raise MCPError(f"Tarea '{task_id}' no encontrada")
    except asyncio.TimeoutError:
        raise MCPError("Timeout en close_task_llm")

@mcp.tool()
async def delete_task_llm(project_id: str, task_id: str) -> str:
    """Elimina una tarea de un proyecto."""
    try:
        await _run_sync(lambda: ts.delete_task(project_id, task_id, user="llm"))
        return task_id
    except KeyError:
        raise MCPError(f"Tarea '{task_id}' no encontrada")
    except asyncio.TimeoutError:
        raise MCPError("Timeout en delete_task_llm")

# ─────────── Tools de Subtareas ───────────

@mcp.tool()
async def add_subtask_llm(project_id: str, task_id: str, payload: dict) -> dict:
    """Añade una subtarea a una tarea."""
    try:
        sub = await _run_sync(lambda: ts.add_subtask(project_id, task_id, payload, user="llm"))
        return sub.dict(by_alias=True)
    except KeyError:
        raise MCPError(f"Tarea '{task_id}' no encontrada")
    except ValueError as e:
        raise MCPError(str(e))
    except asyncio.TimeoutError:
        raise MCPError("Timeout en add_subtask_llm")

@mcp.tool()
async def update_subtask_llm(project_id: str, task_id: str, sub_id: str, updates: dict) -> dict:
    """Actualiza campos de una subtarea."""
    try:
        sub = await _run_sync(lambda: ts.update_subtask(project_id, task_id, sub_id, updates, user="llm"))
        return sub.dict(by_alias=True)
    except KeyError:
        raise MCPError(f"Subtarea '{sub_id}' no encontrada")
    except asyncio.TimeoutError:
        raise MCPError("Timeout en update_subtask_llm")

@mcp.tool()
async def close_subtask_llm(project_id: str, task_id: str, sub_id: str) -> dict:
    """Marca una subtarea como completada."""
    try:
        sub = await _run_sync(lambda: ts.close_subtask(project_id, task_id, sub_id, user="llm"))
        return sub.dict(by_alias=True)
    except KeyError:
        raise MCPError(f"Subtarea '{sub_id}' no encontrada")
    except asyncio.TimeoutError:
        raise MCPError("Timeout en close_subtask_llm")

@mcp.tool()
async def delete_subtask_llm(project_id: str, task_id: str, sub_id: str) -> str:
    """Elimina una subtarea de una tarea."""
    try:
        await _run_sync(lambda: ts.delete_subtask(project_id, task_id, sub_id, user="llm"))
        return sub_id
    except KeyError:
        raise MCPError(f"Subtarea '{sub_id}' no encontrada")
    except asyncio.TimeoutError:
        raise MCPError("Timeout en delete_subtask_llm")

# 3) Ejecutar
if __name__ == "__main__":
    mcp.run()  # STDIO por defecto; para SSE: mcp.run(transport="sse", port=9000)
