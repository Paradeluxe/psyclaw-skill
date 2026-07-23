"""Native OS folder picker for local mission-control UI.

Browser cannot expose real absolute paths; this host-side dialog can.

Windows strategy (in order):
  1. Modern IFileOpenDialog + FOS_PICKFOLDERS (large Explorer-style picker)
  2. WinForms FolderBrowserDialog with topmost owner (legacy small tree)
  3. Shell.Application BrowseForFolder (legacy)
  4. tkinter askdirectory

Result is written to a temp file (not stdout). Cancel stops the chain.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, Optional, Tuple


def _run_ps_script(ps_body: str, label: str) -> Tuple[str, Optional[str]]:
    """Run STA PowerShell; script writes OK|path / CANCEL / FAIL|msg to a result file."""
    tmp_ps = None
    tmp_out = None
    try:
        fd, tmp_out = tempfile.mkstemp(prefix="psyclaw_pick_out_", suffix=".txt")
        os.close(fd)
        with open(tmp_out, "w", encoding="utf-8") as f:
            f.write("")

        out_esc = tmp_out.replace("'", "''")
        full = f"""
$ErrorActionPreference = 'Stop'
$outFile = '{out_esc}'
function Write-Result([string]$line) {{
  [System.IO.File]::WriteAllText($outFile, $line, [System.Text.UTF8Encoding]::new($false))
}}
try {{
{ps_body}
}} catch {{
  Write-Result ('FAIL|' + $_.Exception.Message)
}}
"""
        fd2, tmp_ps = tempfile.mkstemp(prefix="psyclaw_pick_", suffix=".ps1")
        os.close(fd2)
        with open(tmp_ps, "w", encoding="utf-8-sig", newline="\n") as f:
            f.write(full)

        proc = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-STA",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                tmp_ps,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )

        for _ in range(20):
            try:
                with open(tmp_out, "r", encoding="utf-8") as f:
                    raw = f.read().strip()
                if raw:
                    break
            except OSError:
                raw = ""
            time.sleep(0.05)
        else:
            raw = ""

        if not raw:
            err = (proc.stderr or "").strip() or (proc.stdout or "").strip() or f"exit {proc.returncode}"
            if proc.returncode not in (0,):
                return "cancelled", None
            return "fail", f"{label} empty: {err}"

        if raw == "CANCEL" or raw.startswith("CANCEL"):
            return "cancelled", None
        if raw.startswith("FAIL|"):
            return "fail", f"{label}: {raw[5:]}"
        if raw.startswith("OK|"):
            path = raw[3:].strip()
            if path:
                return "ok", path
            return "cancelled", None
        if os.path.isdir(raw):
            return "ok", raw
        return "fail", f"{label} unexpected: {raw!r}"
    except subprocess.TimeoutExpired:
        return "fail", f"{label} timeout"
    except OSError as exc:
        return "fail", f"{label} launch failed: {exc!r}"
    finally:
        for p in (tmp_ps, tmp_out):
            if p:
                try:
                    os.unlink(p)
                except OSError:
                    pass


def _pick_modern_explorer(title: str, initialdir: Optional[str]) -> Tuple[str, Optional[str]]:
    """Large Vista+ Explorer-style folder picker (IFileOpenDialog FOS_PICKFOLDERS)."""
    if sys.platform != "win32":
        return "fail", "not windows"
    desc = (title or "Select folder").replace("'", "''")
    if initialdir and os.path.isdir(initialdir):
        init_block = f"$initial = '{initialdir.replace(chr(39), chr(39)+chr(39))}'"
    else:
        init_block = "$initial = $null"

    # External csharp file approach avoided — single PS script with Add-Type.
    # Use reflection-based OpenFileDialog folder hack is unreliable.
    # Prefer COM via dynamic assembly loaded from here-string.
    body = f"""
  {init_block}
  $title = '{desc}'
  # Prefer WindowsAPICodePack-free COM via Microsoft.WindowsAPICodePack is not required.
  # Use FolderBrowserDialog is small; use OpenFileDialog with FOS_PICKFOLDERS via C#.
  $cs = @'
