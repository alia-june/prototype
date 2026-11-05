from pathlib import Path
from tempfile import TemporaryDirectory
from durable_workspace import DurableWorkspace

with TemporaryDirectory() as td:
    root = Path(td) / "workspace"
    ws = DurableWorkspace.init(root)
    ws.set("project", {"name": "demo", "phase": 1})
    ws.set("tasks", ["inspect", "checkpoint", "recover"])
    snapshot = ws.checkpoint()
    print(ws.verify())
    recovered = DurableWorkspace.recover(snapshot, Path(td) / "recovered")
    print(recovered.get("project"))
