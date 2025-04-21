from datetime import datetime
from typing import Any, Dict, Optional

from .models import HistoryEntry, Project, Status
from .persistence import load_projects, save_projects


class ProjectService:
    def __init__(self):
        self.projects: Dict[str, Project] = load_projects()

    # ---------- Helpers ---------- #

    def _record_history(
        self,
        project: Project,
        action: str,
        user: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        entry = HistoryEntry(
            action=action,
            user=user,
            details=details,
        )
        project.history.append(entry)

    def _persist(self):
        save_projects(self.projects)

    # ---------- CRUD ---------- #

    def create(
        self,
        data: Dict[str, Any],
        user: str,
    ) -> Project:
        if data["id"] in self.projects:
            raise ValueError(f"El proyecto {data['id']} ya existe")
        project = Project.parse_obj(data)
        self._record_history(project, "created", user)
        self.projects[project.id] = project
        self._persist()
        return project

    def update(
        self,
        project_id: str,
        updates: Dict[str, Any],
        user: str,
    ) -> Project:
        if project_id not in self.projects:
            raise KeyError("Proyecto no encontrado")
        project = self.projects[project_id]
        for field, value in updates.items():
            if hasattr(project, field):
                setattr(project, field, value)
            else:
                project.custom_fields[field] = value
        project.status = updates.get("status", project.status)
        self._record_history(
            project,
            "updated",
            user,
            details=updates,
        )
        self._persist()
        return project

    def close(
        self,
        project_id: str,
        user: str,
    ) -> Project:
        project = self.projects[project_id]
        project.status = Status.closed
        project.end_date = project.end_date or datetime.utcnow()
        self._record_history(project, "closed", user)
        self._persist()
        return project

    def delete(
        self,
        project_id: str,
        user: str,
    ):
        if project_id not in self.projects:
            raise KeyError("Proyecto no encontrado")
        removed = self.projects.pop(project_id)
        self._persist()
        return removed
