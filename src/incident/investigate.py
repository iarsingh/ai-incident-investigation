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
