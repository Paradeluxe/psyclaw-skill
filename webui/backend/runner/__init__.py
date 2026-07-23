"""Runner subsystem: state machine + process management.

Public surface:
    - ``state.RunState``              — enum of valid states
    - ``state.StateMachine``          — per-run state machine
    - ``state.ALLOWED_TRANSITIONS``   — for inspection
    - ``process.MockProcess``         — stub implementation
    - ``process.BaseProcess``         — interface
    - ``psychopy_process.PsychoPyProcess`` — real PsychoPy subprocess
"""
from .state import RunState, StateMachine, ALLOWED_TRANSITIONS  # noqa: F401
from .process import BaseProcess, MockProcess  # noqa: F401
from .psychopy_process import PsychoPyProcess  # noqa: F401