using System;
using System.Runtime.InteropServices;
public static class PsyClawFolderPick {{
  [ComImport, Guid("DC1C5A9C-E88A-4DDE-A5A1-60F82A20AEF7")]
  private class FileOpenDialogRCW {{}}
  [ComImport, Guid("42F85136-DB7E-439C-85F1-E4075D135FC8"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  private interface IFileDialog {{
    [PreserveSig] int Show(IntPtr parent);
    void SetFileTypes(uint cFileTypes, IntPtr rgFilterSpec);
    void SetFileTypeIndex(uint iFileType);
    void GetFileTypeIndex(out uint piFileType);
    void Advise(IntPtr pfde, out uint pdwCookie);
    void Unadvise(uint dwCookie);
    void SetOptions(uint fos);
    void GetOptions(out uint pfos);
    void SetDefaultFolder(IShellItem psi);
    void SetFolder(IShellItem psi);
    void GetFolder(out IShellItem ppsi);
    void GetCurrentSelection(out IShellItem ppsi);
    void SetFileName([MarshalAs(UnmanagedType.LPWStr)] string pszName);
    void GetFileName(out IntPtr pszName);
    void SetTitle([MarshalAs(UnmanagedType.LPWStr)] string pszTitle);
    void SetOkButtonLabel([MarshalAs(UnmanagedType.LPWStr)] string pszText);
    void SetFileNameLabel([MarshalAs(UnmanagedType.LPWStr)] string pszLabel);
    void GetResult(out IShellItem ppsi);
    void AddPlace(IShellItem psi, int fdap);
    void SetDefaultExtension([MarshalAs(UnmanagedType.LPWStr)] string pszDefaultExtension);
    void Close(int hr);
    void SetClientGuid(ref Guid guid);
    void ClearClientData();
    void SetFilter(IntPtr pFilter);
  }}
  [ComImport, Guid("43826D1E-E718-42EE-BC55-A1E261C37BFE"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  private interface IShellItem {{
    void BindToHandler(IntPtr pbc, ref Guid bhid, ref Guid riid, out IntPtr ppv);
    void GetParent(out IShellItem ppsi);
    void GetDisplayName(uint sigdnName, out IntPtr ppszName);
    void GetAttributes(uint sfgaoMask, out uint psfgaoAttribs);
    void Compare(IShellItem psi, uint hint, out int piOrder);
  }}
  [DllImport("shell32.dll", CharSet=CharSet.Unicode, PreserveSig=false)]
  private static extern void SHCreateItemFromParsingName(
    [MarshalAs(UnmanagedType.LPWStr)] string pszPath, IntPtr pbc, ref Guid riid, out IShellItem ppv);
  private const uint FOS_PICKFOLDERS = 0x20;
  private const uint FOS_FORCEFILESYSTEM = 0x40;
  private const uint FOS_PATHMUSTEXIST = 0x800;
  private const uint SIGDN_FILESYSPATH = 0x80058000;
  public static string Pick(string title, string initialDir, IntPtr owner) {{
    var dlg = (IFileDialog)new FileOpenDialogRCW();
    dlg.SetTitle(string.IsNullOrEmpty(title) ? "Select folder" : title);
    uint opt; dlg.GetOptions(out opt);
    dlg.SetOptions(opt | FOS_PICKFOLDERS | FOS_FORCEFILESYSTEM | FOS_PATHMUSTEXIST);
    if (!string.IsNullOrEmpty(initialDir) && System.IO.Directory.Exists(initialDir)) {{
      try {{
        Guid iid = new Guid("43826D1E-E718-42EE-BC55-A1E261C37BFE");
        IShellItem item; SHCreateItemFromParsingName(initialDir, IntPtr.Zero, ref iid, out item);
        dlg.SetFolder(item);
      }} catch {{ }}
    }}
    int hr = dlg.Show(owner == IntPtr.Zero ? IntPtr.Zero : owner);
    if (hr != 0) return null;
    IShellItem result; dlg.GetResult(out result);
    IntPtr psz; result.GetDisplayName(SIGDN_FILESYSPATH, out psz);
    string path = Marshal.PtrToStringUni(psz);
    Marshal.FreeCoTaskMem(psz);
    return path;
  }}
}}
'@
  $typeName = 'PsyClawFolderPick'
  # Force recompile if signature changed across agent reloads
  if (-not ([System.Management.Automation.PSTypeName]$typeName).Type) {{
    Add-Type -TypeDefinition $cs -Language CSharp
  }}
  # TopMost owner so the large Explorer dialog is not stuck behind the browser.
  Add-Type -AssemblyName System.Windows.Forms | Out-Null
  Add-Type -AssemblyName System.Drawing | Out-Null
  $owner = New-Object System.Windows.Forms.Form
  $owner.Text = 'psyclaw'
  $owner.TopMost = $true
  $owner.ShowInTaskbar = $true
  $owner.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::FixedToolWindow
  $owner.Opacity = 0.05
  $owner.Size = New-Object System.Drawing.Size(12, 12)
  $owner.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen
  $owner.Show()
  $owner.Activate()
  $owner.BringToFront()
  try {{
    $path = [PsyClawFolderPick]::Pick($title, $initial, $owner.Handle)
    if ([string]::IsNullOrWhiteSpace($path)) {{ Write-Result 'CANCEL' }}
    elseif ($path.StartsWith('HR:')) {{ Write-Result 'CANCEL' }}
    else {{ Write-Result ('OK|' + $path) }}
  }} finally {{
    $owner.Close()
    $owner.Dispose()
  }}
"""
    return _run_ps_script(body, "modern.explorer")


def _pick_shell_browse(title: str, initialdir: Optional[str]) -> Tuple[str, Optional[str]]:
    if sys.platform != "win32":
        return "fail", "not windows"
    desc = (title or "Select folder").replace("'", "''")
    if initialdir and os.path.isdir(initialdir):
        root = "'" + initialdir.replace("'", "''") + "'"
    else:
        root = "17"
    body = f"""
  Add-Type -AssemblyName System.Windows.Forms
  Add-Type -AssemblyName System.Drawing
  $owner = New-Object System.Windows.Forms.Form
  $owner.TopMost = $true
  $owner.ShowInTaskbar = $false
  $owner.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::None
  $owner.Opacity = 0.01
  $owner.Size = New-Object System.Drawing.Size(1,1)
  $owner.StartPosition = [System.Windows.Forms.FormStartPosition]::Manual
  $owner.Location = New-Object System.Drawing.Point(120, 120)
  $owner.Show(); $owner.Activate(); $owner.BringToFront()
  $hwnd = $owner.Handle.ToInt32()
  try {{
    $shell = New-Object -ComObject Shell.Application
    $folder = $shell.BrowseForFolder($hwnd, '{desc}', 0x51, {root})
    if ($null -eq $folder) {{ Write-Result 'CANCEL' }}
    else {{
      $p = $folder.Self.Path
      if ([string]::IsNullOrWhiteSpace($p)) {{ Write-Result 'CANCEL' }}
      else {{ Write-Result ('OK|' + $p) }}
    }}
  }} finally {{ $owner.Close(); $owner.Dispose() }}
"""
    return _run_ps_script(body, "shell.browse")


def _pick_winforms(title: str, initialdir: Optional[str]) -> Tuple[str, Optional[str]]:
    if sys.platform != "win32":
        return "fail", "not windows"
    desc = (title or "Select folder").replace("'", "''")
    init_block = ""
    if initialdir and os.path.isdir(initialdir):
        init_esc = initialdir.replace("'", "''")
        init_block = f"$f.SelectedPath = '{init_esc}'; "
    body = f"""
  Add-Type -AssemblyName System.Windows.Forms
  Add-Type -AssemblyName System.Drawing
  [System.Windows.Forms.Application]::EnableVisualStyles()
  $f = New-Object System.Windows.Forms.FolderBrowserDialog
  $f.Description = '{desc}'
  $f.ShowNewFolderButton = $true
  {init_block}
  $owner = New-Object System.Windows.Forms.Form
  $owner.TopMost = $true
  $owner.ShowInTaskbar = $false
  $owner.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::None
  $owner.Opacity = 0.01
  $owner.Size = New-Object System.Drawing.Size(1,1)
  $owner.StartPosition = [System.Windows.Forms.FormStartPosition]::Manual
  $owner.Location = New-Object System.Drawing.Point(200,200)
  $owner.Show(); $owner.Activate(); $owner.BringToFront()
  $r = $f.ShowDialog($owner)
  $owner.Close(); $owner.Dispose()
  if ($r -eq [System.Windows.Forms.DialogResult]::OK -and $f.SelectedPath) {{
    Write-Result ('OK|' + $f.SelectedPath)
  }} else {{ Write-Result 'CANCEL' }}
"""
    return _run_ps_script(body, "winforms")


def _pick_tk(title: str, initialdir: Optional[str]) -> Tuple[str, Optional[str]]:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception as exc:  # noqa: BLE001
        return "fail", f"tkinter unavailable: {exc!r}"
    root = None
    try:
        root = tk.Tk()
        root.withdraw()
        try:
            root.attributes("-topmost", True)
            root.lift()
            root.focus_force()
            root.update_idletasks()
            root.update()
        except Exception:
            pass
        kwargs: Dict[str, Any] = {"title": title or "Select folder", "mustexist": True}
        if initialdir and os.path.isdir(initialdir):
            kwargs["initialdir"] = initialdir
        path = filedialog.askdirectory(**kwargs)
        if path:
            return "ok", path
        return "cancelled", None
    except Exception as exc:  # noqa: BLE001
        return "fail", f"tkinter dialog error: {exc!r}"
    finally:
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass


def pick_folder(
    title: str = "Select folder",
    initialdir: Optional[str] = None,
) -> Dict[str, Any]:
    """Open a blocking native folder dialog. Returns {ok, path?, cancelled?, error?, backend?}."""
    if sys.platform == "win32":
        backends = [
            ("modern.explorer", _pick_modern_explorer),
            ("winforms", _pick_winforms),
            ("shell.browse", _pick_shell_browse),
            ("tkinter", _pick_tk),
        ]
    else:
        backends = [("tkinter", _pick_tk)]

    errors = []
    for name, fn in backends:
        status, payload = fn(title, initialdir)
        if status == "ok" and payload:
            path = os.path.abspath(os.path.expanduser(payload))
            return {"ok": True, "cancelled": False, "path": path, "backend": name}
        if status == "cancelled":
            return {"ok": True, "cancelled": True, "path": None, "backend": name}
        errors.append(f"{name}: {payload or 'fail'}")

    return {
        "ok": False,
        "cancelled": False,
        "path": None,
        "error": "; ".join(errors) or "no folder dialog backend available",
    }


def reveal_folder(path: str) -> Dict[str, Any]:
    """Open a folder in the OS file manager and try to raise it in front of the browser.

    Windows: ONE open at most. Reuse existing Explorer window for the same path
    when possible (Shell.Application), then TOPMOST-flip + SetForegroundWindow.
    Never run two openers in sequence (that spawned double Explorer windows).
    """
    p = os.path.abspath(os.path.normpath(os.path.expanduser(path)))
    if not os.path.isdir(p):
        return {"ok": False, "error": "not a directory", "code": "not_found", "path": p}

    if sys.platform.startswith("win"):
        return _reveal_folder_win(p)
    if sys.platform == "darwin":
        try:
            subprocess.Popen(["open", p], close_fds=True)
            return {"ok": True, "path": p, "backend": "open"}
        except OSError as exc:
            return {"ok": False, "error": str(exc), "code": "reveal_failed", "path": p}
    try:
        subprocess.Popen(["xdg-open", p], close_fds=True)
        return {"ok": True, "path": p, "backend": "xdg-open"}
    except OSError as exc:
        return {"ok": False, "error": str(exc), "code": "reveal_failed", "path": p}


def _reveal_folder_win(path: str) -> Dict[str, Any]:
    """Windows: reuse or single-open Explorer, then force that window forward.

    Single PowerShell STA script (no ctypes+PS double open).
    """
    try:
        ok, detail = _reveal_folder_win_once(path)
        if ok:
            return {"ok": True, "path": path, "backend": detail or "shell.once+raise"}
    except Exception as exc:  # noqa: BLE001
        try:
            # last resort: one explorer only (may land behind browser)
            subprocess.Popen(["explorer", path], close_fds=True)
            return {
                "ok": True,
                "path": path,
                "backend": "explorer",
                "warn": f"raise path failed: {exc!r}",
            }
        except OSError as e2:
            return {"ok": False, "error": str(e2), "code": "reveal_failed", "path": path}
    return {"ok": True, "path": path, "backend": "shell.once"}


def _reveal_folder_win_once(path: str) -> tuple:
    """Run one STA PowerShell: find-or-open-once + raise. Returns (ok, backend)."""
    path_esc = path.replace("'", "''")
    body = f"""
$ErrorActionPreference = 'SilentlyContinue'
$p = (Resolve-Path -LiteralPath '{path_esc}').Path
$norm = $p.TrimEnd('\\')
$shell = New-Object -ComObject Shell.Application

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class PsyClawReveal {{
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);
  [DllImport("user32.dll")] public static extern bool AllowSetForegroundWindow(int dwProcessId);
  [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  public static readonly IntPtr HWND_TOPMOST = new IntPtr(-1);
  public static readonly IntPtr HWND_NOTOPMOST = new IntPtr(-2);
  public const uint SWP = 0x0001 | 0x0002 | 0x0040;
  public const int SW_RESTORE = 9;
  public const int SW_SHOW = 5;
  public const int ASFW_ANY = -1;
  public static void Raise(IntPtr h) {{
    if (h == IntPtr.Zero) return;
    AllowSetForegroundWindow(ASFW_ANY);
    if (IsIconic(h)) ShowWindow(h, SW_RESTORE);
    ShowWindow(h, SW_SHOW);
    BringWindowToTop(h);
    // TOPMOST flash — reliable when caller is not the foreground process
    SetWindowPos(h, HWND_TOPMOST, 0, 0, 0, 0, SWP);
    SetWindowPos(h, HWND_NOTOPMOST, 0, 0, 0, 0, SWP);
    // ALT key trick: resets foreground lock timeout for SetForegroundWindow
    const byte VK_MENU = 0x12;
    const uint KEYEVENTF_EXTENDEDKEY = 0x0001;
    const uint KEYEVENTF_KEYUP = 0x0002;
    keybd_event(VK_MENU, 0, KEYEVENTF_EXTENDEDKEY, UIntPtr.Zero);
    keybd_event(VK_MENU, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, UIntPtr.Zero);
    IntPtr fg = GetForegroundWindow();
    uint fgPid; uint fgTid = GetWindowThreadProcessId(fg, out fgPid);
    uint cur = GetCurrentThreadId();
    bool att = false;
    if (fgTid != 0 && fgTid != cur) att = AttachThreadInput(cur, fgTid, true);
    SetForegroundWindow(h);
    if (att) AttachThreadInput(cur, fgTid, false);
  }}
}}
"@

function Find-ExplorerHwnd([string]$want) {{
  foreach ($w in @($shell.Windows())) {{
    try {{
      if ($null -eq $w) {{ continue }}
      $fp = $w.Document.Folder.Self.Path
      if ($fp -and ($fp.TrimEnd('\\') -ieq $want)) {{
        return [IntPtr]$w.HWND
      }}
    }} catch {{}}
  }}
  return [IntPtr]::Zero
}}

# 1) Already open? Raise only — do NOT Explore again (avoids second window)
$h = Find-ExplorerHwnd $norm
$opened = $false
if ($h -eq [IntPtr]::Zero) {{
  # 2) Open exactly once
  $shell.Explore($p)
  $opened = $true
  # wait for the window to register with Shell.Application
  for ($i = 0; $i -lt 25; $i++) {{
    Start-Sleep -Milliseconds 80
    $h = Find-ExplorerHwnd $norm
    if ($h -ne [IntPtr]::Zero) {{ break }}
  }}
}}

if ($h -ne [IntPtr]::Zero) {{
  [PsyClawReveal]::Raise($h)
  # second raise after a beat (Explorer sometimes steals/loses focus while painting)
  Start-Sleep -Milliseconds 120
  [PsyClawReveal]::Raise($h)
  exit 0
}}

# Soft fallback: basename title match (no extra open)
$base = Split-Path -Leaf $norm
Get-Process explorer -ErrorAction SilentlyContinue |
  Where-Object {{ $_.MainWindowHandle -ne 0 }} |
  ForEach-Object {{
    try {{
      $t = $_.MainWindowTitle
      if ($t -and $base -and ($t -like "*$base*")) {{
        [PsyClawReveal]::Raise([IntPtr]$_.MainWindowHandle)
        exit 0
      }}
    }} catch {{}}
  }}
exit 0
"""
    fd, tmp_ps = tempfile.mkstemp(prefix="psyclaw_reveal_", suffix=".ps1")
    os.close(fd)
    try:
        with open(tmp_ps, "w", encoding="utf-8-sig", newline="\n") as f:
            f.write(body)
        flags = 0
        if hasattr(subprocess, "CREATE_NO_WINDOW"):
            flags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
        # Block briefly so raise finishes before HTTP returns (focus more reliable)
        proc = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-STA",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                tmp_ps,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=12,
            creationflags=flags,
        )
        try:
            os.unlink(tmp_ps)
        except OSError:
            pass
        if proc.returncode not in (0, None):
            return True, f"shell.once rc={proc.returncode}"
        return True, "shell.once+raise"
    except subprocess.TimeoutExpired:
        try:
            os.unlink(tmp_ps)
        except OSError:
            pass
        return True, "shell.once timeout"
    except OSError:
        try:
            os.unlink(tmp_ps)
        except OSError:
            pass
        return False, "launch failed"


if __name__ == "__main__":
    print(pick_folder("psyclaw dialog smoke", os.path.expanduser("~")))
