"""Host / PsychoPy environment probe for the System (preflight) tab.

Only checks that matter for:
  (1) experiment can run and write data
  (2) PsychoPy engine is healthy

Each check:
  {id, label, group, status: pass|warn|fail|info, detail, value?}
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple


def _psychopy_python() -> str:
    try:
        from psychopy_env import psychopy_python
    except ImportError:
        from backend.psychopy_env import psychopy_python  # type: ignore
    return psychopy_python()


def _os_label() -> str:
    """Human OS name. Win11 still reports platform.release()=='10' — use build ≥22000."""
    system = platform.system()
    if system == "Windows":
        build = 0
        display = ""
        product = ""
        try:
            # registry is the reliable marketing name source
            ps = (
                "$p = Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion'; "
                "$build = 0; [int]::TryParse($p.CurrentBuild, [ref]$build) | Out-Null; "
                "[pscustomobject]@{ build=$build; display=$p.DisplayVersion; product=$p.ProductName } "
                "| ConvertTo-Json -Compress"
            )
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps],
                capture_output=True,
                text=True,
                timeout=6,
            )
            raw = (proc.stdout or "").strip()
            if raw:
                import json as _json

                data = _json.loads(raw)
                build = int(data.get("build") or 0)
                display = str(data.get("display") or "").strip()
                product = str(data.get("product") or "").strip()
        except (OSError, subprocess.TimeoutExpired, ValueError, TypeError):
            pass
        if not build:
            # fallback parse 10.0.26200
            try:
                parts = platform.version().split(".")
                if len(parts) >= 3:
                    build = int(parts[2])
            except ValueError:
                build = 0
        # build ≥ 22000 ⇒ Windows 11 (even when ProductName still says Windows 10)
        if build >= 22000 or "windows 11" in product.lower():
            name = "Windows 11"
        elif product:
            # keep ProductName if already accurate
            name = "Windows 10" if "windows 10" in product.lower() else product
        else:
            name = "Windows 10" if platform.release() == "10" else f"Windows {platform.release()}"
        if display:
            return f"{name} {display}"
        if build:
            return f"{name} (build {build})"
        return name
    if system == "Darwin":
        return f"macOS {platform.mac_ver()[0] or ''}".strip()
    if system == "Linux":
        return f"Linux {platform.release()}".strip()
    return platform.platform()


# Win32_SystemEnclosure ChassisTypes (SMBIOS)
_CHASSIS_LAPTOP = {8, 9, 10, 11, 12, 14, 30, 31, 32}  # portable / laptop / notebook / tablet / convertible
_CHASSIS_DESKTOP = {3, 4, 5, 6, 7, 13, 15, 16, 34, 35}  # desktop / tower / AIO-ish


def _detect_form_factor() -> Dict[str, Any]:
    """Best-effort form factor for System tab illustration: laptop | desktop | mac | macbook."""
    system = platform.system()
    info: Dict[str, Any] = {
        "kind": "desktop",
        "label": "Desktop PC",
        "os": system,
        "detail": platform.platform(),
        "chassis_types": [],
        "has_battery": None,
        "model": None,
    }

    if system == "Darwin":
        model = ""
        try:
            proc = subprocess.run(
                ["system_profiler", "SPHardwareDataType"],
                capture_output=True,
                text=True,
                timeout=8,
            )
            for line in (proc.stdout or "").splitlines():
                if "Model Name" in line or "Model Identifier" in line:
                    model = line.split(":", 1)[-1].strip()
                    if "Model Name" in line:
                        break
        except (OSError, subprocess.TimeoutExpired):
            model = platform.machine()
        info["model"] = model or "Mac"
        low = (model or "").lower()
        if "macbook" in low or "book" in low:
            info["kind"] = "macbook"
            info["label"] = "MacBook"
        else:
            info["kind"] = "mac"
            info["label"] = model if model and "Mac" in model else "Mac"
        info["detail"] = model or platform.platform()
        return info

    if system == "Linux":
        chassis = ""
        try:
            p = "/sys/class/dmi/id/chassis_type"
            if os.path.isfile(p):
                chassis = open(p, encoding="utf-8", errors="replace").read().strip()
        except OSError:
            pass
        try:
            ct = int(chassis) if chassis else 0
        except ValueError:
            ct = 0
        if ct:
            info["chassis_types"] = [ct]
        # battery
        bat = os.path.isdir("/sys/class/power_supply")
        has_bat = False
        if bat:
            try:
                for name in os.listdir("/sys/class/power_supply"):
                    if name.upper().startswith("BAT"):
                        has_bat = True
                        break
            except OSError:
                pass
        info["has_battery"] = has_bat
        if ct in _CHASSIS_LAPTOP or has_bat:
            info["kind"] = "laptop"
            info["label"] = "Laptop"
        else:
            info["kind"] = "desktop"
            info["label"] = "Desktop PC"
        info["detail"] = f"chassis={ct or '?'} battery={has_bat}"
        return info

    # Windows
    if system == "Windows":
        chassis_types: List[int] = []
        # PowerShell CIM — more reliable than legacy wmic on Win11
        ps = (
            "try { "
            "(Get-CimInstance -ClassName Win32_SystemEnclosure).ChassisTypes "
            "| ForEach-Object { $_ } "
            "} catch { }"
        )
        try:
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps],
                capture_output=True,
                text=True,
                timeout=10,
            )
            for tok in (proc.stdout or "").replace(",", " ").split():
                tok = tok.strip()
                if tok.isdigit():
                    chassis_types.append(int(tok))
        except (OSError, subprocess.TimeoutExpired):
            pass
        info["chassis_types"] = chassis_types

        has_bat = None
        try:
            proc = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "(Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue | Measure-Object).Count",
                ],
                capture_output=True,
                text=True,
                timeout=8,
            )
            raw = (proc.stdout or "").strip().splitlines()
            if raw and raw[-1].isdigit():
                has_bat = int(raw[-1]) > 0
        except (OSError, subprocess.TimeoutExpired):
            pass
        info["has_battery"] = has_bat

        model = ""
        try:
            proc = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "(Get-CimInstance Win32_ComputerSystem).Model",
                ],
                capture_output=True,
                text=True,
                timeout=8,
            )
            model = (proc.stdout or "").strip().splitlines()
            model = model[-1].strip() if model else ""
        except (OSError, subprocess.TimeoutExpired):
            model = ""
        info["model"] = model or None

        is_laptop = any(c in _CHASSIS_LAPTOP for c in chassis_types)
        is_desktop = any(c in _CHASSIS_DESKTOP for c in chassis_types)
        if not is_laptop and not is_desktop and has_bat is True:
            is_laptop = True
        if is_laptop and not is_desktop:
            info["kind"] = "laptop"
            info["label"] = "Laptop"
        elif is_desktop and not is_laptop:
            info["kind"] = "desktop"
            info["label"] = "Desktop PC"
        elif is_laptop:
            info["kind"] = "laptop"
            info["label"] = "Laptop"
        else:
            info["kind"] = "desktop"
            info["label"] = "Desktop PC"
        bits = []
        if model:
            bits.append(model)
        if chassis_types:
            bits.append("chassis=" + ",".join(str(c) for c in chassis_types))
        if has_bat is not None:
            bits.append("battery=" + ("yes" if has_bat else "no"))
        info["detail"] = " · ".join(bits) if bits else platform.platform()
        return info

    info["kind"] = "desktop"
    info["label"] = "Workstation"
    return info


def _classify_pnp_connection(instance_id: str, name: str = "") -> str:
    """Heuristic: bluetooth | usb | ps2 | built-in | wireless | other."""
    s = f"{instance_id or ''} {name or ''}".upper()
    if any(tok in s for tok in ("BTHENUM", "BTHLE", "BLUETOOTH", "BTH\\")):
        return "bluetooth"
    if "USB" in s or "HID\\VID" in s or "VID_" in s:
        return "usb"
    if "PS2" in s or "I8042" in s:
        return "ps2"
    if any(tok in s for tok in ("ACPI", "PNP0", "SYNA", "ELAN", "I2C\\", "MSFT0001")):
        return "built-in"
    if any(tok in s for tok in ("RMI", "TOUCHPAD", "TRACKPAD")):
        return "built-in"
    if "HID" in s:
        return "usb"
    return "other"


def _detect_hardware() -> Dict[str, Any]:
    """CPU / GPU / RAM / keyboard+mouse / monitors / speakers (best-effort)."""
    system = platform.system()
    out: Dict[str, Any] = {
        "cpu": None,
        "gpus": [],
        "ram_gb": None,
        "keyboards": [],
        "mice": [],
        "monitors": [],
        "speakers": [],
        "microphones": [],
        "os": system,
    }

    if system == "Windows":
        # One PowerShell round-trip → JSON (includes AllScreens + sound devices)
        ps = r"""
