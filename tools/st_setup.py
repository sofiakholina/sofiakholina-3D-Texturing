"""Installer for sofiakholina ComfyUI workflow packs (runs in ComfyUI's own Python).

Commands: install (default), uninstall, check.
Everything third-party is pinned in manifest.json (tested versions only).
Standard library only; torch / psutil / folder_paths are used when present.
"""
import argparse
import ctypes
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
PIN_FILE = ".sofiakholina_pin.json"
STATE_NAME = "sofiakholina_install.json"
UA = {"User-Agent": "sofiakholina-installer/1.0"}

# ------------------------------------------------------------------ language / output
def _ui_lang():
    try:
        lid = ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF
        return "ru" if lid in (0x19, 0x22, 0x23, 0x3F) else "en"  # ru, uk, be, kk
    except Exception:
        return "en"

LANG = "en"
T = {
    "title": ("Установка: {name} {ver}", "Installing: {name} {ver}"),
    "uninstall_title": ("Удаление: {name}", "Uninstalling: {name}"),
    "check_title": ("Проверка: {name}", "Check: {name}"),
    "comfy": ("ComfyUI: {p}", "ComfyUI: {p}"),
    "log": ("Журнал: {p}", "Log: {p}"),
    "running": ("ComfyUI сейчас запущен. Закройте его и нажмите Enter.", "ComfyUI is running. Close it and press Enter."),
    "still_running": ("ComfyUI всё ещё запущен - остановлено.", "ComfyUI is still running - stopped."),
    "newer": ("Есть новая версия установщика ({v}): {url}", "A newer installer is available ({v}): {url}"),
    "step": ("[{n}] {t}", "[{n}] {t}"),
    "s_env": ("ComfyUI, Python, видеокарта", "ComfyUI, Python, GPU"),
    "s_nodes": ("Ноды", "Nodes"),
    "s_pip": ("Python-пакеты", "Python packages"),
    "s_triton": ("Triton", "Triton"),
    "s_models": ("Модели", "Models"),
    "s_wf": ("Workflow", "Workflows"),
    "comfy_ver": ("ComfyUI {v} (проверено на {t})", "ComfyUI {v} (tested: {t})"),
    "comfy_old": ("ComfyUI старше проверенной версии - обновите ComfyUI, иначе часть нод workflow может не найтись. {how}",
                  "ComfyUI is older than the tested version - update it, or some workflow nodes may be missing. {how}"),
    "upd_desktop": ("Comfy Desktop: обновление ComfyUI в настройках приложения.", "Comfy Desktop: update ComfyUI in the app settings."),
    "upd_portable": ("Portable: запустите update\\update_comfyui.bat в папке ComfyUI_windows_portable.", "Portable: run update\\update_comfyui.bat in the ComfyUI_windows_portable folder."),
    "upd_other": ("Обновите ComfyUI так, как вы его устанавливали.", "Update ComfyUI the way you installed it."),
    "comfy_new": ("ComfyUI новее проверенной версии - обычно работает, но не проверено.",
                  "ComfyUI is newer than the tested version - usually fine, but untested."),
    "py": ("Python {py} / torch {torch} / CUDA {cuda}", "Python {py} / torch {torch} / CUDA {cuda}"),
    "gpu": ("Видеокарта: {g} ({v:.1f} GB)", "GPU: {g} ({v:.1f} GB)"),
    "cpu_torch": ("В выбранной установке ComfyUI стоит PyTorch для CPU. Для этих workflow нужен PyTorch с CUDA.",
                  "The selected ComfyUI installation uses CPU-only PyTorch. These workflows need PyTorch with CUDA."),
    "no_cuda_torch": ("PyTorch в выбранной установке ComfyUI не поддерживает CUDA. Нужна сборка PyTorch для NVIDIA.",
                      "PyTorch in the selected ComfyUI installation has no CUDA support. A PyTorch build for NVIDIA is required."),
    "cuda_gpu_unavailable": ("PyTorch с CUDA {v} установлен, но не может использовать видеокарту NVIDIA.",
                             "PyTorch with CUDA {v} is installed but cannot use an NVIDIA GPU."),
    "cuda_driver_hint": ("Проверьте, видит ли команда nvidia-smi видеокарту, и обновите драйвер NVIDIA при необходимости.",
                         "Run nvidia-smi to check whether the GPU is detected and update the NVIDIA driver if needed."),
    "cuda_install_retry": ("После исправления закройте ComfyUI, снова запустите Install.bat и выберите установку с NVIDIA.",
                           "After fixing this, close ComfyUI, run Install.bat again, and select the NVIDIA installation."),
    "no_torch": ("PyTorch не загружается в этом Python: {e}", "PyTorch does not load in this Python: {e}"),
    "ask_group": ("{q} [Y/N, Enter = {d}]: ", "{q} [Y/N, Enter = {d}]: "),
    "ok": ("[OK]      {m}", "[OK]      {m}"),
    "warn": ("[ВНИМАНИЕ] {m}", "[WARN]    {m}"),
    "fail": ("[ОШИБКА]  {m}", "[FAIL]    {m}"),
    "get": ("[СКАЧИВАЮ] {m}", "[GET]     {m}"),
    "node_ok": ("{n}: проверенная версия {r}", "{n}: tested version {r}"),
    "node_other": ("{n}: найдена другая версия в {p}", "{n}: another version found in {p}"),
    "node_replace": ("Заменить на проверенную версию? Старая будет сохранена в резервную копию", "Replace it with the tested version? The old one is backed up"),
    "node_kept": ("{n}: оставлена как есть (не проверенная версия)", "{n}: left as is (untested version)"),
    "node_dup": ("{n}: найдено несколько копий ({p}) - удалите лишние, две копии конфликтуют", "{n}: several copies found ({p}) - remove the extra ones, two copies conflict"),
    "node_inst": ("{n}: установлена версия {r}", "{n}: installed version {r}"),
    "backup": ("Резервная копия: {p}", "Backup: {p}"),
    "pip_ok": ("пакеты {n}", "packages for {n}"),
    "pip_fail": ("пакеты {n} не установились (см. журнал)", "packages for {n} failed (see log)"),
    "hdr_ok": ("добавлены файлы Python для Triton (include, libs) в {p}", "added Python files for Triton (include, libs) to {p}"),
    "hdr_none": ("нет файлов include/libs для Python {v} - Triton может не работать", "no include/libs for Python {v} - Triton may not work"),
    "hdr_fail": ("не удалось добавить include/libs: {e}", "could not add include/libs: {e}"),
    "triton_ok": ("Triton {v} работает", "Triton {v} works"),
    "triton_inst": ("ставлю Triton ({s})", "installing Triton ({s})"),
    "triton_bad": ("Triton не работает: {e}", "Triton does not work: {e}"),
    "triton_auto": ("torch {t} новее проверенных - подбираю Triton автоматически", "torch {t} is newer than tested - picking Triton automatically"),
    "triton_auto_ok": ("Triton {v} подобран автоматически для torch {t}, не проверено", "Triton {v} picked automatically for torch {t}, not tested"),
    "triton_unknown": ("для torch {t} нет проверенной версии Triton - пропускаю", "no known Triton for torch {t} - skipped"),
    "triton_need": ("GGUF-версии без Triton не запустятся", "the GGUF versions will not run without Triton"),
    "triton_slow": ("без Triton workflow работают, но медленнее", "without Triton the workflows run, but slower"),
    "m_have": ("{n}", "{n}"),
    "m_size": ("{n}: размер отличается от проверенного файла ({a} вместо {b} байт) - оставлен как есть", "{n}: size differs from the tested file ({a} vs {b} bytes) - left as is"),
    "m_missing": ("нет: {n} ({s})", "missing: {n} ({s})"),
    "m_ask": ("Скачать недостающие модели ({s}) в {p}?", "Download the missing models ({s}) to {p}?"),
    "m_sub": ("{n} найден в подпапке: {p} - в workflow выберите его в ноде загрузки вручную (или переместите файл на уровень выше)",
              "{n} found in a subfolder: {p} - pick it in the loader node manually (or move the file one level up)"),
    "m_manual": ("Можно скачать вручную: {u} -> {p}", "Manual download: {u} -> {p}"),
    "m_space": ("Недостаточно места на диске {d}: нужно {n}, свободно {f}", "Not enough space on {d}: need {n}, free {f}"),
    "m_skip": ("модели не скачаны - их можно докачать, запустив установщик ещё раз", "models skipped - run the installer again to download them"),
    "m_done": ("{n} -> {p}", "{n} -> {p}"),
    "m_fail": ("{n}: не скачалось ({e}) - запустите установщик ещё раз, загрузка продолжится", "{n}: download failed ({e}) - run again to resume"),
    "wf_ok": ("{n}", "{n}"),
    "wf_dir": ("Workflow: {p}", "Workflows: {p}"),
    "summary": ("ИТОГ", "SUMMARY"),
    "sum_ok": ("Всё установлено", "Everything installed"),
    "sum_warn": ("Предупреждений: {n} (см. выше)", "Warnings: {n} (see above)"),
    "sum_fail": ("Ошибок: {n} - исправьте и запустите установщик ещё раз", "Errors: {n} - fix them and run again"),
    "next": ("Дальше: запустите ComfyUI, workflow - в левой панели, Рабочие процессы (клавиша W). Проверить, что все ноды загрузились: запустите Check.bat при открытом ComfyUI.",
             "Next: start ComfyUI, the workflows are in the left sidebar, Workflows (W key). To verify all nodes loaded, run Check.bat while ComfyUI is open."),
    "u_nothing": ("Этот набор не установлен этим установщиком - удалять нечего.", "This pack was not installed by this installer - nothing to remove."),
    "u_wf": ("Удалены workflow", "Workflows removed"),
    "u_pip_kept": ("Python-пакеты оставлены - они нужны ComfyUI или другим нодам: {p}", "Python packages kept - ComfyUI or other nodes need them: {p}"),
    "u_pip": ("Python-пакеты, установленные установщиком, удалены: {p}", "Python packages installed by the installer removed: {p}"),
    "u_models_ask": ("Удалить скачанные установщиком модели ({s})? Их могут использовать другие workflow", "Remove the models this installer downloaded ({s})? Other workflows may use them"),
    "u_removed": ("в Корзину: {p}", "to Recycle Bin: {p}"),
    "u_kept": ("оставлено: {p}", "kept: {p}"),
    "u_shared": ("{n} нужен другому набору ({o}) - оставлен", "{n} is needed by another pack ({o}) - kept"),
    "u_pip_fail": ("Python-пакеты не удалились (см. журнал): {p}", "Python packages were not removed (see log): {p}"),
    "u_recycle_fail": ("не удалось переместить в Корзину - удалите вручную: {p}", "could not move to the Recycle Bin - delete it manually: {p}"),
    "node_noid": ("{n}: в {p} лежит папка с другим содержимым - перенесена в резервную копию", "{n}: {p} holds a folder with other content - moved to a backup"),
    "c_models_size": ("{w}: размер не совпадает с проверенным: {n} - удалите файл и запустите Install.bat (скачает заново)", "{w}: size differs from the tested file: {n} - delete it and run Install.bat (downloads it again)"),
    "u_done": ("Удаление завершено.", "Uninstall finished."),
    "c_server": ("ComfyUI не отвечает на {u}. Запустите ComfyUI и запустите Check.bat ещё раз.", "ComfyUI does not answer at {u}. Start ComfyUI and run Check.bat again."),
    "c_other": ("На этом порту запущен другой ComfyUI ({p}) - закройте его и запустите нужный.", "Another ComfyUI is running on this port ({p}) - close it and start the right one."),
    "c_device_unknown": ("ComfyUI не сообщил, какое устройство использует.", "ComfyUI did not report which device it is using."),
    "c_device": ("Устройство ComfyUI: {d} (PyTorch {v})", "ComfyUI device: {d} (PyTorch {v})"),
    "c_device_cpu": ("ComfyUI запущен на CPU (PyTorch {v}). Генерация может идти очень медленно.", "ComfyUI is running on the CPU (PyTorch {v}). Generation can be very slow."),
    "c_cpu_flag_desktop": ("Уберите --cpu в Startup Arguments выбранной установки.", "Remove --cpu from Startup Arguments for this installation."),
    "c_cpu_flag_other": ("Уберите --cpu из команды запуска ComfyUI.", "Remove --cpu from the ComfyUI launch command."),
    "c_cpu_desktop": ("На карточке PyTorch выберите сборку CUDA. Если в списке только CPU, на главном экране создайте New Instance и выберите Hardware → NVIDIA.", "Select a CUDA build on the PyTorch card. If the list shows only CPU builds, create a New Instance from the home screen and select Hardware → NVIDIA."),
    "c_cpu_desktop_legacy": ("Создайте в Comfy Desktop установку с Hardware → NVIDIA.", "Create a Comfy Desktop installation with Hardware → NVIDIA."),
    "c_cpu_portable": ("Используйте ComfyUI Portable для NVIDIA и запускайте его через run_nvidia_gpu.bat.", "Use ComfyUI Portable for NVIDIA and start it with run_nvidia_gpu.bat."),
    "c_cpu_other": ("Установите CUDA-сборку PyTorch в Python этой установки ComfyUI.", "Install a CUDA build of PyTorch in this ComfyUI installation's Python environment."),
    "c_cpu_retry": ("Запустите ComfyUI на NVIDIA, затем снова запустите Check.bat и выберите эту установку.", "Start ComfyUI on NVIDIA, then run Check.bat again and select that installation."),
    "c_nodes_ok": ("{w}: все ноды на месте", "{w}: all nodes loaded"),
    "c_nodes_miss": ("{w}: не загрузились ноды {n}", "{w}: nodes not loaded: {n}"),
    "c_models_miss": ("{w}: нет моделей {n}", "{w}: missing models {n}"),
    "c_models_ok": ("{w}: все модели на месте", "{w}: all models found"),
    "press": ("Нажмите Enter для выхода...", "Press Enter to exit..."),
    "wf_which": ("Какие workflow установить?", "Which workflows to install?"),
    "wf_item": ("{i}. {w}{h}", "{i}. {w}{h}"),
    "gguf_hint": (" (для 6-8 GB VRAM)", " (for 6-8 GB VRAM)"),
    "pick": ("Номера через пробел, 0 - все, Enter - рекомендуемые для вашей видеокарты ({d}): ", "Numbers separated by spaces, 0 - all, Enter - recommended for your GPU ({d}): "),
    "pick_all": ("Номера через пробел, Enter - все: ", "Numbers separated by spaces, Enter - all: "),
    "pick_bad": ("Не понял ответ, введите номера из списка", "Could not read the answer, enter numbers from the list"),
    "picked": ("Будут установлены: {w}", "Will be installed: {w}"),
}

