# screenshot_window.ps1 — Capture any window's contents via Win32 PrintWindow
#
# Works even when cua-driver / computer_use can't see the window because
# another app owns the foreground focus. Reads the window's hwnd from
# Get-Process by title match, then PrintWindow -> PNG.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File screenshot_window.ps1 -TitlePattern "*code_test*" -Out out.png
#   powershell -ExecutionPolicy Bypass -File screenshot_window.ps1 -Pid 31944 -Out out.png

param(
    [string]$TitlePattern = "",
    [int]$Pid = 0,
    [string]$Out = "screenshot.png"
)

Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class W {
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdcBlt, uint nFlags);
  [DllImport("user32.dll")] public static extern bool IsWindow(IntPtr h);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
}
'@

$proc = $null
if ($Pid -gt 0) {
    $proc = Get-Process -Id $Pid -ErrorAction SilentlyContinue
} elseif ($TitlePattern) {
    $proc = Get-Process | Where-Object { $_.MainWindowTitle -like $TitlePattern } | Select-Object -First 1
} else {
    Write-Host "ERROR: provide -TitlePattern or -Pid"
    exit 1
}

if (-not $proc) { Write-Host "ERROR: no process matched"; exit 2 }
$h = $proc.MainWindowHandle
if ($h -eq [IntPtr]::Zero) { Write-Host "ERROR: process has no MainWindowHandle"; exit 3 }
if (-not [W]::IsWindow($h)) { Write-Host "ERROR: hwnd $h is not a valid window"; exit 4 }

$r = New-Object 'W+RECT'
[W]::GetWindowRect($h, [ref]$r) | Out-Null
$w  = $r.R - $r.L
$ht = $r.B - $r.T
if ($w -le 0 -or $ht -le 0) { Write-Host "ERROR: zero-size rect"; exit 5 }
Write-Host "Capturing hwnd=$h pid=$($proc.Id) '$($proc.MainWindowTitle)' ${w}x${ht}"

$bmp = New-Object System.Drawing.Bitmap $w, $ht
$g   = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
$ok  = [W]::PrintWindow($h, $hdc, 2)   # PW_RENDERFULLCONTENT for DWM-composed windows
$g.ReleaseHdc($hdc)
$g.Dispose()
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()

if (-not $ok) { Write-Host "WARN: PrintWindow returned false (may be partial render)" }
Write-Host "OK saved $Out"
exit 0