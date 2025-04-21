from datetime import datetime
from typing import Any, Dict

from .models import Status, Subtask, Task
from .project_service import ProjectService


class TaskService:
    def __init__(self, project_service: ProjectService):
        self.ps = project_service

    # ---------- Tasks ---------- #

    def add_task(
        self,
        project_id: str,
        data: Dict[str, Any],
        user: str,
    ) -> Task:
        project = self.ps.projects[project_id]
        if any(t.id == data["id"] for t in project.tasks):
            raise ValueError("La tarea ya existe en este proyecto")
        task = Task.parse_obj(data)
        project.tasks.append(task)
        self.ps._record_history(
            project,
            "task-created",
            user,
            {"task_id": task.id},
        )
        self.ps._persist()
        return task

    def update_task(
        self,
        project_id: str,
        task_id: str,
        updates: Dict[str, Any],
        user: str,
    ) -> Task:
        project = self.ps.projects[project_id]
        task = next(
            (t for t in project.tasks if t.id == task_id),
            None,
        )
        if not task:
            raise KeyError("Tarea no encontrada")
        for field, value in updates.items():
            if hasattr(task, field):
                setattr(task, field, value)
            else:
                task.custom_fields[field] = value
        task.updated_at = datetime.utcnow()
        task.status = updates.get("status", task.status)
        self.ps._record_history(
            project,
            "task-updated",
            user,
            {"task_id": task.id, **updates},
        )
        self.ps._persist()
        return task

    def close_task(
        self,
        project_id: str,
        task_id: str,
        user: str,
    ) -> Task:
        return self.update_task(
            project_id,
            task_id,
            {"status": Status.completed},
            user,
        )

    def delete_task(
        self,
        project_id: str,
        task_id: str,
        user: str,
    ):
        project = self.ps.projects[project_id]
        project.tasks = [t for t in project.tasks if t.id != task_id]
        self.ps._record_history(
            project,
            "task-deleted",
            user,
            {"task_id": task_id},
        )
        self.ps._persist()

    # ---------- Subtasks ---------- #

    def add_subtask(
        self,
        project_id: str,
        task_id: str,
        data: Dict[str, Any],
        user: str,
    ) -> Subtask:
        task = self._get_task(project_id, task_id)
        if any(st.id == data["id"] for st in task.subtasks):
            raise ValueError("Subtarea duplicada")
        subtask = Subtask.parse_obj(data)
        task.subtasks.append(subtask)
        self.ps._record_history(
            self.ps.projects[project_id],
            "subtask-created",
            user,
            {
                "task_id": task_id,
                "subtask_id": subtask.id,
            },
        )
        self.ps._persist()
        return subtask

    def update_subtask(
        self,
        project_id: str,
        task_id: str,
        sub_id: str,
        updates: Dict[str, Any],
        user: str,
    ) -> Subtask:
        subtask = self._get_subtask(project_id, task_id, sub_id)
        for field, value in updates.items():
            if hasattr(subtask, field):
                setattr(subtask, field, value)
        subtask.updated_at = datetime.utcnow()
        self.ps._record_history(
            self.ps.projects[project_id],
            "subtask-updated",
            user,
            {"task_id": task_id, "subtask_id": sub_id, **updates},
        )
        self.ps._persist()
        return subtask

    def close_subtask(
        self,
        project_id: str,
        task_id: str,
        sub_id: str,
        user: str,
    ) -> Subtask:
        return self.update_subtask(
            project_id,
            task_id,
            sub_id,
            {"status": Status.completed},
            user,
        )

    def delete_subtask(
        self,
        project_id: str,
        task_id: str,
        sub_id: str,
        user: str,
    ):
        task = self._get_task(project_id, task_id)
        task.subtasks = [st for st in task.subtasks if st.id != sub_id]
        self.ps._record_history(
            self.ps.projects[project_id],
            "subtask-deleted",
            user,
            {"task_id": task_id, "subtask_id": sub_id},
        )
        self.ps._persist()

    # ---------- Helpers ---------- #

    def _get_task(
        self,
        project_id: str,
        task_id: str,
    ) -> Task:
        project = self.ps.projects[project_id]
        task = next(
            (t for t in project.tasks if t.id == task_id),
            None,
        )
        if not task:
            raise KeyError("Tarea no encontrada")
        return task

    def _get_subtask(
        self,
        project_id: str,
        task_id: str,
        sub_id: str,
    ) -> Subtask:
        task = self._get_task(project_id, task_id)
        subtask = next(
            (s for s in task.subtasks if s.id == sub_id),
            None,
        )
        if not subtask:
            raise KeyError("Subtarea no encontrada")
        return subtask
