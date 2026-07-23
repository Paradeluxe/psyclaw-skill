"""Windows IME guard — force US-English layout during live keyboard runs.

CJK IMEs (Microsoft Pinyin etc.) show candidate windows that swallow
key events and break RT / single-key responses. Live Start/Pilot runs
switch the active keyboard layout to en-US (00000409) and restore the
previous layout when the run ends.

No-op on non-Windows. Safe to call repeatedly.
"""
from __future__ import annotations

import sys
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


EN_US_KLID = "00000409"
EN_US_TIP = "0409:00000409"

_lock = threading.Lock()
_depth = 0
_saved: Optional["ImeToken"] = None


@dataclass
class ImeToken:
    prev_hkl: int = 0
    forced_hkl: int = 0
    prev_override: Optional[str] = None
    ok: bool = False
    detail: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)


def is_windows() -> bool:
    return sys.platform == "win32"


def force_english(*, also_default: bool = False) -> ImeToken:
    """Activate en-US layout. Nested calls keep a single restore target.

    also_default: also Set-WinDefaultInputMethodOverride to en-US so *new*
    windows inherit English (restored on matching restore()).
    """
    global _depth, _saved
    if not is_windows():
        return ImeToken(detail="not windows")

    with _lock:
        if _depth > 0 and _saved is not None:
            _depth += 1
            return ImeToken(
                prev_hkl=_saved.prev_hkl,
                forced_hkl=_saved.forced_hkl,
                prev_override=_saved.prev_override,
                ok=_saved.ok,
                detail=f"nested depth={_depth}",
            )
        token = _force_english_impl(also_default=also_default)
        if token.ok:
            _saved = token
            _depth = 1
        return token


def restore(token: Optional[ImeToken] = None) -> None:
    """Restore previous layout. Pair with force_english()."""
    global _depth, _saved
    if not is_windows():
        return
    with _lock:
        if _depth <= 0:
            if token and token.ok:
                _restore_impl(token)
            return
        _depth -= 1
        if _depth > 0:
            return
        t = _saved or token
        _saved = None
        if t and t.ok:
            _restore_impl(t)


def _force_english_impl(*, also_default: bool) -> ImeToken:
    try:
        import ctypes
        from ctypes import wintypes
    except Exception as exc:  # noqa: BLE001
        return ImeToken(detail=f"ctypes: {exc!r}")

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.GetKeyboardLayout.argtypes = [wintypes.DWORD]
    user32.GetKeyboardLayout.restype = wintypes.HKL
    user32.LoadKeyboardLayoutW.argtypes = [wintypes.LPCWSTR, wintypes.UINT]
    user32.LoadKeyboardLayoutW.restype = wintypes.HKL
    user32.ActivateKeyboardLayout.argtypes = [wintypes.HKL, wintypes.UINT]
    user32.ActivateKeyboardLayout.restype = wintypes.HKL
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.PostMessageW.argtypes = [
        wintypes.HWND,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM,
    ]
    user32.PostMessageW.restype = wintypes.BOOL

    prev = int(user32.GetKeyboardLayout(0) or 0)
    # KLF_ACTIVATE = 1
    hkl = user32.LoadKeyboardLayoutW(EN_US_KLID, 1)
    if not hkl:
        return ImeToken(prev_hkl=prev, detail="LoadKeyboardLayout failed")

    user32.ActivateKeyboardLayout(hkl, 0)
    hwnd = user32.GetForegroundWindow()
    if hwnd:
        # WM_INPUTLANGCHANGEREQUEST = 0x0050
        user32.PostMessageW(hwnd, 0x0050, 0, hkl)

    prev_override = None
    if also_default:
        prev_override = _get_default_override()
        _set_default_override(EN_US_TIP)

    return ImeToken(
        prev_hkl=prev,
        forced_hkl=int(hkl),
        prev_override=prev_override,
        ok=True,
        detail="en-US",
    )


def _restore_impl(token: ImeToken) -> None:
    try:
        import ctypes
        from ctypes import wintypes
    except Exception:
        return

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.ActivateKeyboardLayout.argtypes = [wintypes.HKL, wintypes.UINT]
    user32.ActivateKeyboardLayout.restype = wintypes.HKL
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.PostMessageW.argtypes = [
        wintypes.HWND,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM,
    ]
    user32.PostMessageW.restype = wintypes.BOOL

    if token.prev_hkl:
        hkl = wintypes.HKL(token.prev_hkl & 0xFFFFFFFFFFFFFFFF)
        try:
            user32.ActivateKeyboardLayout(hkl, 0)
        except Exception:
            pass
        hwnd = user32.GetForegroundWindow()
        if hwnd:
            try:
                user32.PostMessageW(hwnd, 0x0050, 0, hkl)
            except Exception:
                pass

    if token.prev_override is not None:
        # empty string means clear override back to language list order
        _set_default_override(token.prev_override or "")


def _get_default_override() -> Optional[str]:
    try:
        import subprocess

        ps = (
            "$o = Get-WinDefaultInputMethodOverride; "
            "if ($null -eq $o) { '' } else { [string]$o.InputMethodTip }"
        )
        r = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                ps,
            ],
            capture_output=True,
            text=True,
            timeout=8,
            creationflags=getattr(__import__("subprocess"), "CREATE_NO_WINDOW", 0),
        )
        if r.returncode != 0:
            return None
        return (r.stdout or "").strip()
    except Exception:
        return None


