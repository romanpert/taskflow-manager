# =============================================================
# file: api.py
# =============================================================
from fastapi import FastAPI, HTTPException, Body
from typing import Dict, Any

from backend.project_service import ProjectService
from backend.task_service import TaskService
from backend.models import Project, Task, Subtask, Status

app = FastAPI(title="Gestor de Proyectos", version="0.1.0")

ps = ProjectService()
ts = TaskService(ps)

# ---------- Proyectos ---------- #

@app.get("/projects", response_model=list[Project])
def list_projects():
    return list(ps.projects.values())


@app.get("/projects/{project_id}", response_model=Project)
def get_project(project_id: str):
    try:
        return ps.projects[project_id]
    except KeyError:
        raise HTTPException(404, "Proyecto no encontrado")


@app.post("/projects", response_model=Project)
def create_project(payload: Dict[str, Any] = Body(...), user: str = "system"):
    try:
        return ps.create(payload, user=user)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.put("/projects/{project_id}", response_model=Project)
def update_project(project_id: str, updates: Dict[str, Any] = Body(...), user: str = "system"):
    try:
        return ps.update(project_id, updates, user)
    except KeyError:
        raise HTTPException(404, "Proyecto no encontrado")


@app.patch("/projects/{project_id}/close", response_model=Project)
def close_project(project_id: str, user: str = "system"):
    try:
        return ps.close(project_id, user)
    except KeyError:
        raise HTTPException(404, "Proyecto no encontrado")


@app.delete("/projects/{project_id}")
def delete_project(project_id: str, user: str = "system"):
    try:
        removed = ps.delete(project_id, user)
        return {"deleted": removed.id}
    except KeyError:
        raise HTTPException(404, "Proyecto no encontrado")

# ---------- Tareas ---------- #

@app.post("/projects/{project_id}/tasks", response_model=Task)
def add_task(project_id: str, payload: Dict[str, Any] = Body(...), user: str = "system"):
    try:
        return ts.add_task(project_id, payload, user)
    except (KeyError, ValueError) as e:
        raise HTTPException(404 if isinstance(e, KeyError) else 400, str(e))


@app.put("/projects/{project_id}/tasks/{task_id}", response_model=Task)
def update_task(project_id: str, task_id: str, updates: Dict[str, Any] = Body(...), user: str = "system"):
    try:
        return ts.update_task(project_id, task_id, updates, user)
    except KeyError as e:
        raise HTTPException(404, str(e))


@app.patch("/projects/{project_id}/tasks/{task_id}/close", response_model=Task)
def close_task(project_id: str, task_id: str, user: str = "system"):
    try:
        return ts.close_task(project_id, task_id, user)
    except KeyError as e:
        raise HTTPException(404, str(e))


@app.delete("/projects/{project_id}/tasks/{task_id}")
def delete_task(project_id: str, task_id: str, user: str = "system"):
    try:
        ts.delete_task(project_id, task_id, user)
        return {"deleted": task_id}
    except KeyError as e:
        raise HTTPException(404, str(e))

# ---------- Subtareas ---------- #

@app.post("/projects/{project_id}/tasks/{task_id}/subtasks", response_model=Subtask)
def add_subtask(project_id: str, task_id: str, payload: Dict[str, Any] = Body(...), user: str = "system"):
    try:
        return ts.add_subtask(project_id, task_id, payload, user)
    except (KeyError, ValueError) as e:
        raise HTTPException(404 if isinstance(e, KeyError) else 400, str(e))


@app.put("/projects/{project_id}/tasks/{task_id}/subtasks/{sub_id}", response_model=Subtask)
def update_subtask(project_id: str, task_id: str, sub_id: str, updates: Dict[str, Any] = Body(...), user: str = "system"):
    try:
        return ts.update_subtask(project_id, task_id, sub_id, updates, user)
    except KeyError as e:
        raise HTTPException(404, str(e))


@app.patch("/projects/{project_id}/tasks/{task_id}/subtasks/{sub_id}/close", response_model=Subtask)
def close_subtask(project_id: str, task_id: str, sub_id: str, user: str = "system"):
    try:
        return ts.close_subtask(project_id, task_id, sub_id, user)
    except KeyError as e:
        raise HTTPException(404, str(e))


@app.delete("/projects/{project_id}/tasks/{task_id}/subtasks/{sub_id}")
def delete_subtask(project_id: str, task_id: str, sub_id: str, user: str = "system"):
    try:
        ts.delete_subtask(project_id, task_id, sub_id, user)
        return {"deleted": sub_id}
    except KeyError as e:
        raise HTTPException(404, str(e))


# ---------- Root ---------- #

@app.get("/")
def root():
    return {"message": "Servidor de gestión de proyectos activo en puerto 2410"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=2410, reload=True)
