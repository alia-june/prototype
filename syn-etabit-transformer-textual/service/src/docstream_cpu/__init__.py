"""M1 CPU reference library. No service or renderer is started by importing it."""
from .catalog import CpuModel
from .errors import ModelError
from .executor import reference_execute
from .models import Block, Properties, Snapshot, Style, text_digest
from .operations import Batch, parse_batch
from .planner import execute, plan
from .rich import Snapshot2, RichBlock, Span, TableRow, TableCell, CellText, ImageRef, parse_snapshot

__version__ = "0.2.0.dev4"
__all__ = ["CpuModel", "ModelError", "Block", "Properties", "Snapshot", "Style", "Batch",
           "text_digest", "parse_batch", "plan", "execute", "reference_execute", "Snapshot2", "RichBlock", "Span", "TableRow", "TableCell", "CellText", "ImageRef", "parse_snapshot"]
