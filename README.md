# Advanced Workflow for Speech-To-Table, Vietnamese language 

Short description: this repository contains the Spring Capstone project (API + mobile client assets, models, and utilities).

**Status**
- **Deployed:** CamRanh Harbour — deployed and tested on-site for field validation.
- **Published:** Results and documentation published on FPT School Research Gate.

**Quick Start (Local Development)**
- **Prerequisites:** `Python 3.8+`, `git`, and `curl`/`wget` as needed. Ensure ports used by the app (default `8081`) are available.
- **Create and activate virtual environment:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

- **Install dependencies:**

```bash
pip install -r requirements.txt
```

- **Initialize the application database (local):**

```bash
python init_db.py
```

- **Run the application (development):**

```bash
uvicorn main:app --host 0.0.0.0 --port 8081 --reload
```

**Deploy / Run on Linux devices (Jetson Nano or similar)**
- The repository provides helper scripts for device setup and runtime. On the target device:

```bash
chmod +x install.sh run.sh
./install.sh    # performs system-level installs and prepares environment
./run.sh        # starts the application (uses the repo's environment/setup)
```

Notes:
- `install.sh` is intended to prepare native dependencies and system configuration — review it before running on production hardware.
- `run.sh` wraps the app start command; for long-running deployments consider using a process manager (systemd, docker, or supervisord).
- By default, the code running on behalf of `springcapstone2025` linux user, go to `automation-yield.service` for changing this default behaviour.

**Deployment Checklist (for testing in the field)**
1. Provision the target machine with the OS image and network access.
2. Clone this repo and copy any required model files under `models/hubs/` if not already present.
3. Follow the steps in **Quick Start** to create a virtualenv and install Python deps.
4. Run `python init_db.py` to create the local databases under `database/` (the project uses JSON DB files by default).
5. Run `./install.sh` if the target requires native packages or hardware-specific setup.
6. Start the app with `./run.sh` or `uvicorn main:app --host 0.0.0.0 --port 8081`.
7. From a test workstation, confirm API is up:

```bash
curl -v http://<device-ip>:8081/
```

8. Run through the UI flows (admin/user pages under `statics/templates/pages/`) or exercise the API routes under `/admin`, `/system`, and `/user` as needed.

**Testing & Validation Notes**
- The project was deployed and tested at CamRanh Harbour during field trials — this included connectivity, model inference, and end-to-end validation with the mobile client.
- Results, experiment notes, and related documentation have been published to FPT School Research Gate for academic review and reproducibility.

**Troubleshooting**
- If ports are in use, change `--port` in the `uvicorn` command or adjust firewall rules.
- If model files are missing, ensure `models/hubs/` contains the required model directories (see `models/` in this repo).
- For permission issues when running scripts: ensure executable bit set (`chmod +x install.sh run.sh`) and run with an appropriate user.

**Further steps / Contributions**
- To run automated tests or CI, add a test suite and a workflow file (not included by default).
- If you'd like, I can add a `systemd` service unit or a `Dockerfile` to simplify deployments — tell me which you prefer.

**Contact / Attribution**
- For questions about deployment or the field tests at CamRanh Harbour, contact me via shinigami0hacker@gmail.com 
* How to run
Running in dev-mode:
```
python -m venv .venv
./.venv/Script/activate
pip install -r requirement.txt
uvicorn main:app --host 0.0.0.0 --port 8081 --reload
```
To run deploy and run on jetson nano or any linux device, first running the install.sh and run.sh later on.
The network 