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