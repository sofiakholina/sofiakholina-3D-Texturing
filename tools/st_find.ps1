# Finds ComfyUI (Comfy Desktop / Portable / Easy-Install / any path) and runs tools\st_setup.py with its Python.
# Usage: st_find.ps1 <install|uninstall|check> [--comfy <path>] [--pick N] [other st_setup.py flags]
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$tools = $PSScriptRoot
$root = Split-Path $tools -Parent
# same check as st_setup.py (Get-UICulture is unreliable after chcp 65001)
try {
    $k = Add-Type -MemberDefinition '[DllImport("kernel32.dll")] public static extern ushort GetUserDefaultUILanguage();' -Name UiLang -Namespace SofiaKholina -PassThru
    $ru = ($k::GetUserDefaultUILanguage() -band 0x3FF) -in @(0x19, 0x22, 0x23, 0x3F)
} catch { $ru = [System.Globalization.CultureInfo]::InstalledUICulture.TwoLetterISOLanguageName -in @("ru", "uk", "be", "kk") }
function Say($r, $e, $c) { $m = if ($ru) { $r } else { $e }; if ($c) { Write-Host $m -ForegroundColor $c } else { Write-Host $m } }

$cmd = "install"; $comfyArg = $null; $pick = 0; $rest = @()
for ($i = 0; $i -lt $args.Count; $i++) {
    $a = [string]$args[$i]
    if ($i -eq 0 -and $a -in @("install", "uninstall", "check")) { $cmd = $a; continue }
    if ($a -eq "--comfy") { $comfyArg = $args[++$i]; continue }
    if ($a -eq "--pick") { $pick = [int]$args[++$i]; continue }
    $rest += $a
}

$found = New-Object System.Collections.ArrayList
function Add-Found($kind, $comfy, $base, $python, $yaml, $label) {
    if (-not (Test-Path -LiteralPath (Join-Path $comfy "main.py"))) { return }
    if (-not (Test-Path -LiteralPath $python)) { return }
    foreach ($f in $found) { if ($f.Python -eq $python -and $f.Base -eq $base) { return } }
    [void]$found.Add([pscustomobject]@{ Kind = $kind; Comfy = $comfy; Base = $base; Python = $python; Yaml = $yaml; Label = $label })
}

function Parent-Of($p) { if (-not $p) { return $null }; $x = Split-Path $p -Parent; if ($x) { return $x } else { return $null } }

function Probe-Folder($p) {
    try { Probe-FolderInner $p } catch { }
}

function Probe-FolderInner($p) {
    if (-not $p -or -not (Test-Path -LiteralPath $p)) { return }
    $p = (Resolve-Path -LiteralPath $p).Path
    # Portable / Easy-Install: <dir>\python_embeded + <dir>\ComfyUI
    foreach ($d in @($p, (Parent-Of $p))) {
        if (-not $d) { continue }
        $py = Join-Path $d "python_embeded\python.exe"
        if (Test-Path -LiteralPath $py) { Add-Found "portable" (Join-Path $d "ComfyUI") (Join-Path $d "ComfyUI") $py $null $d }
    }
    # venv next to ComfyUI (Comfy Desktop install folder, manual installs)
    foreach ($c in @($p, (Join-Path $p "ComfyUI"))) {
        foreach ($v in @(".venv", "venv")) {
            foreach ($vd in @((Join-Path $c $v), $(if (Parent-Of $c) { Join-Path (Parent-Of $c) $v }))) {
                if (-not $vd) { continue }
                $py = Join-Path $vd "Scripts\python.exe"
                if (Test-Path -LiteralPath $py) { Add-Found "venv" $c $c $py $null $c }
            }
        }
    }
}

