"""PsychoPy process runner — subprocess against resolved PsychoPy Python.

Compiles the paradigm spec to a .py under runs/<id>/, launches PsychoPy's
Python with a clean PYTHONPATH, streams stdout into log.txt, and copies the
trial CSV into runs/<id>/data/trials.csv when the process exits.

Interpreter: PSYCLAW_PSYCHOPY_PYTHON or probed paths (see psychopy_env).
"""
from __future__ import annotations

import os
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .process import BaseProcess

try:
    from psychopy_env import psychopy_python
except ImportError:  # package-style import when backend is on path as package
    from backend.psychopy_env import psychopy_python  # type: ignore


def _psychopy_python() -> str:
    return psychopy_python()


# Resolved at use-time so env changes apply without reimport surprises.
PSYCHOPY_PYTHON = _psychopy_python()


class PsychoPyProcess(BaseProcess):
    """Spawn a real PsychoPy experiment as a subprocess.

    Parameters
    ----------
    paradigm_id : str
        Used by the compiler to pick the right template.
    headless : bool
        If True (default), pass --headless so the script auto-responds and
        doesn't block the server waiting for keypresses.
    """

    def __init__(
        self,
        run_id: str,
        run_dir: str,
        spec: Dict[str, Any],
        paradigm_id: str = "stroop",
        headless: bool = True,
        design: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(run_id, run_dir, spec)
        self.paradigm_id = paradigm_id
        self.headless = headless
        self.design = design
        self._log_path = os.path.join(run_dir, "log.txt")
        self._script_path = os.path.join(run_dir, "experiment.py")
        self._proc: Optional[subprocess.Popen] = None

    def start(self) -> None:
        os.makedirs(os.path.join(self.run_dir, "data"), exist_ok=True)
        self._compile_script()
        self._thread = threading.Thread(
            target=self._run, name=f"PsychoPyProcess-{self.run_id}", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        super().stop()
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.terminate()
            except OSError:
                pass

    def _write_log(self, line: str) -> None:
        with open(self._log_path, "a", encoding="utf-8") as fh:
            fh.write(line.rstrip("\n") + "\n")

    def _compile_script(self) -> None:
        import sys
        backend_dir = str(Path(__file__).resolve().parent.parent)
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        from design_compiler import compile_any

        session = None
        if isinstance(self.spec, dict):
            if isinstance(self.spec.get("session"), dict):
                session = self.spec.get("session")
            else:
                session = {
                    "participant_id": self.spec.get("participant_id") or "P01",
                    "session": self.spec.get("session_id") or "1",
                    "date": self.spec.get("date") or "",
                    "experimenter": self.spec.get("experimenter") or "",
                    "notes": self.spec.get("notes") or "",
                }
        source = compile_any(
            paradigm_id=self.paradigm_id,
            spec=self.spec,
            design=self.design,
            session=session,
        )
        with open(self._script_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(source)
        tag = "design" if self.design else self.paradigm_id
        self._write_log(f"[psychopy] compiled {tag} -> {self._script_path}")

    def _run(self) -> None:
        py = _psychopy_python()
        if not os.path.isfile(py):
            self._write_log(f"[psychopy] ERROR: python not found at {py}")
            self.returncode = 127
            return

        env = os.environ.copy()
        # Critical: strip hermes venv pollution that breaks PsychoPy numpy/crypto.
        env["PYTHONPATH"] = ""
        env["PYTHONHOME"] = ""
        env["PSYCLAW_HEADLESS"] = "1" if self.headless else "0"
        # Live runs default to force en-US IME inside generated script
        if not self.headless:
            force_ime = True
            if isinstance(self.spec, dict):
                sess = self.spec.get("session") if isinstance(self.spec.get("session"), dict) else {}
                raw = sess.get("force_en_ime", self.spec.get("force_en_ime", True))
                force_ime = str(raw).strip().lower() not in ("0", "false", "no", "off", "")
            env["PSYCLAW_FORCE_EN_IME"] = "1" if force_ime else "0"
        else:
            env["PSYCLAW_FORCE_EN_IME"] = "0"

        cmd: List[str] = [py, self._script_path]
        if self.headless:
            cmd.append("--headless")

        self._write_log(f"[psychopy] start: {' '.join(cmd)}")
        try:
            self._proc = subprocess.Popen(
                cmd,
                cwd=self.run_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except OSError as exc:
            self._write_log(f"[psychopy] spawn failed: {exc!r}")
            self.returncode = 126
            return

        assert self._proc.stdout is not None
        for line in self._proc.stdout:
            if self._stop_event.is_set():
                try:
                    self._proc.terminate()
                except OSError:
                    pass
                break
            self._write_log(line.rstrip("\n"))

        # Drain remaining output after terminate
        try:
            self._proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self._proc.kill()
            self._proc.wait(timeout=5)

        if self._stop_event.is_set():
            self.returncode = 130
            self._write_log("[psychopy] stopped by user")
        else:
            self.returncode = self._proc.returncode if self._proc.returncode is not None else -1
            self._write_log(f"[psychopy] exit code={self.returncode}")

        self._harvest_csv()

    def _harvest_csv(self) -> None:
        """Copy the newest CSV from data/ to data/trials.csv for the API.

        Also mirror into <project_path>/data/ (PsychoPy-desktop style) when
        the run carried a project folder.
        """
        data_dir = Path(self.run_dir) / "data"
        if not data_dir.is_dir():
            return
        csvs = sorted(data_dir.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not csvs:
            self._write_log("[psychopy] no CSV produced")
            return
        target = data_dir / "trials.csv"
        # Prefer participant-named file over the trials.csv alias
        named = [c for c in csvs if c.name.lower() != "trials.csv"]
        src = named[0] if named else csvs[0]
        if src.resolve() != target.resolve():
            shutil.copy2(src, target)
        self._write_log(f"[psychopy] harvested {src.name} -> trials.csv")

        proj = ""
        if isinstance(self.spec, dict):
            proj = str(self.spec.get("project_path") or "").strip()
            if not proj and isinstance(self.spec.get("session"), dict):
                proj = str(self.spec["session"].get("project_path") or "").strip()
        if not proj:
            return
        try:
            dest_dir = Path(proj) / "data"
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / src.name
            if src.resolve() != dest.resolve():
                shutil.copy2(src, dest)
            self._write_log(f"[psychopy] mirrored {src.name} -> {dest}")
        except Exception as exc:  # noqa: BLE001
            self._write_log(f"[psychopy] project data mirror failed: {exc!r}")
