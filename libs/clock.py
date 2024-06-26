import threading
# import libs.gpt as gpt
# gen = gpt.Generation()
import doubly_linked_list as dll
import datetime

class TaskManager:
    def __init__(self):
        self.tasks = dll.DoublyLinkedList()
        self.last_reset_time = datetime.datetime.now()

    def check_and_reset_if_needed(self):
        current_time = datetime.datetime.now()
        if (current_time - self.last_reset_time) > datetime.timedelta(hours=24):
            self.tasks = dll.DoublyLinkedList()  # Reset the tasks list
            self.last_reset_time = current_time
            print("Task list has been reset.")

    def add_task_at_start(self, task_name):
        self.check_and_reset_if_needed()
        self.tasks.insertAtStart(task_name)

    def search_task(self, task_name):
        self.check_and_reset_if_needed()
        return self.tasks.searchDLList(task_name)

    def display_tasks(self):
        self.check_and_reset_if_needed()
        return self.tasks.to_list()