def t(key, **kw):
    ru, en = T[key]
    return (ru if LANG == "ru" else en).format(**kw)

class Log:
    def __init__(self, path):
        self.f = open(path, "a", encoding="utf-8")
        self.warns = 0
        self.fails = 0
    def __call__(self, msg="", color=None):
        # color only on screen; the log file stays plain text
        print(f"\033[{COLORS[color]}m{msg}\033[0m" if color else msg, flush=True)
        self.f.write(msg + "\n")
        self.f.flush()
    def ok(self, m): self("    " + t("ok", m=m), "ok")
    def warn(self, m):
        self.warns += 1
        self("    " + t("warn", m=m), "warn")
    def fail(self, m):
        self.fails += 1
        self("    " + t("fail", m=m), "fail")
    def raw(self, text):
        self.f.write(text + "\n")
        self.f.flush()

COLORS = {"ok": "92", "warn": "93", "fail": "91", "head": "96;1", "ask": "97;1"}
LOG = None
ARGS = None
SAVE = lambda: None   # saves the install state; set in cmd_install so an interrupted run can still be uninstalled

def ask(question, default=True, key=None):
    """Y/N question. --yes answers with the default; --set key=y/n answers a named question."""
    if key and key in ARGS.answers:
        ans = ARGS.answers[key]
        LOG(f"    {question} -> {'Y' if ans else 'N'} (--set)")
        return ans
    if ARGS.yes:
        LOG(f"    {question} -> {'Y' if default else 'N'} (--yes)")
        return default
    d = "Y" if default else "N"
    while True:
        r = input("\033[97;1m    " + t("ask_group", q=question, d=d) + "\033[0m").strip().lower()
        if not r:
            return default
        if r[0] in "yд":
            return True
        if r[0] in "nн":
            return False

