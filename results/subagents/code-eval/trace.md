### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: ls
{"path": "workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool call: glob
{"pattern": "**/*", "path": "workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/__init__.py', '/workspace/bookings/__pycache__/__init__.cpython-311.pyc', '/workspace/bookings/__pycache__/__init__.cpython-314.pyc', '/workspace/bookings/__pycache__/billing.cpython-311.pyc', '/workspace/bookings/__pycache__/billing.cpython-314.pyc', '/workspace/bookings/__pycache__/calendar_export.cpython-311.pyc', '/workspace/bookings/__pycache__/calendar_export.cpython-314.pyc', '/workspace/bookings/__pycache__/schedule.cpython-311.pyc', '/workspace/bookings/__pycache__/schedule.cpython-314.pyc', '/workspace/bookings/__pycache__/timeutil.cpython-311.pyc', '/workspace/bookings/__pycache__/timeutil.cpython-314.pyc', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py', '/workspace/tests/__pycache__/test_bookings.cpython-311-pytest-9.1.1.pyc', '/workspace/tests/__pycache__/test_bookings.cpython-314-pytest-9.1.1.pyc', '/workspace/tests/test_bookings.py']

### Tool call: execute
{"command": "pytest workspace/tests"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/lab-asmlgvri
plugins: langsmith-0.14.4, anyio-4.15.1
collected 0 items / 1 error

==================================== ERRORS ====================================
______________ ERROR collecting workspace/tests/test_bookings.py _______________
ImportError while importing test module '/tmp/lab-asmlgvri/workspace/tests/test_bookings.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/home284/284-home/miniconda3/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/home284/284-home/VIN/lab20/K4-DAY20-MULTIAGENTS-TranNamAnh-2A202602901/tasks/code-eval/workspace/tests/test_bookings.py:1: in <module>
    from bookings.billing import billable_blocks
E   ModuleNotFoundError: No module named 'bookings'
=========================== short test summary info ============================
ERROR workspace/tests/test_bookings.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.13s ===============================

Exit code: 2
[Command failed with exit code 2]

### Tool call: execute
{"command": "python -m pytest workspace/tests"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/lab-asmlgvri
plugins: langsmith-0.14.4, anyio-4.15.1
collected 0 items / 1 error

==================================== ERRORS ====================================
______________ ERROR collecting workspace/tests/test_bookings.py _______________
ImportError while importing test module '/tmp/lab-asmlgvri/workspace/tests/test_bookings.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/home284/284-home/miniconda3/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/home284/284-home/VIN/lab20/K4-DAY20-MULTIAGENTS-TranNamAnh-2A202602901/tasks/code-eval/workspace/tests/test_bookings.py:1: in <module>
    from bookings.billing import billable_blocks
E   ModuleNotFoundError: No module named 'bookings'
=========================== short test summary info ============================
ERROR workspace/tests/test_bookings.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.10s ===============================

Exit code: 2
[Command failed with exit code 2]

### Tool call: execute
{"command": "PYTHONPATH=workspace python -m pytest workspace/tests"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/lab-asmlgvri
plugins: langsmith-0.14.4, anyio-4.15.1
collected 3 items

workspace/tests/test_bookings.py FF.                                     [100%]

=================================== FAILURES ===================================
_______________________ test_total_minutes_mixed_formats _______________________

    def test_total_minutes_mixed_formats():
>       assert total_minutes(["1h30m", "2h"]) == 210
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

/home284/284-home/VIN/lab20/K4-DAY20-MULTIAGENTS-TranNamAnh-2A202602901/tasks/code-eval/workspace/tests/test_bookings.py:6: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
workspace/bookings/schedule.py:7: in total_minutes
    return sum(parse_duration(d) for d in durations)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
workspace/bookings/schedule.py:7: in <genexpr>
    return sum(parse_duration(d) for d in durations)
               ^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

text = '2h'

    def parse_duration(text):
        """Convert a duration string to whole minutes (int).
    
        Supported formats:
          "1h30m" -> 90
          "2h"    -> 120
          "45m"   -> 45
          "1:30"  -> 90
          "45"    -> 45    # a bare number means minutes
        Surroundi

### Tool call: read_file
{"file_path": "workspace/tests/test_bookings.py"}

### Tool result
@@ lines 1-15 of 15 @@
from bookings.billing import billable_blocks
from bookings.schedule import add_slot, total_minutes


def test_total_minutes_mixed_formats():
    assert total_minutes(["1h30m", "2h"]) == 210


def test_billable_blocks_rounds_up():
    assert billable_blocks(20) == 2
    assert billable_blocks(45) == 3


def test_add_slot_single_call():
    assert add_slot("a") == ["a"]

### Tool call: read_file
{"file_path": "workspace/bookings/__init__.py"}

### Tool result
@@ lines 1-1 of 1 @@
__version__ = "1.4.2"

### Tool call: read_file
{"file_path": "workspace/bookings/billing.py"}

### Tool result
@@ lines 1-11 of 11 @@
"""Billing rules."""


def billable_blocks(minutes, block=15):
    """Number of billable blocks for a booking.

    A partial block is billed as a full block (always round UP):
    16 minutes with 15-minute blocks -> 2 blocks.
    `minutes` must be >= 0; a negative value raises ValueError.
    """
    return round(minutes / block)

### Tool call: read_file
{"file_path": "workspace/bookings/calendar_export.py"}

### Tool result
@@ lines 1-7 of 7 @@
"""Calendar export."""
from .timeutil import parse_duration


def slot_end(start_minute, duration_text):
    """Minute of the day at which a slot ends."""
    return start_minute + parse_duration(duration_text)

### Tool call: read_file
{"file_path": "workspace/bookings/schedule.py"}

### Tool result
@@ lines 1-17 of 17 @@
"""Schedule helpers."""
from .timeutil import parse_duration


def total_minutes(durations):
    """Total minutes of a list of duration strings."""
    return sum(parse_duration(d) for d in durations)


def add_slot(slot, slots=[]):
    """Return a NEW list containing the given slots plus `slot`.

    Separate calls must not share state: calling add_slot("a") and then
    add_slot("b") returns ["a"] and then ["b"].
    """
    slots.append(slot)
    return slots

### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py"}

### Tool result
@@ lines 1-19 of 19 @@
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))

### Tool call: task
{"description": "Review all files in workspace/bookings/ against their docstrings, requirements, potential edge cases, and ensure robustness and correctness. Do not modify tests/ or tests/test_bookings.py. Ensure every function does precisely what its docstring specifies.", "subagent_type": "reviewer"}

### Tool result
Review of the files in `workspace/bookings/` reveals multiple concrete issues, bugs, and discrepancies against their docstrings and requirements. 

Below are the findings per file with exact paths and evidence:

### 1. `workspace/bookings/billing.py`
* **Issue: Incorrect rounding / implementation for rounding up.**
  * **Docstring requirement:** 
    > A partial block is billed as a full block (always round UP):
    > 16 minutes with 15-minute blocks -> 2 blocks.
    > `minutes` must be >= 0; a negative value raises ValueError.
  * **Current implementation:** `return round(minutes / block)`
  * **Evidence & Failures:** `round()` in Python uses round-half-to-even. For example, `billable_blocks(20)` with block=15 evaluates `20 / 15 = 1.333...`, which `round()` rounds to `1` instead of rounding up to `2` (as tested by `test_billable_blocks_rounds_up` in `tests/test_bookings.py`). Furthermore, negative values are not checked to raise `ValueError` as specified in the docstring.

---

### 2. `workspace/bookings/timeutil.py`
* **Issue: Incomplete regex / parser supporting only a single format.**
  * **Docstring requirement:**
    > Supported formats:
    >   `"1h30m"` -> 90
    >   `"2h"`    -> 120
    >   `"45m"`   -> 45
    >   `"1:30"`  -> 90
    >   `"45"`    -> 45    # a bare number means minutes
    > Surrounding whitespace is ignored.
  * **Current implementation:** `m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())`
  * **Evidence & Failures:** The regex only matches strict `"

### Tool call: edit_file
{"old_string": "def billable_blocks(minutes, block=15):\n    \"\"\"Number of billable blocks for a booking.\n\n    A partial block is billed as a full block (always round UP):\n    16 minutes with 15-minute blocks -> 2 blocks.\n    `minutes` must be >= 0; a negative value raises ValueError.\n    \"\"\"\n    return round(minutes / block)", "file_path": "workspace/bookings/billing.py", "new_string": "def billable_blocks(minutes, block=15):\n    \"\"\"Number of billable blocks for a booking.\n\n    A partial block is billed as a full block (always round UP):\n    16 minutes with 15-minute blocks -> 2 blocks.\n    `minutes` must be >= 0; a negative value raises ValueError.\n    \"\"\"\n    if minutes < 0:\n        raise ValueError(\"minutes must be >= 0\")\n    if block <= 0:\n        raise ValueError(\"block must be > 0\")\n    return math.ceil(minutes / block)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/billing.py'

### Tool call: edit_file
{"new_string": "\"\"\"Billing rules.\"\"\"\nimport math\n\n\ndef billable_blocks(minutes, block=15):", "file_path": "workspace/bookings/billing.py", "old_string": "\"\"\"Billing rules.\"\"\"\n\n\ndef billable_blocks(minutes, block=15):"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/billing.py'

### Tool call: edit_file
{"old_string": "def add_slot(slot, slots=[]):\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    slots.append(slot)\n    return slots", "file_path": "workspace/bookings/schedule.py", "new_string": "def add_slot(slot, slots=None):\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    if slots is None:\n        slots = []\n    return list(slots) + [slot]"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/schedule.py'

### Tool call: edit_file
{"new_string": "def parse_duration(text):\n    \"\"\"Convert a duration string to whole minutes (int).\n\n    Supported formats:\n      \"1h30m\" -> 90\n      \"2h\"    -> 120\n      \"45m\"   -> 45\n      \"1:30\"  -> 90\n      \"45\"    -> 45    # a bare number means minutes\n    Surrounding whitespace is ignored.\n    \"\"\"\n    cleaned = text.strip()\n    if not cleaned:\n        raise ValueError(f\"bad duration: {text!r}\")\n\n    # Format \"1h30m\", \"2h\", \"45m\"\n    if 'h' in cleaned or 'm' in cleaned:\n        # Can be \"1h30m\", \"2h\", \"45m\"\n        m_hm = re.fullmatch(r\"(?:(\\d+)h)?(?:(\\d+)m)?\", cleaned)\n        # Check if match covers entire cleaned string and at least one group matched\n        if m_hm and m_hm.group(0) == cleaned and (m_hm.group(1) is not None or m_hm.group(2) is not None):\n            hours = int(m_hm.group(1)) if m_hm.group(1) is not None else 0\n            minutes = int(m_hm.group(2)) if m_hm.group(2) is not None else 0\n            return hours * 60 + minutes\n\n    # Format \"1:30\"\n    if ':' in cleaned:\n        parts = cleaned.split(':')\n        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():\n            return int(parts[0]) * 60 + int(parts[1])\n\n    # Format \"45\" (bare number)\n    if cleaned.isdigit():\n        return int(cleaned)\n\n    raise ValueError(f\"bad duration: {text!r}\")", "old_string": "def parse_duration(text):\n    \"\"\"Convert a duration string to whole minutes (int).\n\n    Suppor

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/timeutil.py'

### Tool call: execute
{"command": "PYTHONPATH=workspace python -m pytest workspace/tests"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/lab-asmlgvri
plugins: langsmith-0.14.4, anyio-4.15.1
collected 3 items

workspace/tests/test_bookings.py ...                                     [100%]

============================== 3 passed in 0.01s ===============================

[Command succeeded with exit code 0]

### Tool call: write_file
{"content": "from bookings.billing import billable_blocks\nfrom bookings.calendar_export import slot_end\nfrom bookings.schedule import add_slot, total_minutes\nfrom bookings.timeutil import parse_duration\nimport pytest\n\n\ndef test_parse_duration_all_formats():\n    assert parse_duration(\"1h30m\") == 90\n    assert parse_duration(\"2h\") == 120\n    assert parse_duration(\"45m\") == 45\n    assert parse_duration(\"1:30\") == 90\n    assert parse_duration(\"45\") == 45\n    assert parse_duration(\"  2h  \") == 120\n\n    with pytest.raises(ValueError):\n        parse_duration(\"abc\")\n    with pytest.raises(ValueError):\n        parse_duration(\"\")\n\n\ndef test_billable_blocks_edge_cases():\n    assert billable_blocks(0) == 0\n    assert billable_blocks(1) == 1\n    assert billable_blocks(15) == 1\n    assert billable_blocks(16) == 2\n    with pytest.raises(ValueError):\n        billable_blocks(-5)\n\n\ndef test_add_slot_no_state_sharing():\n    assert add_slot(\"a\") == [\"a\"]\n    assert add_slot(\"b\") == [\"b\"]\n    slots = [\"init\"]\n    assert add_slot(\"a\", slots) == [\"init\", \"a\"]\n    assert slots == [\"init\"]\n\n\ndef test_slot_end():\n    assert slot_end(600, \"1h30m\") == 690\n", "file_path": "workspace/tests/test_additional_bookings.py"}

### Tool result
Updated file /workspace/tests/test_additional_bookings.py

### Tool call: execute
{"command": "PYTHONPATH=workspace python -m pytest workspace/tests"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/lab-asmlgvri
plugins: langsmith-0.14.4, anyio-4.15.1
collected 7 items

workspace/tests/test_additional_bookings.py ....                         [ 57%]
workspace/tests/test_bookings.py ...                                     [100%]

============================== 7 passed in 0.02s ===============================

[Command succeeded with exit code 0]

### Tool call: delete
{"file_path": "workspace/tests/test_additional_bookings.py"}

### Tool result
Deleted /workspace/tests/test_additional_bookings.py

### Tool call: execute
{"command": "PYTHONPATH=workspace python -m pytest workspace/tests"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/lab-asmlgvri
plugins: langsmith-0.14.4, anyio-4.15.1
collected 3 items

workspace/tests/test_bookings.py ...                                     [100%]

============================== 3 passed in 0.01s ===============================

[Command succeeded with exit code 0]

### Tool call: execute
{"command": "git status"}

### Tool result
[stderr] fatal: not a git repository (or any of the parent directories): .git

Exit code: 128
[Command failed with exit code 128]

### Assistant
[{'type': 'text', 'text': 'I have successfully fixed the source code of the `bookings` package in `workspace/` so that all tests pass and every function adheres strictly to its docstring specification.\n\n### Summary of Changes:\n1. **`workspace/bookings/timeutil.py` (`parse_duration`)**:\n   - Expanded duration parsing logic to support all documented formats (`"1h30m"`, `"2h"`, `"45m"`, `"1:30"`, and bare numbers like `"45"` for minutes) as well as handling surrounding whitespace correctly and raising `ValueError` on invalid strings.\n2. **`workspace/bookings/billing.py` (`billable_blocks`)**:\n   - Replaced round-half-to-even `round()` with `math.ceil()` to correctly always round up partial blocks, and added validation to raise `ValueError` if negative minutes are provided.\n3. **`workspace/bookings/schedule.py` (`add_slot`)**:\n   - Replaced the mutable default argument (`slots=[]`) with `None` and ensured that calls return a new list without sharing state across invocations.', 'extras': {'signature': 'El4KXAFpFH0TdeNQU1dtpbo5vMV3x7o7c9OFRz1eXa6AtCW4NbZIWm1UREXFFZUeokh2i37YEwmK68qeexATyfhRUYWoX72HGpQ91dk4BnTV9Ts4m/MdDP87Jn50kTI/'}}]