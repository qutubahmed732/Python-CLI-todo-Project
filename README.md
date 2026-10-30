# Task Tracker CLI

A small command-line app for keeping everyday tasks in one place. Add a task when it comes to mind, update it as plans change, and mark it done when you finish. Your tasks are saved locally, so they are still there the next time you run the program.

This project was a challenge project from Roadmap.sh, and I made it.

Challenge link: https://roadmap.sh/projects/task-tracker

## What it can do

- Add, update, and delete tasks
- Mark tasks as `todo`, `in-progress`, or `done`
- List every task or filter by status
- Save task details and timestamps in a local JSON file
- Create `data.json` automatically the first time you use the app

## Built with

The app is written in Python and uses the standard library for command-line arguments, JSON, timestamps, and file handling. It does not need third-party packages to run. The `pyproject.toml` file registers the `task-cli` command when you install the project.

Python 3.10 or later is required.

## Get started on Windows

Open PowerShell in the project folder:

```powershell
cd "C:\Users\DELL\Desktop\stack-learnt\CLI"
```

Create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project in editable mode to make `task-cli` available inside the activated environment:

```powershell
python -m pip install -e .
```

If PowerShell says script execution is disabled, allow activation for the current PowerShell window and try again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

You can also run the app without installing it by using `python main.py` instead of `task-cli`.

## Commands

Add a task:

```powershell
task-cli add "Buy groceries"
```

List all tasks, or filter by status:

```powershell
task-cli list
task-cli list todo
task-cli list in-progress
task-cli list done
```

Update or delete a task by its ID:

```powershell
task-cli update 1 "Buy groceries and cook dinner"
task-cli delete 1
```

Change a task's status:

```powershell
task-cli mark-in-progress 1
task-cli mark-done 1
```

Task IDs are assigned automatically. The `update` and `delete` commands need the ID shown when you list your tasks.

## Where your tasks live

Tasks are stored in `data.json` in the current working directory. Each task has an ID, description, status, creation time, and last-updated time. The data file is ignored by Git so your personal task list won't be added to a normal Git commit.

To leave the virtual environment, run:

```powershell
deactivate
```
