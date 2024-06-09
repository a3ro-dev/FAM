import threading
import libs.gpt as gpt
gen = gpt.Generation()

class Clock:
    def __init__(self):
        self.todo_list = []
        self.timer = None

    def add_todo(self, task):
        self.todo_list.append(task)

    def remove_todo(self, task):
        if task in self.todo_list:
            self.todo_list.remove(task)

    def view_todos(self):
        return self.todo_list

    def set_timer(self, seconds):
        if self.timer is not None:
            self.timer.cancel()
        self.timer = threading.Timer(seconds, self.timer_callback)
        self.timer.start()

    def timer_callback(self):
        print("Timer finished!")

# Usage
module = Clock()
module.add_todo("Finish project")
module.add_todo("Review code")
print(module.view_todos())  # ["Finish project", "Review code"]
module.remove_todo("Finish project")
print(module.view_todos())  # ["Review code"]
module.set_timer(5)  # Sets a timer for 5 seconds