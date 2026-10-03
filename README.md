# AI incident investigation platform

Level: Advanced

Skills: Logs, Kubernetes signals, a hypothesis, FastAPI

Send a snapshot: OOMKilled, memory percent, restart count. If the container was OOMKilled and memory was at or above 90 percent, the response names that hypothesis and lists the evidence.

`confirmed_root_cause` stays false. A person confirms a cause. This service does not query a live cluster; you pass the snapshot.

```bash
pip install -r requirements.txt
pytest -q
```

