import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASKS_FILE = Path("data.json")
TASK_STATUSES = {"todo", "in-progress", "done"}


class TaskTrackerError(Exception):
    pass


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _save_tasks(tasks: list[dict[str, Any]], file_path: Path) -> None:
    temporary_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=file_path.parent,
            delete=False,
        ) as temporary_file:
            temporary_path = temporary_file.name
            json.dump(tasks, temporary_file, indent=4)
            temporary_file.write("\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, file_path)
    except OSError as error:
        if temporary_path is not None:
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass
        raise TaskTrackerError(f"Could not save tasks: {error}") from error


def _load_tasks(file_path: Path = TASKS_FILE) -> list[dict[str, Any]]:
    if not file_path.exists():
        _save_tasks([], file_path)
        return []

    try:
        file_contents = file_path.read_text(encoding="utf-8")
    except OSError as error:
        raise TaskTrackerError(f"Could not read tasks: {error}") from error

    if not file_contents.strip():
        _save_tasks([], file_path)
        return []

    try:
        stored_tasks = json.loads(file_contents)
    except json.JSONDecodeError as error:
        raise TaskTrackerError(f"{file_path} contains invalid JSON.") from error

    if not isinstance(stored_tasks, list):
        raise TaskTrackerError(f"{file_path} must contain a JSON list.")

    tasks: list[dict[str, Any]] = []
    migrated = False
    seen_ids: set[int] = set()
    migration_time = _timestamp()

    for item in stored_tasks:
        if not isinstance(item, dict):
            raise TaskTrackerError(f"{file_path} contains a task that is not an object.")

        if "id" not in item and "key" in item and "descr" in item:
            item = {
                "id": item["key"],
                "description": item["descr"],
                "status": "todo",
                "createdAt": migration_time,
                "updatedAt": migration_time,
            }
            migrated = True

        task_id = item.get("id")
        description = item.get("description")
        status = item.get("status")
        created_at = item.get("createdAt")
        updated_at = item.get("updatedAt")

        if isinstance(task_id, bool) or not isinstance(task_id, int) or task_id < 1:
            raise TaskTrackerError(f"{file_path} contains an invalid task ID.")
        if task_id in seen_ids:
            raise TaskTrackerError(f"{file_path} contains duplicate task ID {task_id}.")
        if not isinstance(description, str) or not description.strip():
            raise TaskTrackerError(f"Task {task_id} has an invalid description.")
        if not isinstance(status, str) or status not in TASK_STATUSES:
            raise TaskTrackerError(f"Task {task_id} has an invalid status.")
        if not isinstance(created_at, str) or not isinstance(updated_at, str):
            raise TaskTrackerError(f"Task {task_id} has invalid timestamps.")

        seen_ids.add(task_id)
        tasks.append(
            {
                "id": task_id,
                "description": description,
                "status": status,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

    if migrated:
        _save_tasks(tasks, file_path)
    return tasks


def add_task(description: str, file_path: Path = TASKS_FILE) -> dict[str, Any]:
    cleaned_description = description.strip()
    if not cleaned_description:
        raise TaskTrackerError("Task description cannot be empty.")

    tasks = _load_tasks(file_path)
    task_id = max((task["id"] for task in tasks), default=0) + 1
    now = _timestamp()
    task = {
        "id": task_id,
        "description": cleaned_description,
        "status": "todo",
        "createdAt": now,
        "updatedAt": now,
    }
    tasks.append(task)
    _save_tasks(tasks, file_path)
    return task


def update_task(task_id: int, description: str, file_path: Path = TASKS_FILE) -> dict[str, Any]:
    cleaned_description = description.strip()
    if not cleaned_description:
        raise TaskTrackerError("Task description cannot be empty.")

    tasks = _load_tasks(file_path)
    for task in tasks:
        if task["id"] == task_id:
            task["description"] = cleaned_description
            task["updatedAt"] = _timestamp()
            _save_tasks(tasks, file_path)
            return task
    raise TaskTrackerError(f"Task with ID {task_id} was not found.")


def delete_task(task_id: int, file_path: Path = TASKS_FILE) -> None:
    tasks = _load_tasks(file_path)
    remaining_tasks = [task for task in tasks if task["id"] != task_id]
    if len(remaining_tasks) == len(tasks):
        raise TaskTrackerError(f"Task with ID {task_id} was not found.")
    _save_tasks(remaining_tasks, file_path)


def mark_task(task_id: int, status: str, file_path: Path = TASKS_FILE) -> dict[str, Any]:
    if status not in TASK_STATUSES:
        raise TaskTrackerError(f"Unsupported task status: {status}.")

    tasks = _load_tasks(file_path)
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = status
            task["updatedAt"] = _timestamp()
            _save_tasks(tasks, file_path)
            return task
    raise TaskTrackerError(f"Task with ID {task_id} was not found.")


def list_tasks(status: str | None = None, file_path: Path = TASKS_FILE) -> list[dict[str, Any]]:
    if status is not None and status not in TASK_STATUSES:
        raise TaskTrackerError(f"Unsupported task status: {status}.")

    tasks = _load_tasks(file_path)
    if status is None:
        return tasks
    return [task for task in tasks if task["status"] == status]
