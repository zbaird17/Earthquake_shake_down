# Earthquake Shake-Down Desktop App

Earthquake Shake-Down is a Python Tkinter 2D structural-dynamics simulator. It includes
grid-snapped structural placement, floor masses, gravity modes, sine-wave shaking,
Pymunk rigid-body physics, fatigue tracking, design import/export, and test controls.

## Requirements

- Windows
- Python 3.10 or newer
- Tkinter, included with the standard Python installer for Windows

The required Python packages are:

- NumPy
- Matplotlib
- Pymunk

## Install

Open PowerShell in the project directory:

```powershell
cd "C:\Users\zacha\OneDrive\CCE 270\earthquake_desktop"
```

Create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the packages:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Tkinter is normally installed with Python on Windows. If it is missing, reinstall
Python from python.org with the **tcl/tk and IDLE** feature enabled.

## Run

With the virtual environment activated:

```powershell
python app.py
```

You can also run the app directly if the required packages are installed in the
selected Python environment:

```powershell
py app.py
```

## Test

Run the included focused test suite:

```powershell
python -m unittest discover -s tests -v
```

## Basic Use

1. Select a structural tool from the left sidebar.
2. Use the grid to place columns, beams, braces, or floor masses.
3. Drag a member or floor mass to move it.
4. Drag a member endpoint or floor-mass corner to change its size or shape.
5. Click a P/M badge to switch the joint between pinned and moment-frame behavior.
6. Choose the amplitude, frequency, duration, and gravity mode.
7. Click **Start Test**, and use **End Test** after a finite test completes.

Saved designs are JSON files. Use **Save Design** and **Import Design** in the app
sidebar. Import/export is unavailable during a test.