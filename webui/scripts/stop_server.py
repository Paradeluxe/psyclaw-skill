#!/usr/bin/env python3
"""Stop psyclaw-webui on PSYCLAW_PORT (default 8876). Bounded; never hangs."""
from __future__ import annotations

import os
import subprocess
import sys
import time


def _port() -> int:
    try:
        return int(os.environ.get("PSYCLAW_PORT", "8876"))
    except ValueError:
        return 8876


def _pids_on_port_windows(port: int) -> list[int]:
    pids: set[int] = set()
    try:
        proc = subprocess.run(
            ["netstat", "-ano", "-p", "tcp"],
            capture_output=True,
            text=True,
            timeout=5,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    suffix = f":{port}"
    for line in (proc.stdout or "").splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        # TCP  local  foreign  STATE  PID
        state = parts[3].upper() if not parts[3].isdigit() else parts[2].upper()
        # netstat columns: Proto Local Foreign State PID  (5 fields) 
        # sometimes State is parts[3]
        if "LISTENING" not in line.upper():
            continue
        local = parts[1]
        if not (local.endswith(suffix) or local.endswith("]" + suffix)):
            continue
        try:
            pids.add(int(parts[-1]))
        except ValueError:
            continue
    return sorted(pids)


def _pids_on_port_posix(port: int) -> list[int]:
    pids: set[int] = set()
    for cmd in (
        ["lsof", f"-tiTCP:{port}", "-sTCP:LISTEN"],
        ["fuser", f"{port}/tcp"],
    ):
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            continue
        out = (proc.stdout or "") + " " + (proc.stderr or "")
        for tok in out.replace("\n", " ").split():
            tok = tok.strip().rstrip(":")
            if tok.isdigit():
                pids.add(int(tok))
        if pids:
            break
    return sorted(pids)


def _kill_pid(pid: int) -> str:
    if pid <= 0:
        return "skip"
    if sys.platform == "win32":
        try:
            proc = subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True,
                text=True,
                timeout=8,
                encoding="utf-8",
                errors="replace",
            )
            if proc.returncode == 0:
                return "killed"
            err = (proc.stderr or proc.stdout or "").strip()
            return err or f"exit {proc.returncode}"
        except subprocess.TimeoutExpired:
            return "timeout"
        except OSError as exc:
            return str(exc)
    try:
        os.kill(pid, 15)
    except OSError:
        pass
    time.sleep(0.3)
    try:
        os.kill(pid, 9)
    except OSError:
        pass
    return "killed"


def _extra_psyclaw_pids_windows() -> list[int]:
    ps = r"""
$ids = @()
Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match 'python' -and $_.CommandLine } |
  ForEach-Object {
    $c = $_.CommandLine
    if ($c -match 'psyclaw-webui' -or $c -match 'backend\\app\.py' -or $c -match 'backend/app\.py' -or ($c -match 'start\.py' -and $c -match 'psyclaw')) {
      $ids += $_.ProcessId
    }
  }
$ids -join "`n"
"""
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
            capture_output=True,
            text=True,
            timeout=10,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    out: list[int] = []
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if line.isdigit():
            out.append(int(line))
    return out


def stop(*, verbose: bool = True) -> int:
    port = _port()
    if sys.platform == "win32":
        pids = set(_pids_on_port_windows(port)) | set(_extra_psyclaw_pids_windows())
    else:
        pids = set(_pids_on_port_posix(port))

    # never kill ourselves
    pids.discard(os.getpid())

    if not pids:
        if verbose:
            print(f"psyclaw-webui: nothing to stop on port {port}")
        return 0

    if verbose:
        print(f"psyclaw-webui: stopping PIDs {sorted(pids)} (port {port})")
    for pid in sorted(pids):
        result = _kill_pid(pid)
        if verbose:
            print(f"  pid {pid}: {result}")

    deadline = time.time() + 4.0
    while time.time() < deadline:
        left = (
            _pids_on_port_windows(port)
            if sys.platform == "win32"
            else _pids_on_port_posix(port)
        )
        if not left:
            if verbose:
                print("psyclaw-webui: stopped")
            return 0
        # re-kill stragglers once
        for pid in left:
            _kill_pid(pid)
        time.sleep(0.3)

    left = (
        _pids_on_port_windows(port)
        if sys.platform == "win32"
        else _pids_on_port_posix(port)
    )
    if left:
        if verbose:
            print(
                f"psyclaw-webui: still listening after stop: PIDs {left}. "
                f"End them in Task Manager or: taskkill /PID {left[0]} /F",
                file=sys.stderr,
            )
        return 1
    if verbose:
        print("psyclaw-webui: stopped")
    return 0


def main() -> int:
    return stop(verbose=True)


if __name__ == "__main__":
    sys.exit(main())
