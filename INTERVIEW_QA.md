# ai-incident-investigation — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does ai-incident-investigation address, and what can you demonstrate?

Send a snapshot: OOMKilled, memory percent, restart count. If the container was OOMKilled and memory was at or above 90 percent, the response names that hypothesis and lists the evidence.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/incident/main.py`](src/incident/main.py): Implementation or supporting configuration.
- [`src/incident/ops.py`](src/incident/ops.py): Implementation or supporting configuration.
- [`src/incident/investigate.py`](src/incident/investigate.py): Implementation or supporting configuration.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`Dockerfile`](Dockerfile): Container build/service configuration.
- [`Makefile`](Makefile): Implementation or supporting configuration.
- [`docker-compose.yml`](docker-compose.yml): Container build/service configuration.
- [`tests/test_incident.py`](tests/test_incident.py): Executable checks and regression examples.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `investigate` and explain the decision it makes?

The main walkthrough here is `investigate(snapshot)` in [`src/incident/investigate.py`](src/incident/investigate.py#L1).

```python
def investigate(snapshot):
    evidence = []
    if snapshot.get("oom_killed"):
        evidence.append("container OOMKilled")
    if snapshot.get("memory_percent", 0) >= 90:
        evidence.append("memory at or above 90 percent")
    if snapshot.get("restart_count", 0) >= 3:
        evidence.append("three or more restarts")
    hypotheses = []
    if "container OOMKilled" in evidence and "memory at or above 90 percent" in evidence:
        hypotheses.append({
            "id": "memory-limit",
            "statement": "The container was OOMKilled while memory was already high.",
            "evidence": evidence,
        })
    return {"confirmed_root_cause": False, "hypotheses": hypotheses, "evidence": evidence}
```

The implementation calls `evidence.append`, `hypotheses.append`, `snapshot.get`. In an interview, trace those calls in execution order using a fixture input.

## 4. What input validation and failure behavior are implemented?

Explicit failure paths include:

- `HTTPException(status_code=404, detail='workspace not found')` in [`src/incident/ops.py`](src/incident/ops.py#L77).
- `HTTPException(status_code=404, detail='job not found')` in [`src/incident/ops.py`](src/incident/ops.py#L100).
- `HTTPException(status_code=404, detail='job not found')` in [`src/incident/ops.py`](src/incident/ops.py#L109).
- `HTTPException(status_code=403, detail='production apply is disabled in this lab')` in [`src/incident/ops.py`](src/incident/ops.py#L113).

I would test both the condition that reaches each exception and the caller that translates it. An explicit raise does not mean every malformed input or dependency failure is handled.

## 5. Which test would you use to demonstrate correctness?

[`tests/test_incident.py`](tests/test_incident.py#L8) contains `test_memory_evidence_is_a_hypothesis_not_a_confirmed_cause`:

```python
def test_memory_evidence_is_a_hypothesis_not_a_confirmed_cause():
    body = client.post("/investigations", json={"service": "billing", "oom_killed": True, "memory_percent": 94, "restart_count": 4}).json()
    assert body["confirmed_root_cause"] is False
    assert body["hypotheses"][0]["id"] == "memory-limit"
    quiet = client.post("/investigations", json={"service": "billing"}).json()
    assert quiet["hypotheses"] == []
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 6. What HTTP interface does the code expose?

- `POST /investigations` → `create` in [`src/incident/main.py`](src/incident/main.py#L19).
- `GET /readyz` → `readyz` in [`src/incident/ops.py`](src/incident/ops.py#L74).
- `POST /workspaces` → `create_workspace` in [`src/incident/ops.py`](src/incident/ops.py#L80).
- `GET /workspaces` → `list_workspaces` in [`src/incident/ops.py`](src/incident/ops.py#L98).
- `POST /workspaces/{workspace_id}/jobs` → `create_job` in [`src/incident/ops.py`](src/incident/ops.py#L106).
- `GET /jobs/{job_id}` → `get_job` in [`src/incident/ops.py`](src/incident/ops.py#L130).
- `POST /jobs/{job_id}/approve` → `approve_job` in [`src/incident/ops.py`](src/incident/ops.py#L140).
- `GET /audit` → `audit` in [`src/incident/ops.py`](src/incident/ops.py#L160).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 7. Where does state live, and what happens with multiple workers?

Module-level containers include `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS` in [`src/incident/ops.py`](src/incident/ops.py).

These containers belong to a Python process. Inspect which are constant fixtures and which are mutated. Mutable process state needs an explicit shared-storage or synchronization strategy before multiple workers can provide consistent behavior.

## 8. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 9. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 10. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 11. What is the input-to-output contract of `investigate`?

In [`src/incident/investigate.py`](src/incident/investigate.py#L1), `investigate(snapshot)` receives the inputs. The function computes these intermediate values:

- `evidence = []`
- `hypotheses = []`

Its result is defined by:

- `{'confirmed_root_cause': False, 'hypotheses': hypotheses, 'evidence': evidence}`

## 12. Which decision rules or boundary conditions should an interviewer challenge?

The implementation in [`src/incident/investigate.py`](src/incident/investigate.py#L1) branches on:

- `snapshot.get('oom_killed')`
- `snapshot.get('memory_percent', 0) >= 90`
- `snapshot.get('restart_count', 0) >= 3`
- `'container OOMKilled' in evidence and 'memory at or above 90 percent' in evidence`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.

## 13. What does the operations plane add, and where is its limit?

[`src/incident/ops.py`](src/incident/ops.py) declares `GET /readyz`, `POST /workspaces`, `GET /workspaces`, `POST /workspaces/{workspace_id}/jobs`, `GET /jobs/{job_id}`, `POST /jobs/{job_id}/approve`, `GET /audit`, `GET /metrics`. Inspect the application’s `include_router` call for its URL prefix.

Its state containers are `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS`. The job-approval handler defines whether a target is accepted or refused; check that branch and the associated tests instead of treating a recorded job as a successful infrastructure apply.