if ($comfyArg) {
    Probe-Folder $comfyArg
} else {
    # 1) Comfy Desktop (new launcher)
    $cd = Join-Path $env:APPDATA "Comfy Desktop"
    $inst = Join-Path $cd "installations.json"
    if (Test-Path -LiteralPath $inst) {
        try {
            $list = Get-Content -LiteralPath $inst -Raw -Encoding UTF8 | ConvertFrom-Json
            foreach ($x in @($list)) {
                if ($x.status -and $x.status -ne "installed") { continue }
                $c = Join-Path $x.installPath "ComfyUI"
                $y = Join-Path $cd ("instance-model-paths\" + $x.id + ".yaml")
                if (-not (Test-Path -LiteralPath $y)) { $y = $null }
                Add-Found "comfy-desktop" $c $c (Join-Path $c ".venv\Scripts\python.exe") $y ("Comfy Desktop: " + $x.name)
            }
        } catch { }
    }
    # 2) ComfyUI Desktop (older official app) - not tested
    $old = Join-Path $env:APPDATA "ComfyUI\config.json"
    if (Test-Path -LiteralPath $old) {
        try {
            $cfg = Get-Content -LiteralPath $old -Raw -Encoding UTF8 | ConvertFrom-Json
            $b = $cfg.basePath
            $res = Get-ChildItem -Path (Join-Path $env:LOCALAPPDATA "Programs") -Directory -ErrorAction SilentlyContinue |
                ForEach-Object { Join-Path $_.FullName "resources\ComfyUI" } | Where-Object { Test-Path -LiteralPath (Join-Path $_ "main.py") } | Select-Object -First 1
            $y = Join-Path $env:APPDATA "ComfyUI\extra_models_config.yaml"
            if (-not (Test-Path -LiteralPath $y)) { $y = $null }
            if ($b -and $res) { Add-Found "desktop-legacy" $res $b (Join-Path $b ".venv\Scripts\python.exe") $y "ComfyUI Desktop" }
        } catch { }
    }
    # 3) Portable / Easy-Install / venv around this folder
    $d = $root
    for ($k = 0; $k -lt 4 -and $d; $k++) {
        Probe-Folder $d
        Get-ChildItem -LiteralPath $d -Directory -ErrorAction SilentlyContinue | ForEach-Object { Probe-Folder $_.FullName }
        $d = Parent-Of $d
    }
}

while ($found.Count -eq 0) {
    if ($rest -contains "--yes") { Say "ComfyUI не найден. Установите Comfy Desktop (https://www.comfy.org/download) или укажите путь: --comfy <папка>" "ComfyUI not found. Install Comfy Desktop (https://www.comfy.org/download) or pass --comfy <folder>"; exit 2 }
    Say "ComfyUI не найден автоматически." "ComfyUI was not found automatically."
    Say "Если ComfyUI ещё не установлен: скачайте Comfy Desktop (https://www.comfy.org/download), установите, запустите один раз, закройте и запустите Install.bat снова." "If ComfyUI is not installed yet: download Comfy Desktop (https://www.comfy.org/download), install it, start it once, close it and run Install.bat again."
    Say "Вставьте путь к папке ComfyUI (где main.py) или к папке Portable (где python_embeded) и нажмите Enter:" "Paste the path to the ComfyUI folder (with main.py) or the Portable folder (with python_embeded) and press Enter:"
    $p = (Read-Host).Trim().Trim('"')
    if (-not $p) { exit 2 }
    Probe-Folder $p
    if ($found.Count -eq 0) { Say "В этой папке ComfyUI с Python не найден." "No ComfyUI with Python found there." }
}

function Ask-OtherPath {
    # returns a ComfyUI found at a path the user pastes, or $null on empty input
    while ($true) {
        Say "Вставьте путь к папке ComfyUI (где main.py) или к папке Portable (где python_embeded) и нажмите Enter:" "Paste the path to the ComfyUI folder (with main.py) or the Portable folder (with python_embeded) and press Enter:" Yellow
        $p = (Read-Host).Trim().Trim('"')
        if (-not $p) { return $null }
        $saved = $script:found
        $script:found = New-Object System.Collections.ArrayList
        Probe-Folder $p
        $new = $script:found
        $script:found = $saved
        if ($new.Count -gt 0) { return $new[0] }
        Say "В этой папке ComfyUI с Python не найден." "No ComfyUI with Python found there." Red
    }
}

$sel = $found[0]
$interactive = -not $comfyArg -and -not ($rest -contains "--yes") -and -not ($pick -ge 1 -and $pick -le $found.Count)
if ($found.Count -eq 1 -and $interactive) {
    Say ("Найдена ComfyUI: " + $sel.Comfy + "   [" + $sel.Label + "]") ("Found ComfyUI: " + $sel.Comfy + "   [" + $sel.Label + "]") Cyan
    Say "Если на компьютере несколько ComfyUI (например, Comfy Desktop и ещё Portable в другой папке), установщик мог найти не ту. Нужна эта - просто нажмите Enter. Нужна другая - вставьте путь к её папке и нажмите Enter." "If you have several ComfyUI on this computer (e.g. Comfy Desktop and a Portable in another folder), the installer may have found the wrong one. This one - just press Enter. Another one - paste the path to its folder and press Enter." Yellow
    $p = (Read-Host).Trim().Trim('"')
    if ($p) {
        $saved = $found; $found = New-Object System.Collections.ArrayList
        Probe-Folder $p
        $new = $found; $found = $saved
        if ($new.Count -gt 0) { $sel = $new[0] } else { Say "В этой папке ComfyUI с Python не найден." "No ComfyUI with Python found there." Red; $o = Ask-OtherPath; if (-not $o) { exit 2 }; $sel = $o }
    }
}
elseif ($found.Count -gt 1) {
    if ($pick -ge 1 -and $pick -le $found.Count) { $sel = $found[$pick - 1] }
    else {
        Say "Найдено несколько ComfyUI - выберите, с какой работать:" "Several ComfyUI found - choose which one to use:" Cyan
        for ($i = 0; $i -lt $found.Count; $i++) { Write-Host ("  {0}) {1}   [{2}]" -f ($i + 1), $found[$i].Comfy, $found[$i].Label) }
        if ($rest -contains "--yes") { Say "Выберите: --pick N" "Choose with --pick N"; exit 2 }
        Say "  0) Другая папка - нужной ComfyUI нет в списке (например, Portable лежит в другом месте)" "  0) Another folder - the ComfyUI you need is not listed (e.g. a Portable stored elsewhere)"
        $q = "Number"; if ($ru) { $q = "Номер" }
        do { $n = Read-Host $q } until ($n -match '^\d+$' -and [int]$n -ge 0 -and [int]$n -le $found.Count)
        if ([int]$n -eq 0) { $o = Ask-OtherPath; if (-not $o) { exit 2 }; $sel = $o }
        else { $sel = $found[[int]$n - 1] }
    }
}

$pyArgs = @("-s", (Join-Path $tools "st_setup.py"), $cmd, "--comfy", $sel.Comfy, "--base", $sel.Base, "--kind", $sel.Kind)
if ($sel.Yaml) { $pyArgs += @("--extra-yaml", $sel.Yaml) }
$pyArgs += $rest
& $sel.Python @pyArgs
exit $LASTEXITCODE
