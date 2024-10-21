import libs.doubly_linked_list as dll
import datetime
import threading
import time
import subprocess
import logging

class TaskManager:
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

    def set_timer(self, seconds: int) -> None:
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