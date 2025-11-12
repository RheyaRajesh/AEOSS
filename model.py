from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Task:
    profit: float
    duration: float
    window_start: float
    window_end: float
    position: Tuple[float, float, float]
    id: int

class MathematicalModel:
    def __init__(self):
        self.tasks: List[Task] = []
        self.count = 0

    def add_task(self, profit, duration, w_start, w_end, pos):
        task = Task(profit, duration, w_start, w_end, pos, self.count)
        self.tasks.append(task)
        self.count += 1

    def profit(self, schedule):
        return sum(self.tasks[tid].profit for tid, _ in schedule)
