from typing import List, Tuple
import heapq
from model import MathematicalModel

class ScheduleBuilder:
    def __init__(self, model: MathematicalModel):
        self.model = model
        self.best_profit = 0.0
        self.best_schedule = []
        self.tree = []

    def solve(self):
        self.best_profit = 0.0
        self.best_schedule = []
        self.tree = []

        pq = []
        initial_ub = self._ub([], [])
        heapq.heappush(pq, (-initial_ub, [], []))

        while pq:
            neg_ub, seq, times = heapq.heappop(pq)
            ub = -neg_ub
            node = {"sequence": seq.copy(), "start_times": times.copy(), "upper_bound": ub, "depth": len(seq), "pruned": False}
            self.tree.append(node)

            if ub <= self.best_profit:
                self.tree[-1]["pruned"] = True
                continue

            profit = self.model.profit(list(zip(seq, times)))
            if profit > self.best_profit:
                self.best_profit = profit
                self.best_schedule = list(zip(seq, times))

            if len(seq) == len(self.model.tasks):
                continue

            for tid in range(len(self.model.tasks)):
                if tid in seq:
                    continue
                start = self._est(seq, times, tid)
                if start + self.model.tasks[tid].duration > self.model.tasks[tid].window_end:
                    continue
                new_seq = seq + [tid]
                new_times = times + [start]
                new_ub = self._ub(new_seq, new_times)
                heapq.heappush(pq, (-new_ub, new_seq, new_times))
        return self.best_schedule, self.tree

    def _est(self, seq, times, tid):
        task = self.model.tasks[tid]
        if not seq:
            return task.window_start
        last_end = times[-1] + self.model.tasks[seq[-1]].duration
        return max(last_end, task.window_start)

    def _ub(self, seq, times):
        profit = self.model.profit(list(zip(seq, times)))
        remaining = [t for i,t in enumerate(self.model.tasks) if i not in seq]
        remaining.sort(key=lambda t: (t.profit / (t.duration if t.duration>0 else 1)), reverse=True)
        t = 0.0
        if seq:
            t = times[-1] + self.model.tasks[seq[-1]].duration
        ub = profit
        for task in remaining:
            est = max(t, task.window_start)
            if est + task.duration <= task.window_end:
                ub += task.profit
                t = est + task.duration
        return ub
