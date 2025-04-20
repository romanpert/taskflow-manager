# =============================================================
# file: models.py
# =============================================================
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any

from pydantic import BaseModel, Field, validator


class Status(str, Enum):
    pending = "pending"
    active = "active"
    in_progress = "in-progress"
    completed = "completed"
    closed = "closed"
    archived = "archived"


class HistoryEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: str
    user: str
    details: Optional[Dict[str, Any]] = None


class Attachment(BaseModel):
    name: str
    url: str
    type: Optional[str] = None


class Notification(BaseModel):
    kind: str = Field("reminder", alias="tipo")
    datetime: datetime = Field(alias="fecha")
    message: str = Field(alias="mensaje")


class Subtask(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    status: Status = Status.pending
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    history: List[HistoryEntry] = []

    @validator("updated_at", always=True)
    def set_updated(cls, v, values):
        return v or values.get("created_at")


class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    start_date: Optional[datetime] = Field(None, alias="fecha_inicio")
    end_date: Optional[datetime] = Field(None, alias="fecha_fin")
    status: Status = Status.pending
    assignees: List[str] = Field(default_factory=list, alias="asignados")
    priority: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list, alias="etiquetas")
    subtasks: List[Subtask] = Field(default_factory=list)
    history: List[HistoryEntry] = Field(default_factory=list)
    attachments: List[Attachment] = Field(default_factory=list, alias="adjuntos")
    notifications: List[Notification] = Field(default_factory=list, alias="notificaciones")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, alias="campos_personalizados")


class Project(BaseModel):
    id: str
    name: str = Field(alias="nombre")
    description: Optional[str] = Field(None, alias="descripcion")
    status: Status = Status.active
    start_date: Optional[datetime] = Field(None, alias="fecha_inicio")
    end_date: Optional[datetime] = Field(None, alias="fecha_fin")
    owners: List[str] = Field(default_factory=list, alias="responsables")
    tags: List[str] = Field(default_factory=list, alias="etiquetas")
    tasks: List[Task] = Field(default_factory=list)
    history: List[HistoryEntry] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict, alias="campos_personalizados")