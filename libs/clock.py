import libs.doubly_linked_list as dll
import datetime
import threading
import time
import subprocess
import logging

class TaskManager:
    """
    TaskManager class for managing tasks, reminders, timers, stopwatches, and alarms.
    Attributes:
        tasks (dll.DoublyLinkedList): A doubly linked list to store tasks.
        reminders (list): A list to store reminders as tuples of (datetime, message).
        timers (list): A list to store active timers.
        stopwatch_start_time (datetime): The start time of the stopwatch.
        alarms (list): A list to store alarm times.
        last_reset_time (datetime): The last time the task list was reset.
    Methods:
        check_and_reset_if_needed() -> None:
            Checks if the task list needs to be reset based on a 24-hour interval and resets if needed.
        add_task_at_start(task_name: str) -> None:
            Adds a task to the start of the task list after checking and resetting if needed.
        search_task(task_name: str) -> bool:
            Searches for a task in the task list after checking and resetting if needed.
        display_tasks() -> list:
            Returns a list of all tasks after checking and resetting if needed.
        set_reminder(time_str: str, message: str) -> None:
            Sets a reminder for a specific time and starts a thread to check reminders.
        check_reminders() -> None:
            Continuously checks for reminders and logs them when the time is reached.
        set_timer(seconds: float) -> None:
            Sets a timer for a specified number of seconds and starts a thread to handle it.
        start_stopwatch() -> None:
            Starts the stopwatch.
        stop_stopwatch() -> None:
            Stops the stopwatch and logs the elapsed time.
        set_alarm(time_str: str) -> None:
            Sets an alarm for a specific time and starts a thread to check alarms.
        check_alarms() -> None:
            Continuously checks for alarms and logs them when the time is reached.
    Note:
        This class is still being tested and is in the early stages of development.
    """
    def __init__(self):
        self.tasks = dll.DoublyLinkedList()
        self.reminders = []
        self.timers = []
        self.stopwatch_start_time = None
        self.alarms = []
        self.last_reset_time = datetime.datetime.utcnow()
        logging.info("TaskManager initialized.")

    def check_and_reset_if_needed(self) -> None:
        current_time = datetime.datetime.now(datetime.UTC)
        if (current_time - self.last_reset_time) > datetime.timedelta(hours=24):
            self.tasks = dll.DoublyLinkedList()  # Reset the tasks list
            self.last_reset_time = current_time
            logging.info("Task list has been reset.")

    def add_task_at_start(self, task_name: str) -> None:
        self.check_and_reset_if_needed()
        self.tasks.insert_at_start(task_name)
        logging.info(f"Task added: {task_name}")

    def search_task(self, task_name: str) -> bool:
        self.check_and_reset_if_needed()
        found = self.tasks.search(task_name)
        logging.info(f"Task {'found' if found else 'not found'}: {task_name}")
        return found

    def display_tasks(self) -> list:
        self.check_and_reset_if_needed()
        tasks = self.tasks.to_list()
        logging.info(f"Displaying tasks: {tasks}")
        return tasks

    def set_reminder(self, time_str: str, message: str) -> None:
        reminder_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        self.reminders.append((reminder_time, message))
        threading.Thread(target=self.check_reminders).start()
        logging.info(f"Reminder set for {reminder_time}: {message}")

    def check_reminders(self) -> None:
        while True:
            now = datetime.datetime.now()
            for reminder in self.reminders:
                if now >= reminder[0]:
                    logging.info(f"Reminder: {reminder[1]}")
                    self.reminders.remove(reminder)
            time.sleep(60)  # Check every minute

    def set_timer(self, seconds: float) -> None:
        def timer(seconds):
            time.sleep(seconds)
            logging.info("Time's up!")
            subprocess.run(['ffplay', '-nodisp', '-autoexit', '/path/to/alarm_chime.mp3'], check=True)

        threading.Thread(target=timer, args=(seconds,)).start()
        logging.info(f"Timer set for {seconds} seconds.")

    def start_stopwatch(self) -> None:
        self.stopwatch_start_time = datetime.datetime.now()
        logging.info("Stopwatch started.")

    def stop_stopwatch(self) -> None:
        if self.stopwatch_start_time:
            elapsed_time = datetime.datetime.now() - self.stopwatch_start_time
            logging.info(f"Stopwatch stopped. Elapsed time: {elapsed_time}")
            self.stopwatch_start_time = None
        else:
            logging.warning("Stopwatch is not running.")

    def set_alarm(self, time_str: str) -> None:
        alarm_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        self.alarms.append(alarm_time)
        threading.Thread(target=self.check_alarms).start()
        logging.info(f"Alarm set for {alarm_time}")

    def check_alarms(self) -> None:
        while True:
            now = datetime.datetime.now()
            for alarm in self.alarms:
                if now >= alarm:
                    logging.info("Alarm ringing!")
                    subprocess.run(['ffplay', '-nodisp', '-autoexit', '/path/to/alarm_chime.mp3'], check=True)
                    self.alarms.remove(alarm)
            time.sleep(60)  # Check every minute