def human(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024.0

# ------------------------------------------------------------------ helpers
def version_tuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", str(v))[:3])

def download(url, target, expected=None, progress=True):
    """HTTP download with resume (.part) and size check."""
    part = target + ".part"
    have = os.path.getsize(part) if os.path.exists(part) else 0
    if expected and have > expected:
        os.remove(part)
        have = 0
    if expected and have == expected:   # finished earlier, interrupted before the rename
        os.replace(part, target)
        return
    headers = dict(UA)
    if have:
        headers["Range"] = f"bytes={have}-"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        mode = "ab" if have and r.status == 206 else "wb"
        done = have if mode == "ab" else 0
        total = expected or (int(r.headers.get("Content-Length", 0)) + done)
        last = 0
        with open(part, mode) as f:
            while True:
                chunk = r.read(8 << 20)
                if not chunk:
                    break
                f.write(chunk)
                done += len(chunk)
                if progress and total and time.time() - last > 0.5:
                    last = time.time()
                    print(f"\r      {done / 1024 ** 3:6.2f} / {total / 1024 ** 3:6.2f} GB", end="", flush=True)
    if progress:
        print()
    if expected and os.path.getsize(part) != expected:
        raise RuntimeError(f"size {os.path.getsize(part)} != {expected}")
    os.replace(part, target)

def fetch_json(url, timeout=15):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def recycle(path):
    """Moves a file or folder to the Windows Recycle Bin. On Windows never deletes permanently:
    if the Recycle Bin move fails, the file stays and False is returned."""
    if not os.path.exists(path):
        return True
    if os.name == "nt":
        class SHFILEOPSTRUCTW(ctypes.Structure):
            _fields_ = [("hwnd", ctypes.c_void_p), ("wFunc", ctypes.c_uint), ("pFrom", ctypes.c_wchar_p),
                        ("pTo", ctypes.c_wchar_p), ("fFlags", ctypes.c_ushort), ("fAnyOperationsAborted", ctypes.c_int),
                        ("hNameMappings", ctypes.c_void_p), ("lpszProgressTitle", ctypes.c_wchar_p)]
        op = SHFILEOPSTRUCTW(None, 3, os.path.abspath(path) + "\0\0", None, 0x40 | 0x10 | 0x04 | 0x400, 0, None, None)
        try:
            if ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op)) == 0 and not os.path.exists(path):
                return True
        except Exception as e:
            LOG.raw(f"recycle {path}: {e}")
        LOG.warn(t("u_recycle_fail", p=path))
        return False
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)
    return True

