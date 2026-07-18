# close_psychopy.ps1 — Cleanly close PsychoPy Builder without taskkill.
#
# Sends WM_CLOSE to the main window + every child window (in case a "Save?"
# modal is on top). Does NOT use taskkill, so it cannot kill Hermes' own
# pythonw.exe gateway/worker processes.
#
# Usage: powershell -ExecutionPolicy Bypass -File close_psychopy.ps1

Add-Type @'
using System;
using System.Runtime.InteropServices;
public class W {
  [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr p, EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
}
'@

$procs = Get-Process pythonw | Where-Object { $_.MainWindowTitle -like '*PsychoPy*' }
if (-not $procs) {
    Write-Host "No PsychoPy Builder found."
    exit 0
}

foreach ($proc in $procs) {
    $h = $proc.MainWindowHandle
    Write-Host "Closing pid=$($proc.Id) hwnd=$h title='$($proc.MainWindowTitle)'"
    [void][W]::EnumChildWindows($h, {
        param($c, $l)
        [W]::SendMessage($c, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null
        return $true
    }, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 300
    [W]::SendMessage($h, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null
}

Start-Sleep -Seconds 2
$remaining = Get-Process pythonw | Where-Object { $_.MainWindowTitle -like '*PsychoPy*' }
if ($remaining) {
    Write-Host "WARN: still $($remaining.Count) builder process(es):"
    $remaining | ForEach-Object { Write-Host "  pid=$($_.Id) title='$($_.MainWindowTitle)'" }
    exit 1
}
Write-Host "OK: all PsychoPy Builder processes closed."
exit 0
