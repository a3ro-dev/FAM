import libs.doubly_linked_list as dll
import datetime

class TaskManager:
    def __init__(self):
        self.tasks = dll.DoublyLinkedList()
        self.last_reset_time = datetime.datetime.utcnow()

    def check_and_reset_if_needed(self) -> None:
        current_time = datetime.datetime.now(datetime.UTC)
        if (current_time - self.last_reset_time) > datetime.timedelta(hours=24):
            self.tasks = dll.DoublyLinkedList()  # Reset the tasks list
            self.last_reset_time = current_time
            print("Task list has been reset.")

    def add_task_at_start(self, task_name: str) -> None:
        self.check_and_reset_if_needed()
        self.tasks.insert_at_start(task_name)

    def search_task(self, task_name: str) -> bool:
        self.check_and_reset_if_needed()
        return self.tasks.search(task_name)

    def display_tasks(self) -> list:
        self.check_and_reset_if_needed()
        return self.tasks.to_list()