def _set_default_override(tip: str) -> bool:
    """Set or clear WinDefaultInputMethodOverride. tip='' clears."""
    try:
        import subprocess

        if tip:
            # escape single quotes for PowerShell
            safe = tip.replace("'", "''")
            cmd = f"Set-WinDefaultInputMethodOverride -InputTip '{safe}'"
        else:
            cmd = "Set-WinDefaultInputMethodOverride -InputTip $null"
        r = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                cmd,
            ],
            capture_output=True,
            text=True,
            timeout=8,
            creationflags=getattr(__import__("subprocess"), "CREATE_NO_WINDOW", 0),
        )
        return r.returncode == 0
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Snippet inlined into generated experiment.py (PsychoPy child process).
# Must stay pure stdlib + ctypes — no backend imports.
# ---------------------------------------------------------------------------

EXPERIMENT_IME_HELPERS = r'''
def _psyclaw_force_en_ime(win=None):
    """Switch this process to en-US layout (no CJK candidate UI)."""
    import sys as _sys
    if _sys.platform != "win32":
        return None
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.GetKeyboardLayout.argtypes = [wintypes.DWORD]
        user32.GetKeyboardLayout.restype = wintypes.HKL
        user32.LoadKeyboardLayoutW.argtypes = [wintypes.LPCWSTR, wintypes.UINT]
        user32.LoadKeyboardLayoutW.restype = wintypes.HKL
        user32.ActivateKeyboardLayout.argtypes = [wintypes.HKL, wintypes.UINT]
        user32.ActivateKeyboardLayout.restype = wintypes.HKL
        user32.GetForegroundWindow.restype = wintypes.HWND
        user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        user32.PostMessageW.restype = wintypes.BOOL

        prev = int(user32.GetKeyboardLayout(0) or 0)
        hkl = user32.LoadKeyboardLayoutW("00000409", 1)
        if not hkl:
            return None
        user32.ActivateKeyboardLayout(hkl, 0)

        hwnds = []
        fg = user32.GetForegroundWindow()
        if fg:
            hwnds.append(fg)
        # PsychoPy / pyglet / glfw window handle if present
        if win is not None:
            try:
                wh = getattr(win, "winHandle", None)
                for attr in ("_hwnd", "hwnd", "_hWnd"):
                    h = getattr(wh, attr, None) if wh is not None else None
                    if h:
                        hwnds.append(int(h))
                if wh is not None and hasattr(wh, "get_handle"):
                    try:
                        hwnds.append(int(wh.get_handle()))
                    except Exception:
                        pass
            except Exception:
                pass
        seen = set()
        for h in hwnds:
            if not h or h in seen:
                continue
            seen.add(h)
            try:
                user32.PostMessageW(wintypes.HWND(h), 0x0050, 0, hkl)
            except Exception:
                pass
        return {"prev": prev, "hkl": int(hkl)}
    except Exception as _e:
        print("[psyclaw] WARN IME force: " + repr(_e), flush=True)
        return None


def _psyclaw_restore_ime(state):
    if not state:
        return
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.ActivateKeyboardLayout.argtypes = [wintypes.HKL, wintypes.UINT]
        user32.ActivateKeyboardLayout.restype = wintypes.HKL
        user32.GetForegroundWindow.restype = wintypes.HWND
        user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        user32.PostMessageW.restype = wintypes.BOOL
        prev = int(state.get("prev") or 0)
        if not prev:
            return
        hkl = wintypes.HKL(prev & 0xFFFFFFFFFFFFFFFF)
        user32.ActivateKeyboardLayout(hkl, 0)
        fg = user32.GetForegroundWindow()
        if fg:
            user32.PostMessageW(fg, 0x0050, 0, hkl)
    except Exception as _e:
        print("[psyclaw] WARN IME restore: " + repr(_e), flush=True)


def _psyclaw_assert_en_ime():
    """Re-assert en-US (user may have Alt+Shift mid-run)."""
    try:
        import sys as _sys
        if _sys.platform != "win32":
            return
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.GetKeyboardLayout.argtypes = [wintypes.DWORD]
        user32.GetKeyboardLayout.restype = wintypes.HKL
        user32.LoadKeyboardLayoutW.argtypes = [wintypes.LPCWSTR, wintypes.UINT]
        user32.LoadKeyboardLayoutW.restype = wintypes.HKL
        user32.ActivateKeyboardLayout.argtypes = [wintypes.HKL, wintypes.UINT]
        user32.ActivateKeyboardLayout.restype = wintypes.HKL
        cur = int(user32.GetKeyboardLayout(0) or 0)
        # low word = lang id; 0x0409 = en-US
        if (cur & 0xFFFF) == 0x0409:
            return
        hkl = user32.LoadKeyboardLayoutW("00000409", 1)
        if hkl:
            user32.ActivateKeyboardLayout(hkl, 0)
    except Exception:
        pass
'''