$ErrorActionPreference = 'SilentlyContinue'
$cpu = (Get-CimInstance Win32_Processor | Select-Object -First 1).Name
$gpus = @(Get-CimInstance Win32_VideoController | ForEach-Object { $_.Name } | Where-Object { $_ })
$ramBytes = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
$ramGb = if ($ramBytes) { [math]::Round($ramBytes / 1GB, 1) } else { $null }
function Map-Dev($cls) {
  @(Get-PnpDevice -Class $cls -Status OK -ErrorAction SilentlyContinue | ForEach-Object {
    $id = $_.InstanceId
    $nm = $_.FriendlyName
    $u = ("$id $nm").ToUpper()
    $conn = 'other'
    if ($u -match 'BTHENUM|BTHLE|BLUETOOTH|BTH\\') { $conn = 'bluetooth' }
    elseif ($u -match 'USB|HID\\VID|VID_') { $conn = 'usb' }
    elseif ($u -match 'PS2|I8042') { $conn = 'ps2' }
    elseif ($u -match 'ACPI|PNP0|SYNA|ELAN|I2C\\|MSFT0001|RMI|TOUCHPAD|TRACKPAD') { $conn = 'built-in' }
    elseif ($u -match 'HID') { $conn = 'usb' }
    [pscustomobject]@{ name = $nm; connection = $conn; instance_id = $id }
  })
}
$kbs = Map-Dev 'Keyboard'
$mice = Map-Dev 'Mouse'
$mons = @()
try {
  Add-Type -AssemblyName System.Windows.Forms | Out-Null
  $i = 0
  foreach ($s in [System.Windows.Forms.Screen]::AllScreens) {
    $dev = [string]$s.DeviceName
    $label = if ($s.Primary) { "Monitor $($i+1) · Primary" } else { "Monitor $($i+1)" }
    $mons += [pscustomobject]@{
      index = $i
      primary = [bool]$s.Primary
      width = [int]$s.Bounds.Width
      height = [int]$s.Bounds.Height
      x = [int]$s.Bounds.X
      y = [int]$s.Bounds.Y
      device = $dev
      label = $label
    }
    $i++
  }
} catch {}
$speakers = @()
$microphones = @()
try {
  # Real WASAPI endpoints (jacks/HDMI/USB headsets), NOT Win32_SoundDevice drivers.
  # InstanceId: {0.0.0.*}=render(playback)  {0.0.1.*}=capture(mic)
  $eps = @(Get-PnpDevice -Class 'AudioEndpoint' -ErrorAction SilentlyContinue)
  foreach ($e in $eps) {
    $id = [string]$e.InstanceId
    $nm = [string]$e.FriendlyName
    $st = [string]$e.Status
    if (-not $nm) { continue }
    $u = ("$id $nm").ToUpperInvariant()
    $virt = $false
    if ($u -match 'VIRTUAL|VB-AUDIO|CABLE INPUT|CABLE OUTPUT|STEREO MIX|WHAT U HEAR|NVIDIA VIRTUAL|BROADCAST') { $virt = $true }
    $flow = 'other'
    if ($id -match '\{0\.0\.0\.') { $flow = 'render' }
    elseif ($id -match '\{0\.0\.1\.') { $flow = 'capture' }
    else { continue }
    $obj = [pscustomobject]@{
      name = $nm
      status = $st
      flow = $flow
      virtual = [bool]$virt
      instance_id = $id
      source = 'endpoint'
    }
    if ($flow -eq 'render') { $speakers += $obj }
    else { $microphones += $obj }
  }
} catch {}
# Fallback: sound *drivers* only when no endpoints found (honest: not a jack)
if (-not $speakers -or $speakers.Count -eq 0) {
  try {
    $speakers = @(Get-CimInstance Win32_SoundDevice | ForEach-Object {
      $nm = $_.Name
      if ($nm) {
        $u = $nm.ToUpperInvariant()
        $virt = [bool]($u -match 'VIRTUAL|BROADCAST')
        [pscustomobject]@{
          name = $nm
          status = [string]$_.Status
          flow = 'render'
          virtual = $virt
          instance_id = ''
          source = 'driver'
        }
      }
    })
  } catch {}
}
if ((-not $speakers -or $speakers.Count -eq 0)) {
  try {
    $speakers = @(Get-PnpDevice -Class 'MEDIA' -Status OK -ErrorAction SilentlyContinue | ForEach-Object {
      $nm = $_.FriendlyName
      if (-not $nm) { return }
      $u = $nm.ToUpperInvariant()
      $virt = [bool]($u -match 'VIRTUAL|BROADCAST')
      [pscustomobject]@{
        name = $nm
        status = 'OK'
        flow = 'render'
        virtual = $virt
        instance_id = [string]$_.InstanceId
        source = 'driver'
      }
    })
  } catch {}
}
[pscustomobject]@{
  cpu = $cpu
  gpus = $gpus
  ram_gb = $ramGb
  keyboards = $kbs
  mice = $mice
  monitors = $mons
  speakers = $speakers
  microphones = $microphones
} | ConvertTo-Json -Compress -Depth 6
"""
        try:
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false); "
                 "$OutputEncoding = [Console]::OutputEncoding; " + ps],
                capture_output=True,
                timeout=16,
            )
            raw_bytes = proc.stdout or b""
            raw = ""
            for enc in ("utf-8-sig", "utf-8", "gbk", "cp936", "latin-1"):
                try:
                    raw = raw_bytes.decode(enc).strip()
                    if raw:
                        break
                except UnicodeDecodeError:
                    continue
            if not raw:
                raw = raw_bytes.decode("utf-8", errors="replace").strip()
            if raw:
                import json as _json

                data = _json.loads(raw)
                out["cpu"] = data.get("cpu") or None
                gpus = data.get("gpus") or []
                if isinstance(gpus, str):
                    gpus = [gpus]
                out["gpus"] = [g for g in gpus if g]
                try:
                    out["ram_gb"] = float(data["ram_gb"]) if data.get("ram_gb") is not None else None
                except (TypeError, ValueError):
                    out["ram_gb"] = None

                def _norm_list(items: Any) -> List[Dict[str, Any]]:
                    if not items:
                        return []
                    if isinstance(items, dict):
                        items = [items]
                    res = []
                    for it in items:
                        if not isinstance(it, dict):
                            continue
                        name = it.get("name") or ""
                        conn = it.get("connection") or _classify_pnp_connection(
                            str(it.get("instance_id") or ""), str(name)
                        )
                        res.append(
                            {
                                "name": name,
                                "connection": conn,
                                "instance_id": it.get("instance_id"),
                            }
                        )
                    return res

                out["keyboards"] = _norm_list(data.get("keyboards"))
                out["mice"] = _norm_list(data.get("mice"))

                mons_raw = data.get("monitors") or []
                if isinstance(mons_raw, dict):
                    mons_raw = [mons_raw]
                monitors: List[Dict[str, Any]] = []
                for it in mons_raw:
                    if not isinstance(it, dict):
                        continue
                    try:
                        idx = int(it.get("index", len(monitors)))
                        w = int(it.get("width") or 0)
                        h = int(it.get("height") or 0)
                    except (TypeError, ValueError):
                        continue
                    if w < 1 or h < 1:
                        continue
                    primary = bool(it.get("primary"))
                    label = str(it.get("label") or "").strip()
                    if not label:
                        label = f"Monitor {idx + 1}" + (" · Primary" if primary else "")
                    monitors.append(
                        {
                            "index": idx,
                            "primary": primary,
                            "width": w,
                            "height": h,
                            "x": int(it.get("x") or 0),
                            "y": int(it.get("y") or 0),
                            "device": str(it.get("device") or ""),
                            "label": label,
                        }
                    )
                out["monitors"] = monitors

                spk_raw = data.get("speakers") or []
                if isinstance(spk_raw, dict):
                    spk_raw = [spk_raw]
                speakers: List[Dict[str, Any]] = []
                for it in spk_raw:
                    if not isinstance(it, dict):
                        continue
                    nm = str(it.get("name") or "").strip()
                    if not nm:
                        continue
                    speakers.append(
                        {
                            "name": nm,
                            "status": str(it.get("status") or ""),
                            "flow": str(it.get("flow") or "render"),
                            "virtual": bool(it.get("virtual")),
                            "instance_id": str(it.get("instance_id") or ""),
                            "source": str(it.get("source") or ""),
                        }
                    )
                out["speakers"] = speakers

                mic_raw = data.get("microphones") or []
                if isinstance(mic_raw, dict):
                    mic_raw = [mic_raw]
                microphones: List[Dict[str, Any]] = []
                for it in mic_raw:
                    if not isinstance(it, dict):
                        continue
                    nm = str(it.get("name") or "").strip()
                    if not nm:
                        continue
                    microphones.append(
                        {
                            "name": nm,
                            "status": str(it.get("status") or ""),
                            "flow": str(it.get("flow") or "capture"),
                            "virtual": bool(it.get("virtual")),
                            "instance_id": str(it.get("instance_id") or ""),
                            "source": str(it.get("source") or ""),
                        }
                    )
                out["microphones"] = microphones
        except (OSError, subprocess.TimeoutExpired, ValueError):
            pass
        return out

    if system == "Darwin":
        try:
            proc = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True,
                text=True,
                timeout=4,
            )
            out["cpu"] = (proc.stdout or "").strip() or None
        except (OSError, subprocess.TimeoutExpired):
            pass
        try:
            proc = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            gpus = []
            monitors: List[Dict[str, Any]] = []
            cur_w = cur_h = None
            for line in (proc.stdout or "").splitlines():
                if "Chipset Model" in line or "Chipset model" in line:
                    gpus.append(line.split(":", 1)[-1].strip())
                low = line.lower()
                if "resolution" in low and ":" in line:
                    # e.g. Resolution: 2560 x 1600
                    rest = line.split(":", 1)[-1].strip()
                    parts = rest.replace("×", "x").lower().split("x")
                    try:
                        if len(parts) >= 2:
                            cur_w = int("".join(c for c in parts[0] if c.isdigit()) or 0)
                            cur_h = int("".join(c for c in parts[1] if c.isdigit()) or 0)
                            if cur_w and cur_h:
                                idx = len(monitors)
                                monitors.append(
                                    {
                                        "index": idx,
                                        "primary": idx == 0,
                                        "width": cur_w,
                                        "height": cur_h,
                                        "x": 0,
                                        "y": 0,
                                        "device": "",
                                        "label": f"Monitor {idx + 1}"
                                        + (" · Primary" if idx == 0 else ""),
                                    }
                                )
                    except ValueError:
                        pass
            out["gpus"] = gpus
            out["monitors"] = monitors
        except (OSError, subprocess.TimeoutExpired):
            pass
        try:
            import psutil  # type: ignore

            out["ram_gb"] = round(psutil.virtual_memory().total / (1024**3), 1)
        except Exception:  # noqa: BLE001
            pass
        return out

    # Linux
    try:
        with open("/proc/cpuinfo", encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.lower().startswith("model name"):
                    out["cpu"] = line.split(":", 1)[-1].strip()
                    break
    except OSError:
        pass
    try:
        mem_kb = None
        with open("/proc/meminfo", encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    mem_kb = int(line.split()[1])
                    break
        if mem_kb:
            out["ram_gb"] = round(mem_kb / (1024**2), 1)
    except (OSError, ValueError):
        pass
    # GPU via lspci if present
    try:
        proc = subprocess.run(
            ["lspci"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        gpus = []
        for line in (proc.stdout or "").splitlines():
            low = line.lower()
            if "vga" in low or "3d" in low or "display" in low:
                gpus.append(line.split(":", 2)[-1].strip() if ":" in line else line.strip())
        out["gpus"] = gpus[:4]
    except (OSError, subprocess.TimeoutExpired):
        pass
    # xrandr monitors when available
    try:
        proc = subprocess.run(
            ["xrandr", "--query"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        monitors = []
        for line in (proc.stdout or "").splitlines():
            if " connected" not in line:
                continue
            # e.g. HDMI-1 connected primary 1920x1080+0+0
            primary = " primary " in line or line.endswith(" primary")
            m = None
            import re as _re

            m = _re.search(r"(\d+)x(\d+)\+(\d+)\+(\d+)", line)
            if not m:
                continue
            idx = len(monitors)
            monitors.append(
                {
                    "index": idx,
                    "primary": primary or idx == 0,
                    "width": int(m.group(1)),
                    "height": int(m.group(2)),
                    "x": int(m.group(3)),
                    "y": int(m.group(4)),
                    "device": line.split()[0],
                    "label": f"Monitor {idx + 1}" + (" · Primary" if (primary or idx == 0) else ""),
                }
            )
        out["monitors"] = monitors
    except (OSError, subprocess.TimeoutExpired, ValueError):
        pass
    return out


def _disk_free_gb(path: str) -> Optional[float]:
    try:
        usage = shutil.disk_usage(path)
        return round(usage.free / (1024**3), 2)
    except OSError:
        return None


def _disk_total_gb(path: str) -> Optional[float]:
    try:
        usage = shutil.disk_usage(path)
        return round(usage.total / (1024**3), 2)
    except OSError:
        return None


def _disk_root(path: str) -> str:
    """Volume root letter/path (e.g. 'E:\\\\' on Windows, '/' on Unix)."""
    abs_path = os.path.abspath(path)
    if platform.system() == "Windows":
        drive, _ = os.path.splitdrive(abs_path)
        if drive:
            return drive + "\\"
        return abs_path
    # best-effort: walk up until parent stops changing (mount root unknown)
    return os.path.abspath(os.sep)


def _resolve_existing_path(path: str) -> str:
    """Walk up until an existing path for shutil.disk_usage (drive root ok)."""
    p = os.path.abspath(os.path.expanduser(path))
    if os.path.exists(p):
        return p
    cur = p
    while True:
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        if os.path.exists(parent):
            return parent
        cur = parent
    if platform.system() == "Windows":
        drive, _ = os.path.splitdrive(p)
        if drive:
            root = drive + "\\"
            if os.path.exists(root):
                return root
    return os.path.abspath(".")


def probe_disk(data_path: Optional[str]) -> Dict[str, Any]:
    """Disk free for the experiment folder volume only.

    No path → pending (do not invent a default drive).
    With path → free space on that path's volume + root letter.
    """
    if not data_path or not str(data_path).strip():
        facts = {
            "path": None,
            "probe_path": None,
            "root": None,
            "free_gb": None,
            "total_gb": None,
            "pending": True,
        }
        check = {
            "id": "disk_free",
            "label": "Disk free (data)",
            "group": "runtime",
            "status": "info",
            "detail": "Open experiment folder in Builder first",
            "value": None,
        }
        return {"ok": True, "facts": {"disk": facts}, "check": check}

    raw = str(data_path).strip()
    probe_path = _resolve_existing_path(raw)
    root = _disk_root(probe_path)
    free_gb = _disk_free_gb(probe_path)
    total_gb = _disk_total_gb(probe_path)
    facts = {
        "path": os.path.abspath(os.path.expanduser(raw)),
        "probe_path": probe_path,
        "root": root,
        "free_gb": free_gb,
        "total_gb": total_gb,
        "pending": False,
    }
    # short root label for detail: "E:" not "E:\"
    if platform.system() == "Windows" and len(root) >= 2 and root[1] == ":":
        root_label = root[:2]  # E:
    else:
        root_label = root

    if free_gb is None:
        status, detail = "warn", f"could not read free space · {root_label} · {probe_path}"
    elif free_gb < 1:
        status, detail = "fail", f"{root_label} · {free_gb} GB free — need ≥1 GB · {probe_path}"
    elif free_gb < 5:
        status, detail = "warn", f"{root_label} · {free_gb} GB free · {probe_path}"
    else:
        status, detail = "pass", f"{root_label} · {free_gb} GB free · {probe_path}"

    check = {
        "id": "disk_free",
        "label": "Disk free (data)",
        "group": "runtime",
        "status": status,
        "detail": detail,
        "value": free_gb,
    }
    return {"ok": status != "fail", "facts": {"disk": facts}, "check": check}


def _run_py(exe: str, code: str, timeout: float = 12.0) -> Tuple[int, str, str]:
    try:
        proc = subprocess.run(
            [exe, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONPATH": "", "PYTHONHOME": ""},
        )
        return proc.returncode, (proc.stdout or "").strip(), (proc.stderr or "").strip()
    except FileNotFoundError:
        return 127, "", "executable not found"
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except OSError as exc:
        return 1, "", str(exc)


def probe(runs_dir: str, data_path: Optional[str] = None) -> Dict[str, Any]:
    """Host preflight.

    Disk free is bound to the experiment folder path (data_path), not the
    internal runs/ dir. Without data_path the disk check stays pending.
    ``runs_dir`` is retained for callers/compat only (not used for Data disk).
    """
    checks: List[Dict[str, Any]] = []
    facts: Dict[str, Any] = {}
    t0 = time.time()
    _ = runs_dir  # reserved / compat

    # facts always (raw report), not all become UI checks
    facts["os"] = {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "platform": platform.platform(),
        "label": _os_label(),
    }
    facts["host_python"] = {
        "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "executable": sys.executable,
    }
    try:
        facts["form_factor"] = _detect_form_factor()
    except Exception as exc:  # noqa: BLE001
        facts["form_factor"] = {
            "kind": "desktop",
            "label": "Desktop PC",
            "detail": f"detect failed: {exc!r}",
            "os": platform.system(),
        }

    try:
        facts["hardware"] = _detect_hardware()
    except Exception as exc:  # noqa: BLE001
        facts["hardware"] = {"error": repr(exc), "cpu": None, "gpus": [], "ram_gb": None,
                             "keyboards": [], "mice": []}

    # --- Disk free (experiment folder volume only) ---
    disk_report = probe_disk(data_path)
    facts["disk"] = disk_report["facts"]["disk"]
    checks.append(disk_report["check"])

    # --- PsychoPy python binary ---
    pp = _psychopy_python()
    force_mock = os.environ.get("PSYCLAW_FORCE_MOCK", "0") == "1"
    facts["psychopy_python_path"] = pp
    facts["force_mock"] = force_mock
    exists = os.path.isfile(pp)
    checks.append(
        {
            "id": "psychopy_python",
            "label": "PsychoPy Python",
            "group": "engine",
            "status": "pass" if exists else "fail",
            "detail": pp if exists else f"missing: {pp}",
            "value": pp,
        }
    )

    # --- PsychoPy import + version ---
    psy_ver: Optional[str] = None
    psy_err: Optional[str] = None
    if exists:
        code, out, err = _run_py(
            pp,
            "import psychopy; print(psychopy.__version__)",
            timeout=20.0,
        )
        if code == 0 and out:
            psy_ver = out.splitlines()[-1].strip()
        else:
            psy_err = err or out or f"exit {code}"
    facts["psychopy"] = {"version": psy_ver, "error": psy_err}
    if force_mock:
        checks.append(
            {
                "id": "psychopy_import",
                "label": "PsychoPy import",
                "group": "engine",
                "status": "warn",
                "detail": "PSYCLAW_FORCE_MOCK=1 — runs use MockProcess",
                "value": psy_ver,
            }
        )
    elif psy_ver:
        checks.append(
            {
                "id": "psychopy_import",
                "label": "PsychoPy import",
                "group": "engine",
                "status": "pass",
                "detail": f"psychopy {psy_ver}",
                "value": psy_ver,
            }
        )
    else:
        checks.append(
            {
                "id": "psychopy_import",
                "label": "PsychoPy import",
                "group": "engine",
                "status": "fail",
                "detail": psy_err or "PsychoPy not importable",
                "value": None,
            }
        )

    # --- Window backend + graphics libs (one card) ---
    win_backend = None
    backends = "n/a"
    if exists and psy_ver and not force_mock:
        code, out, err = _run_py(
            pp,
            (
                "import os\n"
                "os.environ.setdefault('PSYCHOPY_DISABLE_VERSION_CHECK','1')\n"
                "from psychopy import prefs\n"
                "print(prefs.general.get('winType', 'default') or 'default')\n"
            ),
            timeout=15.0,
        )
        if code == 0 and out:
            win_backend = out.splitlines()[-1].strip()

        code2, out2, _err2 = _run_py(
            pp,
            (
                "mods=[]\n"
                "for m in ('pyglet','glfw','pygame'):\n"
                "  try:\n"
                "    __import__(m); mods.append(m)\n"
                "  except Exception:\n"
                "    pass\n"
                "print(','.join(mods) if mods else 'none')\n"
            ),
            timeout=12.0,
        )
        backends = out2 if code2 == 0 else "unknown"
    facts["win_backend"] = win_backend
    facts["graphics_libs"] = backends

    if force_mock or not exists:
        gfx_status, gfx_detail = "info", "n/a (mock or no binary)"
    elif win_backend or (backends not in ("none", "unknown", "")):
        gfx_status = "pass"
        bits = []
        if win_backend:
            bits.append(f"winType={win_backend}")
        if backends and backends not in ("n/a",):
            bits.append(f"libs={backends}")
        gfx_detail = " · ".join(bits) if bits else "ok"
    else:
        gfx_status, gfx_detail = "warn", "no winType / no pyglet|glfw|pygame"

    checks.append(
        {
            "id": "psychopy_graphics",
            "label": "PsychoPy graphics",
            "group": "engine",
            "status": gfx_status,
            "detail": gfx_detail,
            "value": {"winType": win_backend, "libs": backends},
        }
    )

    # --- Runner mode summary ---
    if force_mock:
        mode, mode_status = "mock (forced)", "warn"
    elif exists and psy_ver:
        mode, mode_status = "psychopy-real", "pass"
    elif exists:
        mode, mode_status = "binary present but import failed", "fail"
    else:
        mode, mode_status = "mock (no PsychoPy binary)", "warn"
    facts["runner_mode"] = mode
    checks.append(
        {
            "id": "runner_mode",
            "label": "Run engine",
            "group": "engine",
            "status": mode_status,
            "detail": mode,
            "value": mode,
        }
    )

    counts = {"pass": 0, "warn": 0, "fail": 0, "info": 0}
    for c in checks:
        st = c.get("status") or "info"
        counts[st] = counts.get(st, 0) + 1

    overall = "pass"
    if counts.get("fail", 0):
        overall = "fail"
    elif counts.get("warn", 0):
        overall = "warn"

    return {
        "ok": overall != "fail",
        "overall": overall,
        "counts": counts,
        "checks": checks,
        "facts": facts,
        "elapsed_ms": int((time.time() - t0) * 1000),
        "checked_at": time.time(),
    }
