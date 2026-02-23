<div align="center">
  
# AEOSS 🌍  
## **Agile Earth Observation Satellite Scheduling**

AEOSS is a **research-oriented Python project** that implements an efficient **Branch and Bound** algorithm to solve the complex scheduling problem of **agile Earth observation satellites**.

</div>

The goal is to **maximize observation profit** (scientific/commercial value) while respecting:
- Satellite **agility** (slew time, maneuver constraints)
- **Time window** availability for each target
- **On-board resource** limitations (energy, memory, etc.)

It includes **pruning strategies** for better performance and **visualization** of schedules and solutions.


## ✨ Key Features

- 🧠 **Exact Branch & Bound solver** with intelligent bounding & pruning
- 📊 **Profit maximization** under multiple realistic constraints
- 🖼️ **Visualization** of selected observations, timelines & satellite path
- 🗂️ Modular structure: model, solver, visualization separated
- ⚡ Generates output images in `/visualizations/` folder
- 🔬 Ready for experimentation, benchmarking, paper reproduction

## 🛠️ Tech Stack

| Component         | Technology              | Purpose                              |
|-------------------|-------------------------|--------------------------------------|
| Language          | Python 3.8+             | Core implementation                  |
| Algorithm         | Branch & Bound          | Exact optimization                   |
| Visualization     | Matplotlib / similar    | Schedule & result plotting           |
| Dependencies      | Listed in requirements.txt | (numpy, matplotlib, etc. likely) |

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/RheyaRajesh/AEOSS.git
cd AEOSS

# 2. (Optional but recommended) Create virtual environment
python -m venv venv
source venv/bin/activate    # Linux / macOS
venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the solver + visualization
python main.py
