"""
==========================================================
Automation - Task Scheduler
==========================================================
"""

from typing import Callable, List, Dict, Any

class AutomationScheduler:
    def __init__(self):
        self.registered_tasks = []

    def schedule_daily(self, task_name: str, callback: Callable) -> None:
        self.registered_tasks.append({"name": task_name, "interval": "daily", "callback": callback})

scheduler = AutomationScheduler()
