# Validation boundary

The test suite exercises six synthetic receipt-envelope fixtures, plus unknown
tool and insufficient-receipt refusals. It verifies that fixture files are not
written during evaluation and that the example source imports no declared
subprocess or network client module.

The tests establish only deterministic classification of these declared fixture
facts. They do not validate a real Mill batch, invoke a controller, prove a
receipt's truth, establish LLM egress absence for the wider host, or grant a
human or system authority to take the next action.

Run the suite with:

```text
python -B -m unittest tests/test_expert_system.py
```
