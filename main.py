from model import MathematicalModel
from solver import ScheduleBuilder
from viz import Visuals
import os
import matplotlib.pyplot as plt


def build_model():
    model = MathematicalModel()
    model.add_task(100, 30, 0, 60, (1.2, 0.2, 0.1))
    model.add_task(80, 20, 10, 50, (0.2, 1.1, 0.0))
    model.add_task(120, 40, 20, 80, (-1.0, -0.2, 0.0))
    model.add_task(90, 25, 30, 90, (0.0, -1.0, 0.2))
    model.add_task(110, 35, 40, 100, (0.7, 0.7, 0.1))
    model.add_task(70, 15, 50, 85, (-0.7, 0.7, 0.0))
    model.add_task(130, 45, 60, 120, (0.0, 0.0, 1.2))
    model.add_task(95, 30, 70, 130, (0.0, 0.0, -1.2))
    return model


def main():
    os.makedirs("visualizations", exist_ok=True)

    model = build_model()
    builder = ScheduleBuilder(model)
    schedule, tree = builder.solve()

    profit = sum(model.tasks[t].profit for t, _ in schedule)
    print(f"OPTIMAL PROFIT: ${profit:.2f}")
    print("Schedule:", schedule)

    # --- Generate visualizations ---
    # --- Generate visualizations ---
    v = Visuals(tree, model)
    v.search_tree()                    # saves visualizations/search_tree.png
    v.pruning_stats()                  # saves visualizations/pruning_statistics.png
    v.orbit(schedule)                  # saves visualizations/orbital_schedule.png
    v.timeline(schedule)               # saves visualizations/schedule_timeline.png


    # --- Timeline chart (redundant backup, optional) ---
    fig, ax = plt.subplots(figsize=(12, 4))
    yticks = []
    ylabels = []
    colors = plt.get_cmap("tab20").colors

    for i, (tid, st) in enumerate(schedule):
        task = model.tasks[tid]
        ax.barh(i, task.duration, left=st, height=0.6,
                color=colors[i % len(colors)], edgecolor="black", alpha=0.8)
        ax.text(st + task.duration / 2, i,
                f"T{task.id + 1}\n${task.profit}",
                va='center', ha='center', fontweight='bold', color='white')
        yticks.append(i)
        ylabels.append(f"Task {task.id + 1}")

    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels)
    ax.set_xlabel("Time")
    ax.set_title("Schedule Timeline", fontsize=14, fontweight='bold')
    plt.tight_layout()
    tl_path = "visualizations/schedule_timeline.png"
    plt.savefig(tl_path, dpi=150)
    plt.close()
    print(f"[INFO] Timeline saved at {tl_path}")


if __name__ == "__main__":
    main()