def pip_install(args, constraints):
    cmd = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--no-warn-script-location"]
    if constraints:
        cmd += ["-c", constraints]
    cmd += args
    LOG.raw("$ " + " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    LOG.raw(r.stdout[-4000:] + r.stderr[-4000:])
    return r.returncode == 0

def make_constraints():
    """Keeps torch & co exactly as they are: nothing we install may replace them."""
    from importlib import metadata
    lines = []
    for p in ("torch", "torchvision", "torchaudio", "numpy"):
        try:
            lines.append(f"{p}=={metadata.version(p)}")
        except Exception:
            pass
    path = os.path.join(tempfile.gettempdir(), "sofiakholina_constraints.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path

# ------------------------------------------------------------------ environment
class Env:
    def __init__(self, a):
        self.comfy = os.path.abspath(a.comfy)          # folder with main.py
        self.base = os.path.abspath(a.base or a.comfy)  # folder with custom_nodes / user / models
        self.custom_nodes = os.path.join(self.base, "custom_nodes")
        self.user = os.path.join(self.base, "user")
        self.extra_yaml = [p for p in (a.extra_yaml or []) if p and os.path.isfile(p)]
        own = os.path.join(self.comfy, "extra_model_paths.yaml")
        if os.path.isfile(own) and own not in self.extra_yaml:
            self.extra_yaml.append(own)
        self.kind = a.kind
        self.state_path = os.path.join(self.user, STATE_NAME)

    def comfy_version(self):
        try:
            ns = {}
            exec(open(os.path.join(self.comfy, "comfyui_version.py"), encoding="utf-8").read(), ns)
            return ns["__version__"]
        except Exception:
            return "?"

    def load_state(self):
        try:
            return json.load(open(self.state_path, encoding="utf-8"))
        except Exception:
            return {"packs": {}}

    def save_state(self, st):
        os.makedirs(self.user, exist_ok=True)
        json.dump(st, open(self.state_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

def comfy_running():
    try:
        import psutil
    except Exception:
        return False
    me = os.getpid()
    exe = os.path.normcase(os.path.realpath(sys.executable))
    for p in psutil.process_iter(["pid", "exe", "cmdline"]):
        try:
            if p.info["pid"] == me or not p.info["exe"]:
                continue
            if os.path.normcase(os.path.realpath(p.info["exe"])) == exe and any("main.py" in c for c in (p.info["cmdline"] or [])):
                return True
        except Exception:
            continue
    return False

def torch_info():
    import torch
    cuda = torch.version.cuda or "none"
    gpu, vram = None, 0.0
    if torch.cuda.is_available():
        gpu = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / 1024 ** 3
    return torch.__version__, cuda, gpu, vram

# ------------------------------------------------------------------ nodes
def node_dirs(env, node):
    """Folders in custom_nodes that hold this node pack (by signature files)."""
    out = []
    if not os.path.isdir(env.custom_nodes):
        return out
    for d in sorted(os.listdir(env.custom_nodes)):
        p = os.path.join(env.custom_nodes, d)
        if not os.path.isdir(p) or d.endswith(".disabled") or d.startswith("."):
            continue
        if all(os.path.isfile(os.path.join(p, s)) for s in node["signature"]):
            out.append(p)
    return out

def read_pin(path):
    try:
        return json.load(open(os.path.join(path, PIN_FILE), encoding="utf-8"))
    except Exception:
        return None

CODE_EXT = {".py", ".js", ".css", ".html", ".glsl"}
IGNORE = {"__pycache__", ".git", ".github", PIN_FILE, ".tracking", ".cache"}

def tree_hashes(root):
    out = {}
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in IGNORE]
        for f in files:
            if f in IGNORE or os.path.splitext(f)[1].lower() not in CODE_EXT:
                continue
            p = os.path.join(d, f)
            out[os.path.relpath(p, root).replace("\\", "/")] = hashlib.md5(open(p, "rb").read()).hexdigest()
    return out

def fetch_node(node, tmp):
    z = os.path.join(tmp, "node.zip")
    download(node["url"], z, progress=False)
    with zipfile.ZipFile(z) as zf:
        zf.extractall(os.path.join(tmp, "x"))
    src = os.path.join(tmp, "x")
    items = os.listdir(src)
    if len(items) == 1 and os.path.isdir(os.path.join(src, items[0])):
        src = os.path.join(src, items[0])
    return src

def write_pin(path, node):
    json.dump({"ref": node["ref"], "url": node["url"], "installed": datetime.datetime.now().isoformat(timespec="seconds")},
              open(os.path.join(path, PIN_FILE), "w", encoding="utf-8"))

def backup_folder(env, cur):
    bdir = os.path.join(env.base, "sofiakholina_backup")
    os.makedirs(bdir, exist_ok=True)
    dst = os.path.join(bdir, os.path.basename(cur) + "_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    k = 1
    while os.path.exists(dst):
        k += 1
        dst = dst.rsplit("~", 1)[0] + f"~{k}"
    shutil.move(cur, dst)
    LOG(f"    {t('backup', p=dst)}")
    return dst

def install_node(env, node, state_pack):
    name, ref = node["name"], node["ref"]
    found = node_dirs(env, node)
    if len(found) > 1:
        LOG.warn(t("node_dup", n=name, p=", ".join(os.path.basename(f) for f in found)))
    used = state_pack.setdefault("used_nodes", [])
    if found:
        pin = read_pin(found[0])
        if pin and pin.get("ref") == ref:
            LOG.ok(t("node_ok", n=name, r=node["label"]))
            if found[0] not in used:
                used.append(found[0])
            return True
    tmp = tempfile.mkdtemp(prefix="sk_node_")
    try:
        src = fetch_node(node, tmp)
        target = os.path.join(env.custom_nodes, node["folder"])
        if found:
            cur = found[0]
            if tree_hashes(cur) == tree_hashes(src):   # same files, installed another way
                write_pin(cur, node)
                LOG.ok(t("node_ok", n=name, r=node["label"]))
                if cur not in used:
                    used.append(cur)
                return True
            LOG(f"    {t('node_other', n=name, p=cur)}")
            if not ask(t("node_replace"), True, key="replace_nodes"):
                LOG.warn(t("node_kept", n=name))
                return True
            backup_folder(env, cur)
            target = cur                                 # keep the user's folder name
        os.makedirs(env.custom_nodes, exist_ok=True)
        if os.path.exists(target):                       # same name, but not this pack (old or broken copy): never delete it
            LOG.warn(t("node_noid", n=name, p=target))
            backup_folder(env, target)
        shutil.copytree(src, target)
        write_pin(target, node)
        LOG.ok(t("node_inst", n=name, r=node["label"]))
        if not found:
            state_pack.setdefault("created_nodes", [])
            if target not in state_pack["created_nodes"]:
                state_pack["created_nodes"].append(target)
        if target not in used:
            used.append(target)
        return True
    except Exception as e:
        LOG.fail(f"{name}: {e}")
        return False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def installed_dists():
    """Installed packages, read by pip in a fresh process (importlib.metadata in this process can return a stale list)."""
    r = subprocess.run([sys.executable, "-m", "pip", "list", "--format=json", "--disable-pip-version-check"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode == 0:
        try:
            return {re.sub(r"[-_.]+", "-", x["name"].strip().lower()) for x in json.loads(r.stdout)}
        except Exception as e:
            LOG.raw(f"pip list: {e}")
    LOG.raw("pip list failed: " + r.stderr[-1000:])
    from importlib import metadata
    out = set()
    for d in metadata.distributions():
        n = (d.metadata["Name"] or "").strip()
        if n:
            out.add(re.sub(r"[-_.]+", "-", n.lower()))
    return out

def _norm(n):
    return re.sub(r"[-_.]+", "-", n.strip().lower())

def _req_name(line):
    m = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", line.split("#")[0])
    return _norm(m.group(1)) if m else None

def still_needed(env, pkgs):
    """Of pkgs, those still needed: listed in ComfyUI's or any remaining node's requirements.txt,
    or required (directly or through other kept packages) by an installed package outside pkgs."""
    from importlib import metadata
    need = set()
    files = [os.path.join(env.comfy, "requirements.txt")]
    if os.path.isdir(env.custom_nodes):
        files += [os.path.join(env.custom_nodes, d, "requirements.txt") for d in os.listdir(env.custom_nodes)]
    for f in files:
        if os.path.isfile(f):
            for line in open(f, encoding="utf-8", errors="replace"):
                n = _req_name(line)
                if n in pkgs:
                    need.add(n)
    reqs = {}
    for d in metadata.distributions():
        name = _norm(d.metadata["Name"] or "")
        if not name:
            continue
        deps = set()
        for q in d.requires or []:
            if "extra ==" in q.replace(" ", " "):
                continue
            n = _req_name(q)
            if n:
                deps.add(n)
        reqs[name] = deps
    users = {n for n in reqs if n not in pkgs} | need
    changed = True
    while changed:
        changed = False
        for u in list(users):
            for dep in reqs.get(u, ()):
                if dep in pkgs and dep not in need:
                    need.add(dep)
                    users.add(dep)
                    changed = True
    return need

def install_node_pip(env, node, constraints):
    found = node_dirs(env, node)
    if not found:
        return
    reqs = []
    rf = os.path.join(found[0], "requirements.txt")
    if os.path.isfile(rf):
        for line in open(rf, encoding="utf-8", errors="replace"):
            s = line.split("#")[0].strip()
            if s and not re.match(r"^(torch|torchvision|torchaudio)\b", s, re.I):
                reqs.append(s)
    reqs += node.get("pip", [])
    if not reqs:
        return
    if pip_install(reqs, constraints):
        LOG.ok(t("pip_ok", n=node["name"]))
    else:
        LOG.fail(t("pip_fail", n=node["name"]))

# ------------------------------------------------------------------ triton
TRITON_TEST = r'''
import torch, triton, triton.language as tl
@triton.jit
def k(x, y, n, B: tl.constexpr):
    i = tl.program_id(0) * B + tl.arange(0, B)
    m = i < n
    tl.store(y + i, tl.load(x + i, mask=m) * 2, mask=m)
x = torch.arange(64, device="cuda", dtype=torch.float32)
y = torch.empty_like(x)
k[(1,)](x, y, 64, B=64)
assert torch.allclose(y, x * 2)
print(triton.__version__)
'''

def triton_works():
    path = os.path.join(tempfile.gettempdir(), "sofiakholina_triton_test.py")
    open(path, "w", encoding="utf-8").write(TRITON_TEST)
    r = subprocess.run([sys.executable, path], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    LOG.raw(r.stdout[-2000:] + r.stderr[-3000:])
    if r.returncode == 0:
        return True, r.stdout.strip().splitlines()[-1]
    err = (r.stderr.strip().splitlines() or ["?"])[-1]
    return False, err[:200]

def python_headers(man, state_pack):
    """Embedded Python (Portable) has no Include/libs, which Triton needs to compile. Adds them."""
    base = sys.base_prefix
    if os.path.isfile(os.path.join(base, "Include", "Python.h")) or os.path.isfile(os.path.join(base, "include", "Python.h")):
        return
    ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    url = man["triton"].get("include_libs", {}).get(ver)
    if not url:
        LOG.warn(t("hdr_none", v=ver))
        return
    tmp = tempfile.mkdtemp(prefix="sk_inc_")
    try:
        z = os.path.join(tmp, "inc.zip")
        download(url, z, progress=False)
        with zipfile.ZipFile(z) as zf:
            top = sorted({n.split("/")[0] for n in zf.namelist() if n.split("/")[0]})
            new = [x for x in top if not os.path.exists(os.path.join(base, x))]
            zf.extractall(base)
        LOG.ok(t("hdr_ok", p=base))
        state_pack["python_headers_added"] = base
        state_pack["python_headers_paths"] = [os.path.join(base, x) for x in new]
    except Exception as e:
        LOG.warn(t("hdr_fail", e=e))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def setup_triton(man, torch_ver, need, constraints, state_pack):
    if os.name != "nt":
        LOG.warn("Triton: Windows only installer step - skipped")
        return
    python_headers(man, state_pack)
    tv = ".".join(torch_ver.split("+")[0].split(".")[:2])
    ok, info = triton_works()
    table = man["triton"]["by_torch"]
    spec = table.get(tv)
    if ok:
        LOG.ok(t("triton_ok", v=info))
        return
    def key(v):
        return tuple(int(x) for x in v.split("."))
    if spec:
        specs = [spec]
    elif table and key(tv) > max(key(k) for k in table):
        # torch newer than the table: newest Triton first, then older ones, each checked by the test kernel
        LOG.warn(t("triton_auto", t=tv))
        specs = ["triton-windows"] + sorted({v for v in table.values() if "<" in v},
                                            key=lambda v: key(v.split("<")[1]), reverse=True)[:3]
    else:
        LOG.warn(t("triton_unknown", t=tv))
        (LOG.fail if need == "required" else LOG.warn)(t("triton_need" if need == "required" else "triton_slow"))
        return
    for sp in specs:
        LOG(f"    {t('triton_inst', s=sp)}")
        pip_install(["--upgrade", sp], constraints)
        ok, info = triton_works()
        if ok:
            break
    if ok:
        LOG.ok(t("triton_ok", v=info))
        if not spec:
            LOG.warn(t("triton_auto_ok", v=info, t=tv))
        state_pack["triton_installed"] = True
    else:
        LOG.warn(t("triton_bad", e=info))
        (LOG.fail if need == "required" else LOG.warn)(t("triton_need" if need == "required" else "triton_slow"))

# ------------------------------------------------------------------ models
def load_folder_paths(env):
    sys.path.insert(0, env.comfy)
    cwd = os.getcwd()
    os.chdir(env.comfy)
    try:
        import folder_paths
        if env.base != env.comfy:
            folder_paths.base_path = env.base
            folder_paths.models_dir = os.path.join(env.base, "models")
        try:
            from utils.extra_config import load_extra_path_config
            for y in env.extra_yaml:
                load_extra_path_config(y)
        except Exception as e:
            LOG.raw(f"extra_model_paths not read: {e}")
        if "ultratex" not in folder_paths.folder_names_and_paths:
            folder_paths.add_model_folder_path("ultratex", os.path.join(folder_paths.models_dir, "ultratex"))
        return folder_paths
    finally:
        os.chdir(cwd)

def model_paths(fp, folder):
    """All folders ComfyUI searches for this model type; the download target is first.
    Target = the first folder named like the type (diffusion_models, not the legacy unet)."""
    try:
        paths = list(fp.folder_names_and_paths[folder][0])
    except Exception:
        return [os.path.join(fp.models_dir, folder)]
    named = [p for p in paths if os.path.basename(os.path.normpath(p)).lower() == folder.lower()]
    if named:
        paths.remove(named[0])
        paths.insert(0, named[0])
    return paths

def find_model(fp, m):
    for folder in [m["folder"]] + m.get("also_in", []):
        for root in model_paths(fp, folder):
            p = os.path.join(root, m["name"])
            if os.path.isfile(p):
                return p
    return None

def find_in_subfolder(fp, m):
    """Same file in a subfolder: ComfyUI lists it as 'sub/name', so the workflow will not pick it by itself."""
    name = m["name"].lower()
    for folder in [m["folder"]] + m.get("also_in", []):
        for root in model_paths(fp, folder):
            if not os.path.isdir(root):
                continue
            for d, _dirs, files in os.walk(root, followlinks=True):
                if d == root:
                    continue
                for f in files:
                    if f.lower() == name:
                        return os.path.join(d, f)
    return None

def setup_models(env, models, state_pack):
    fp = load_folder_paths(env)
    missing = []
    for m in models:
        p = find_model(fp, m)
        if p:
            size = os.path.getsize(p)
            if m.get("size") and size != m["size"]:
                LOG.warn(t("m_size", n=m["name"], a=size, b=m["size"]))
            else:
                LOG.ok(t("m_have", n=m["name"]))
            state_pack.setdefault("used_models", [])
            if p not in state_pack["used_models"]:
                state_pack["used_models"].append(p)
        else:
            sub = find_in_subfolder(fp, m)
            if sub:
                LOG.warn(t("m_sub", n=m["name"], p=sub))
                continue
            missing.append(m)
            LOG(f"    {t('m_missing', n=m['folder'] + '/' + m['name'], s=human(m['size']))}")
    if not missing:
        return
    total = sum(m["size"] for m in missing)
    first = model_paths(fp, missing[0]["folder"])[0]
    base = os.path.dirname(first.rstrip("\\/"))
    if not ask(t("m_ask", s=human(total), p=base), True, key="models"):
        LOG.warn(t("m_skip"))
        return
    need = {}
    for m in missing:
        root = model_paths(fp, m["folder"])[0]
        drive = os.path.splitdrive(os.path.abspath(root))[0] or root
        need[drive] = need.get(drive, 0) + m["size"]
    for drive, n in need.items():
        probe = drive + os.sep if drive.endswith(":") else drive
        try:
            free = shutil.disk_usage(probe).free
        except Exception:
            continue
        if free < n + (1 << 30):
            LOG.fail(t("m_space", d=drive, n=human(n + (1 << 30)), f=human(free)))
            return
    for m in missing:
        root = model_paths(fp, m["folder"])[0]
        os.makedirs(root, exist_ok=True)
        target = os.path.join(root, m["name"])
        LOG(f"    {t('get', m=m['name'] + ' (' + human(m['size']) + ')')}")
        state_pack.setdefault("models", [])
        if target not in state_pack["models"]:
            state_pack["models"].append(target)
        SAVE()
        err = None
        for url in m["urls"]:
            try:
                download(url, target, m["size"])
                err = None
                break
            except Exception as e:
                err = e
                LOG.raw(f"{url}: {e}")
        if err:
            LOG.fail(t("m_fail", n=m["name"], e=err))
            LOG("              " + t("m_manual", u=m["urls"][0], p=target))
        else:
            LOG.ok(t("m_done", n=m["name"], p=target))

# ------------------------------------------------------------------ workflows
def wf_dir(env, man):
    base = os.path.join(env.user, "default", "workflows")
    return os.path.join(base, man["workflow_folder"]) if man.get("workflow_folder") else base

def setup_workflows(env, man, wfs, state_pack):
    dst = wf_dir(env, man)
    os.makedirs(dst, exist_ok=True)
    for w in wfs:
        src = os.path.join(ROOT, "workflows", w)
        out = os.path.join(dst, w)
        if os.path.isfile(out):
            if open(out, "rb").read() == open(src, "rb").read():
                LOG.ok(t("wf_ok", n=w))
                continue
            shutil.copyfile(out, out + "." + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".bak")
        shutil.copyfile(src, out)
        LOG.ok(t("wf_ok", n=w))
    LOG(f"    {t('wf_dir', p=dst)}")
    state_pack["workflow_dir"] = dst
    known = {w for g in man["groups"] for w in g["workflows"]}
    state_pack["workflows"] = sorted(w for w in set(state_pack.get("workflows", []) + wfs) if w in known)

# ------------------------------------------------------------------ commands
def check_update(man):
    try:
        remote = fetch_json(man["update_url"], timeout=10)
        if version_tuple(remote.get("version", "0")) > version_tuple(man["version"]):
            LOG.warn(t("newer", v=remote["version"], url=man["repo_url"]))
    except Exception as e:
        LOG.raw(f"update check: {e}")

def recommended_workflows(man, vram):
    """Workflows suggested for this GPU: groups made for low VRAM if the card is below their limit, else the others."""
    allw = [w for g in man["groups"] for w in g["workflows"]]
    low = [g for g in man["groups"] if "default_if_vram_below" in g]
    if not low:
        return allw
    small = [g for g in low if vram < g["default_if_vram_below"]]
    groups = small if small else [g for g in man["groups"] if g not in low]
    return [w for g in groups for w in g["workflows"]]

def selected_workflows(man, vram):
    """One numbered menu. Returns (groups, workflows)."""
    allw = [w for g in man["groups"] for w in g["workflows"]]
    rec = recommended_workflows(man, vram)
    if len(allw) > 1:
        LOG("    " + t("wf_which"))
        for i, w in enumerate(allw, 1):
            LOG("      " + t("wf_item", i=i, w=w[:-5], h=t("gguf_hint") if "GGUF" in w else ""))
        same = rec == allw
        prompt = t("pick_all") if same else t("pick", d=" ".join(str(allw.index(w) + 1) for w in rec))
        while True:
            if ARGS.pick is not None:
                r = ARGS.pick
            elif ARGS.yes:
                r = ""
            else:
                r = input("\033[97;1m    " + prompt + "\033[0m")
            r = r.replace(",", " ").split()
            if not r:
                wfs = rec
                break
            try:
                idx = sorted({int(x) for x in r})
                if idx == [0]:
                    wfs = allw
                    break
                if idx and all(1 <= i <= len(allw) for i in idx):
                    wfs = [allw[i - 1] for i in idx]
                    break
            except ValueError:
                pass
            if ARGS.pick is not None or ARGS.yes:
                LOG.fail(t("pick_bad"))
                raise SystemExit(2)
            LOG("    " + t("pick_bad"))
    else:
        wfs = allw
    LOG("    " + t("picked", w=", ".join(w[:-5] for w in wfs)))
    groups = [g for g in man["groups"] if set(g["workflows"]) & set(wfs)]
    return groups, wfs

STEP = [0]

def step(key):
    STEP[0] += 1
    LOG(t("step", n=STEP[0], t=t(key)), "head")

def cmd_install(env, man):
    global SAVE
    st = env.load_state()
    pack = st["packs"].setdefault(man["id"], {})
    SAVE = lambda: env.save_state(st)
    step("s_env")
    if not wait_comfy_closed():
        return
    cv = env.comfy_version()
    LOG(f"    {t('comfy_ver', v=cv, t=man['comfyui_tested'])}")
    if cv != "?" and version_tuple(cv) < version_tuple(man["comfyui_min"]):
        LOG.warn(t("comfy_old", how=t({"comfy-desktop": "upd_desktop", "desktop-legacy": "upd_desktop", "portable": "upd_portable"}.get(env.kind, "upd_other"))))
    elif cv != "?" and version_tuple(cv) > version_tuple(man["comfyui_tested"]):
        LOG(f"    {t('comfy_new')}")
    try:
        tver, cuda, gpu, vram = torch_info()
    except Exception as e:
        LOG.fail(t("no_torch", e=e))
        return
    LOG(f"    {t('py', py=sys.version.split()[0], torch=tver, cuda=cuda)}")
    if not gpu:
        if cuda == "none":
            LOG.fail(t("cpu_torch" if "+cpu" in tver else "no_cuda_torch"))
            setup_hint = {
                "comfy-desktop": "c_cpu_desktop",
                "desktop-legacy": "c_cpu_desktop_legacy",
                "portable": "c_cpu_portable",
            }.get(env.kind, "c_cpu_other")
            LOG("    " + t(setup_hint))
        else:
            LOG.fail(t("cuda_gpu_unavailable", v=cuda))
            LOG("    " + t("cuda_driver_hint"))
        LOG("    " + t("cuda_install_retry"))
        return
    LOG(f"    {t('gpu', g=gpu, v=vram)}")
    groups, wfs = selected_workflows(man, vram)
    gids = [g["id"] for g in groups]
    nodes = [n for n in man["nodes"] if (set(n["workflows"]) & set(wfs) if "workflows" in n else set(n["groups"]) & set(gids))]
    models = []
    for m in man["models"]:
        if set(m["workflows"]) & set(wfs) and m not in models:
            models.append(m)

    LOG()
    step("s_nodes")
    for n in nodes:
        install_node(env, n, pack)
        SAVE()
    LOG()
    step("s_pip")
    before = installed_dists()
    pack["pip_pending_before"] = sorted(before)   # an interrupted run can still be uninstalled
    SAVE()
    constraints = make_constraints()
    for n in nodes:
        install_node_pip(env, n, constraints)
    triton_need = None
    for g in groups:
        tr = g.get("triton")
        if tr == "required" or (tr == "recommended" and triton_need is None):
            triton_need = tr
    if triton_need:
        LOG()
        step("s_triton")
        setup_triton(man, tver, triton_need, constraints, pack)
    added = sorted(installed_dists() - before)
    if added:
        pack["pip_added"] = sorted(set(pack.get("pip_added", [])) | set(added))
    pack.pop("pip_pending_before", None)
    SAVE()
    LOG()
    step("s_models")
    setup_models(env, models, pack)
    LOG()
    step("s_wf")
    setup_workflows(env, man, wfs, pack)
    pack.update({"version": man["version"], "groups": sorted(set(pack.get("groups", []) + gids)),
                 "installed": datetime.datetime.now().isoformat(timespec="seconds")})
    env.save_state(st)

def wait_comfy_closed():
    """False if ComfyUI is still running after the user was asked to close it."""
    while comfy_running():
        if ARGS.yes:
            LOG.fail(t("still_running"))
            return False
        input("\033[93m    " + t("running") + "\033[0m")
        if comfy_running():
            LOG.fail(t("still_running"))
            return False
    return True

def cmd_uninstall(env, man):
    st = env.load_state()
    pack = st["packs"].get(man["id"])
    if not pack:
        LOG(t("u_nothing"))
        return
    if not wait_comfy_closed():
        return
    wdir = pack.get("workflow_dir", wf_dir(env, man))
    for w in pack.get("workflows", []):
        recycle(os.path.join(wdir, w))
    if man.get("workflow_folder"):
        try:
            os.rmdir(wdir)
        except OSError:
            pass
    LOG.ok(t("u_wf"))
    others = {k: v for k, v in st["packs"].items() if k != man["id"]}
    for path in pack.get("created_nodes", []):
        if not os.path.exists(path):
            continue
        users = [k for k, v in others.items() if path in v.get("used_nodes", []) or path in v.get("created_nodes", [])]
        if users:   # another pack still needs it: hand the ownership over
            owner = others[users[0]].setdefault("created_nodes", [])
            if path not in owner:
                owner.append(path)
            LOG(f"    {t('u_shared', n=os.path.basename(path), o=', '.join(users))}")
            continue
        if recycle(path):
            LOG.ok(t("u_removed", p=path))
    pips = set(pack.get("pip_added", []))
    if pack.get("pip_pending_before"):   # install was interrupted during the package step
        try:
            pips |= installed_dists() - set(pack["pip_pending_before"])
        except Exception as e:
            LOG.raw(f"pending packages: {e}")
    if pack.get("triton_installed"):
        pips.add("triton-windows")
    for k, v in others.items():
        keep = pips & (set(v.get("pip_added", [])) | ({"triton-windows"} if v.get("triton_installed") else set()))
        for p in sorted(keep):
            LOG(f"    {t('u_shared', n=p, o=k)}")
        pips -= keep
    if pips:
        try:
            keep = still_needed(env, pips)
        except Exception as e:
            LOG.raw(f"dependency check failed: {e}")
            keep = set(pips)
        if keep:
            LOG(f"    {t('u_pip_kept', p=', '.join(sorted(keep)))}")
        pips -= keep
    if pips:
        r = subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y"] + sorted(pips),
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        LOG.raw(r.stdout[-4000:] + r.stderr[-4000:])
        left = sorted(pips & installed_dists())
        if r.returncode == 0 and not left:
            LOG.ok(t("u_pip", p=", ".join(sorted(pips))))
        else:
            LOG.fail(t("u_pip_fail", p=", ".join(left or sorted(pips))))
    if pack.get("python_headers_paths") and not any(v.get("python_headers_paths") or v.get("triton_installed") for v in others.values()):
        for p in pack["python_headers_paths"]:
            if recycle(p):
                LOG.ok(t("u_removed", p=p))
    models = [x for m in pack.get("models", []) for x in (m, m + ".part") if os.path.isfile(x)]   # .part: interrupted download
    shared = [m for m in models if any(m in v.get("models", []) + v.get("used_models", []) for v in others.values())]
    models = [m for m in models if m not in shared]
    for m in shared:
        o = next(k for k, v in others.items() if m in v.get("models", []) + v.get("used_models", []))
        others[o].setdefault("models", []).append(m)
        LOG(f"    {t('u_shared', n=os.path.basename(m), o=o)}")
    if models:
        total = sum(os.path.getsize(m) for m in models)
        if ask(t("u_models_ask", s=human(total)), False, key="remove_models"):
            for m in models:
                if recycle(m):
                    LOG.ok(t("u_removed", p=m))
    del st["packs"][man["id"]]
    env.save_state(st)
    LOG(t("u_done"))

def same_comfy(env, url, stats):
    """True if the server at url is this ComfyUI (another one may run on the same port)."""
    nc = lambda x: os.path.normcase(os.path.abspath(x))
    try:
        fp = fetch_json(url + "/internal/folder_paths", timeout=10)
        nodes = [nc(x) for x in fp.get("custom_nodes", [])]
        if nodes:
            return nc(os.path.join(env.comfy, "custom_nodes")) in nodes
    except Exception:
        pass
    sysi = stats.get("system", {})
    argv = (sysi.get("argv") or [""])[0]
    if argv and os.path.isabs(argv):
        return nc(argv) == nc(os.path.join(env.comfy, "main.py"))
    # relative argv ("main.py") fits any install: compare what else is known
    return bool(sysi.get("embedded_python")) == (env.kind == "portable") and sysi.get("comfyui_version") == env.comfy_version()

def report_comfy_device(env, stats):
    devices = stats.get("devices") or []
    device = devices[0] if isinstance(devices, list) and devices else None
    device_type = device.get("type") if isinstance(device, dict) else None
    if not device_type:
        LOG.warn(t("c_device_unknown"))
        return

    system = stats.get("system") or {}
    version = system.get("pytorch_version") or "?"
    if device_type != "cpu":
        LOG("    " + t("c_device", d=device.get("name") or device_type, v=version))
        return

    LOG.fail(t("c_device_cpu", v=version))
    forced_cpu = "--cpu" in (system.get("argv") or [])
    if forced_cpu and env.kind != "portable":
        flag_hint = "c_cpu_flag_desktop" if env.kind == "comfy-desktop" else "c_cpu_flag_other"
        LOG("    " + t(flag_hint))
    if not forced_cpu or "+cpu" in version or env.kind == "portable":
        setup_hint = {
            "comfy-desktop": "c_cpu_desktop",
            "desktop-legacy": "c_cpu_desktop_legacy",
            "portable": "c_cpu_portable",
        }.get(env.kind, "c_cpu_other")
        LOG("    " + t(setup_hint))
    LOG("    " + t("c_cpu_retry"))

def cmd_check(env, man):
    urls = [f"http://127.0.0.1:{p}" for p in (ARGS.port or [8188, 8000])]
    info = None
    other = None
    matched_stats = None
    for u in urls:
        try:
            stats = fetch_json(u + "/api/system_stats", timeout=10)
            argv = (stats.get("system", {}).get("argv") or [""])[0]
            same = same_comfy(env, u, stats)
            if not same:
                other = argv
                continue
            matched_stats = stats
            info = fetch_json(u + "/api/object_info", timeout=60)
            break
        except Exception:
            continue
    if info is None and other:
        LOG.warn(t("c_other", p=other))
    if matched_stats is not None:
        report_comfy_device(env, matched_stats)
    st = env.load_state()
    pack = st["packs"].get(man["id"], {})
    known = [w for g in man["groups"] for w in g["workflows"]]
    wfs = [w for w in pack.get("workflows", []) if w in known] or known
    fp = load_folder_paths(env)
    for w in wfs:
        p = os.path.join(ROOT, "workflows", w)
        g = json.load(open(p, encoding="utf-8"))
        sub = {s["id"] for s in g.get("definitions", {}).get("subgraphs", [])}
        nodes = g["nodes"] + [n for s in g.get("definitions", {}).get("subgraphs", []) for n in s["nodes"]]
        types = {n["type"] for n in nodes if n["type"] not in sub and n.get("mode") != 4}
        types -= {"Note", "MarkdownNote", "Reroute", "PrimitiveNode"}
        if info is not None:
            miss = sorted(x for x in types if x not in info)
            (LOG.fail(t("c_nodes_miss", w=w, n=", ".join(miss))) if miss else LOG.ok(t("c_nodes_ok", w=w)))
        mm, bad = [], []
        for m in man["models"]:
            if w not in m["workflows"]:
                continue
            p = find_model(fp, m)
            if not p:
                mm.append(m["name"])
            elif m.get("size") and os.path.getsize(p) != m["size"]:
                bad.append(m["name"])
        if mm:
            LOG.fail(t("c_models_miss", w=w, n=", ".join(mm)))
        if bad:
            LOG.warn(t("c_models_size", w=w, n=", ".join(bad)))
        if not mm and not bad:
            LOG.ok(t("c_models_ok", w=w))
    if info is None:
        LOG.warn(t("c_server", u=" / ".join(urls)))

def main():
    if os.name == "nt":
        os.system("")   # turns on ANSI colors in the Windows console
    global LANG, LOG, ARGS
    ap = argparse.ArgumentParser()
    ap.add_argument("command", nargs="?", default="install", choices=["install", "uninstall", "check"])
    ap.add_argument("--comfy", required=True)
    ap.add_argument("--base")
    ap.add_argument("--extra-yaml", action="append")
    ap.add_argument("--kind", default="manual")
    ap.add_argument("--lang", choices=["ru", "en"])
    ap.add_argument("--yes", action="store_true", help="answer every question with its default")
    ap.add_argument("--set", action="append", default=[], help="answer a named question: key=y|n")
    ap.add_argument("--port", action="append", type=int)
    ap.add_argument("--workflows", dest="pick", help="workflow numbers, e.g. \"1 3\"; 0 - all; empty - recommended")
    ap.add_argument("--no-pause", action="store_true")
    ARGS = ap.parse_args()
    ARGS.answers = {}
    for s in ARGS.set:
        k, _, v = s.partition("=")
        ARGS.answers[k.strip()] = v.strip().lower().startswith(("y", "1", "t", "д"))
    LANG = ARGS.lang or _ui_lang()
    man = json.load(open(os.path.join(TOOLS, "manifest.json"), encoding="utf-8"))
    logs = os.path.join(ROOT, "logs")
    os.makedirs(logs, exist_ok=True)
    LOG = Log(os.path.join(logs, f"{ARGS.command}_{datetime.datetime.now():%Y%m%d_%H%M%S}.log"))
    env = Env(ARGS)
    head = {"install": "title", "uninstall": "uninstall_title", "check": "check_title"}[ARGS.command]
    LOG("=" * 64)
    LOG("  " + t(head, name=man["name"], ver=man["version"]))
    LOG("  " + t("comfy", p=env.comfy + (f"  ({env.kind})" if env.kind else "")))
    LOG("  " + t("log", p=LOG.f.name))
    LOG("=" * 64)
    LOG.raw(f"python={sys.executable} base={env.base} yaml={env.extra_yaml} args={sys.argv[1:]}")
    if ARGS.command != "uninstall":
        check_update(man)
    try:
        {"install": cmd_install, "uninstall": cmd_uninstall, "check": cmd_check}[ARGS.command](env, man)
    except KeyboardInterrupt:
        LOG.fail("cancelled")
    except Exception as e:
        import traceback
        LOG.raw(traceback.format_exc())
        LOG.fail(f"{type(e).__name__}: {e}")
    LOG()
    LOG("=" * 25 + f" {t('summary')} " + "=" * 25, "head")
    if LOG.fails:
        LOG(t("sum_fail", n=LOG.fails), "fail")
    if LOG.warns:
        LOG(t("sum_warn", n=LOG.warns), "warn")
    if not LOG.fails and not LOG.warns:
        LOG(t("sum_ok") if ARGS.command == "install" else "OK", "ok")
    if ARGS.command == "install" and not LOG.fails:
        LOG(t("next"), "head")
    LOG()
    for f in ("sofiakholina_constraints.txt", "sofiakholina_triton_test.py"):
        try:
            os.remove(os.path.join(tempfile.gettempdir(), f))
        except OSError:
            pass
    sys.exit(1 if LOG.fails else 0)

if __name__ == "__main__":
    main()
