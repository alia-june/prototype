"""Subprocess used only by bounded crash-recovery validation."""
import os
from pathlib import Path
import sys

from docstream_cpu.service import DocumentService
from docstream_cpu.storage import Store

target = sys.argv[2]
def fault(phase):
    if phase == target:
        os._exit(71)

with Store(Path(sys.argv[1]), fault=fault) as store:
    DocumentService(store).ingest({"request_key": "crash", "text": "recover"})
