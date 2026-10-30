import argparse
import sys

from app import TaskTrackerError, add_task, delete_task, list_tasks, mark_task, update_task


def positive_integer(value: str) -> int:
    try:
        task_id = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("ID must be a positive integer.") from error
    if task_id < 1:
        raise argparse.ArgumentTypeError("ID must be a positive integer.")
    return task_id


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="task-cli")
    commands = parser.add_subparsers(dest="command", required=True)

    add_command = commands.add_parser("add")
    add_command.add_argument("description")

    update_command = commands.add_parser("update")
    update_command.add_argument("id", type=positive_integer)
    update_command.add_argument("description")

    delete_command = commands.add_parser("delete")
    delete_command.add_argument("id", type=positive_integer)

    in_progress_command = commands.add_parser("mark-in-progress")
    in_progress_command.add_argument("id", type=positive_integer)

    done_command = commands.add_parser("mark-done")
    done_command.add_argument("id", type=positive_integer)

    list_command = commands.add_parser("list")
    list_command.add_argument("status", nargs="?", choices=("todo", "in-progress", "done"))

    return parser


def print_tasks(tasks: list[dict[str, object]]) -> None:
    if not tasks:
        print("No tasks found.")
        return

    print("ID | STATUS      | DESCRIPTION")
    for task in tasks:
        print(f'{task["id"]} | {task["status"]:<11} | {task["description"]}')


def main() -> int:
    parser = build_parser()
    arguments = parser.parse_args()

    try:
        if arguments.command == "add":
            task = add_task(arguments.description)
            print(f'Task added successfully (ID: {task["id"]})')
        elif arguments.command == "update":
            update_task(arguments.id, arguments.description)
            print(f"Task {arguments.id} updated successfully.")
        elif arguments.command == "delete":
            delete_task(arguments.id)
            print(f"Task {arguments.id} deleted successfully.")
        elif arguments.command == "mark-in-progress":
            mark_task(arguments.id, "in-progress")
            print(f"Task {arguments.id} marked as in progress.")
        elif arguments.command == "mark-done":
            mark_task(arguments.id, "done")
            print(f"Task {arguments.id} marked as done.")
        else:
            print_tasks(list_tasks(arguments.status))
    except TaskTrackerError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
