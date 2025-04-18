[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/4VaBY3on)
# Test Routing Suite

This repository provides a comprehensive suite for testing, visualizing, and evaluating two routing algorithms. It includes scripts for running tests on different router classes, visualizing the network, and evaluating code quality.

---

## **Contents**

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Usage](#usage)
   - [Run All Tests](#run-all-tests)
   - [Visualize Network](#visualize-network)
   - [Run a Single Test](#run-a-single-test)
   - [Code Quality Check](#code-quality-check)
4. [Configuration Files](#configuration-files)
5. [Grading Scheme](#grading-scheme)
6. [Troubleshooting](#troubleshooting)
7. [Resources](#resources)

---

## **Requirements**

- **Python 3.10 or higher**
- Required Python modules:
  - `dijkstar`
  - `networkx`
  - `pylint`
  - `radon`
  - `tabulate`
  - `tkinter` (needed for visualization only)

## **Installation**

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```
2. Install required dependencies (if not already installed):

   ```bash
   pip install -r requirements.txt
   ```
3. Verify that `tkinter` is installed:

   ```bash
   python3 -m tkinter
   ```

   If the GUI doesn't appear, follow the [Tkinter installation guide](https://chatgpt.com/?temporary-chat=true#tkinter).

---

💡 **Bonus Tip:**

For much faster dependency installation, try [`uv`](https://github.com/astral-sh/uv), a lightning-fast alternative to `pip`.

#### 🚀 Install `uv` :

```bash
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installing, use it just like pip:

```bash
uv pip install -r requirements.txt
```

> ⚡ `uv` dramatically speeds up installs and works as a drop-in replacement for most pip workflows.

## **Usage**

### **Run All Tests**

Run all test cases for both `DV` and `LS` router classes and calculate the total score:

```bash
python3 runAll.py
```

- **Outputs**:
  - Scores for each test case and router class.
  - Total grade including bonus points (if applicable).

---

### **Visualize Network**

Use the `visualise_network.py` script to visualize network configurations:

```bash
python3 visualize_network.py <test_config.json>
```

- Replace `<test_config.json>` with the path to your test configuration file (e.g., `test1.json`).
- A GUI window will display the network topology, routing paths, and packet movements.

---

### **Run a Single Test**

To run a single test case manually, use the `network.py` script:

```bash
python3 network.py <test_config.json> <router_class>
```

- Replace `<test_config.json>` with the test configuration file (e.g., `test1.json`).
- Replace `<router_class>` with either `DV` or `LS` to specify the router class.

Example:

```bash
python3 network.py test2.json DV
```

---

## **Grading Scheme**

> ***Bonus marks will only be given if you score full in DV and have non-zero marks in LS.***

| Test Name              | Router Class | Description                              | Points |
| ---------------------- | ------------ | ---------------------------------------- | ------ |
| **Test 1**       | DV, LS       | Small networks                           | 3      |
| **Test 2**       | DV, LS       | Small networks with link changes         | 5-1    |
| **Test 3**       | DV, LS       | Medium network                           | 10     |
| **Test 4**       | DV, LS       | Large network                            | 12     |
| **Test 5**       | DV, LS       | Large networks with link changes         | 15-5   |
| **Bonus**        | DV           | Bonus for implementing both router types | 10     |
| **Code Quality** | LS           | Adherence to good coding practices       | 5      |

## Code Quality Check

### Overview

**`ReviewCodeQuality.py`** ensures the code adheres to standards of:

- **Maintainability**
- **Modularity**
- **Cyclomatic Complexity**
- **Comments Documentation**

It evaluates files using tools like **Radon** and **Pylint**, scoring them on various metrics.

### Metrics and Scoring

1. **Maintainability Index (MI)**

   - Scored using Radon:
     - Grade A/B: **1 point**
     - Grade C: **0.75 points**
     - Grade D: **0.5 points**
     - Grade E: **0.25 points**
     - Grade F: **0.1 points**
2. **Cyclomatic Complexity (CC)**

   - Graded by Radon:
     - Grade A/B: **1 point**
     - Grade C: **0.75 points**
     - Grade D: **0.5 points**
     - Grade E: **0.25 points**
     - Grade F: **0.1 pointsPylint Score**
3. - Scaled to **2.5 points**:
     - 9–10: **2.5 points**
     - 7–8: **2 points**
     - 5–6.9: **1.5 points**
     - 3–4.9: **1 point**
     - Below 3: **0.5 points**
4. **Comments Ratio**

   - Based on percentage of comments in the code:
     - ≥15%: **0.5 points**
     - 10–14.9%: **0.45 points**
     - 5–9.9%: **0.35 points**
     - 2–4.9%: **0.25 points**
     - <2%: **0.1 points**

---

### Running Code Quality Checks

```bash
python3 ReviewCodeQuality.py <file_paths>
```

#### Example

```bash
python3 ReviewCodeQuality.py LSrouter.py DVrouter.py
```

### Output Example

```bash
Processing: client.py
Results for client.py:
  Modularity: 1/1
  Cyclomatic Complexity: 1/1
  Pylint Rating: 2/2.5
  Comments Ratio: 0.45/0.5
  Final Score: 4.95/5

Processing: server.py
Results for server.py:
  Modularity: 0.75/1
  Cyclomatic Complexity: 0.75/1
  Pylint Rating: 1.5/2.5
  Comments Ratio: 0.35/0.5
  Final Score: 3.35/5

Average Score for 2 file(s): 4.15/5
```

---

## Docker Setup

A **Dockerfile** is included for consistent testing. Use the following steps:

1. **Build and Run Container**:

   ```bash
   docker compose run --rm netcen-spring-2025
   # or
   docker-compose run --rm netcen-spring-2025
   ```

   **What this command does**:

   - **`run`**: Executes the `netcen-spring-2025` service defined in the `docker-compose.yml` file as a temporary, one-off container.
   - **`--rm`**: Automatically removes the container after the task completes, ensuring no leftover containers clutter the system.
   - This command starts the container and runs the service or command specified for `netcen-spring-2025` in `docker-compose.yml`.
2. **Access Code**:

   - Code is mounted at `/home/netcen_pa3` inside the container. This allows you to access and work with your files directly within the container.

---

## **Troubleshooting**

### Common Issues and Fixes

#### **1. Tkinter GUI Does Not Work**

- Ensure `tkinter` is installed on your system.
- Verify with:

  ```bash
  python3 -m tkinter
  ```
- Follow the [Tkinter Installation Guide](#resources) if needed.

### **Installing Tkinter: A Comprehensive Guide**

Tkinter is the standard GUI toolkit for Python and is included with most Python distributions. However, on some systems or Python installations, it might not be properly configured or installed. This guide walks you through the steps to ensure Tkinter is correctly set up, covering various platforms and common issues.

---

### **What Is Tkinter?**

- Tkinter is Python's standard library for building graphical user interfaces (GUIs).
- It relies on **Tcl/Tk**, a cross-platform GUI toolkit, to function.
- Python interacts with Tcl/Tk through the `_tkinter` module.

---

### **How to Check if Tkinter Is Installed**

1. Open a terminal and run:
   ```bash
   python3 -m tkinter
   ```
2. If Tkinter is installed correctly, a small GUI window should appear.
3. If you see an error like `ModuleNotFoundError: No module named '_tkinter'`, follow the installation steps below.

---

### **Installing Tkinter on Different Platforms**

#### **1. macOS**

1. **Install Tcl/Tk:**
   Use Homebrew to install Tcl/Tk, which is required for Tkinter.

   ```bash
   brew install tcl-tk
   ```
2. **Install the `python-tk` Formula:**
   Homebrew provides a separate formula for Tkinter:

   ```bash
   brew install python-tk@<version>
   ```

   Replace `<version>` with the version of Python you are using (e.g., `python-tk@3.13`).
3. **Verify Installation:**

   ```bash
   python3 -m tkinter
   ```

   If a GUI window appears, Tkinter is installed correctly.

---

#### **2. Linux (Debian/Ubuntu)**

1. **Install Tkinter via Package Manager:**
   Use `apt` to install Tkinter:

   ```bash
   sudo apt-get update
   sudo apt-get install python3-tk
   ```
2. **Verify Installation:**

   ```bash
   python3 -m tkinter
   ```

   If a GUI window appears, Tkinter is installed correctly.

---

#### **3. Windows**

1. **Ensure Tcl/Tk Is Included During Python Installation:**

   - Download the official Python installer from [python.org](https://www.python.org/downloads/).
   - During installation, select "Customize installation."
   - Ensure the "tcl/tk and IDLE" option is checked.
2. **Verify Installation:**

   ```bash
   python3 -m tkinter
   ```

   If a GUI window appears, Tkinter is installed correctly.

---

### **Common Issues and Solutions**

#### **1. Missing `_tkinter` Module**

- **Cause:** Python was built without Tcl/Tk support.
- **Solution:** Reinstall Python with Tcl/Tk support, ensuring Tcl/Tk is installed before Python.

#### **2. Virtual Environment Issues**

- **Cause:** Tkinter is not included in virtual environments by default.
- **Solution:** Install Tkinter in the base Python installation, then recreate your virtual environment.

#### **3. Conflicting Tcl/Tk Versions**

- **Cause:** The system has multiple Tcl/Tk versions, and Python links to the wrong one.
- **Solution:** Use `brew info tcl-tk` (macOS) or verify paths during Python configuration.

#### **4. Environment Variables Not Set**

- **Cause:** Python cannot locate Tcl/Tk libraries.
- **Solution:** Export the necessary environment variables (macOS/Linux):
  ```bash
  export LDFLAGS="-L/opt/homebrew/opt/tcl-tk/lib"
  export CPPFLAGS="-I/opt/homebrew/opt/tcl-tk/include"
  ```

---

### **Rebuilding Python with Tcl/Tk Support**

If the above steps do not work, you may need to rebuild Python from source.

1. **Download the Python Source Code:**

   ```bash
   curl -O https://www.python.org/ftp/python/<version>/Python-<version>.tgz
   tar xzf Python-<version>.tgz
   cd Python-<version>
   ```

   Replace `<version>` with your Python version (e.g., `3.13.1`).
2. **Configure with Tcl/Tk Paths:**

   ```bash
   ./configure --with-tcltk-includes='-I/opt/homebrew/opt/tcl-tk/include' --with-tcltk-libs='-L/opt/homebrew/opt/tcl-tk/lib'
   ```
3. **Build and Install:**

   ```bash
   make
   sudo make install
   ```

---

### **Testing Your Installation**

After completing the installation steps, verify Tkinter functionality:

1. Open a Python REPL:
   ```bash
   python3
   ```
2. Run the following code:
   ```python
   from tkinter import Tk
   root = Tk()
   print("Tkinter is working!")
   root.mainloop()
   ```

---

### **Resources**

- [Python Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [TkDocs Tutorial](https://tkdocs.com/tutorial/index.html)
- [Homebrew Tcl-Tk Formula](https://formulae.brew.sh/formula/tcl-tk)
