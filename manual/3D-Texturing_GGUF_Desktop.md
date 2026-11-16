# 3D-Texturing_GGUF — Comfy Desktop

**Русский** · [English](#english)

У вас Portable? → [3D-Texturing_GGUF_Portable](3D-Texturing_GGUF_Portable.md)

## 1. Скачайте модели по ссылкам (11.2 GB)

| Файл | Положить в |
|---|---|
| [flux-2-klein-base-9b-Q4_0.gguf](https://huggingface.co/unsloth/FLUX.2-klein-base-9B-GGUF/resolve/main/flux-2-klein-base-9b-Q4_0.gguf) | `C:\Users\<имя пользователя>\AppData\Local\Comfy-Desktop\ComfyUI-Shared\models\diffusion_models` |
| [Qwen3-8B-Q4_K_M.gguf](https://huggingface.co/unsloth/Qwen3-8B-GGUF/resolve/main/Qwen3-8B-Q4_K_M.gguf) | `C:\Users\<имя пользователя>\AppData\Local\Comfy-Desktop\ComfyUI-Shared\models\text_encoders` |
| [flux2-vae.safetensors](https://huggingface.co/Comfy-Org/flux2-dev/resolve/main/split_files/vae/flux2-vae.safetensors) | `C:\Users\<имя пользователя>\AppData\Local\Comfy-Desktop\ComfyUI-Shared\models\vae` |
| [dit_lora.safetensors](https://www.modelscope.ai/models/Yibo-Zhang/UltraTex/resolve/master/flux2/lora/dit_lora.safetensors) → переименовать в `ultratex_flux2.safetensors` | `C:\Users\<имя пользователя>\AppData\Local\Comfy-Desktop\ComfyUI-Shared\models\loras` |
| [decoder.pt](https://www.modelscope.ai/models/Yibo-Zhang/UltraTex/resolve/master/flux2/decoder.pt) → переименовать в `ultratex_flux2_decoder.pt` | `C:\Users\<имя пользователя>\AppData\Local\Comfy-Desktop\ComfyUI-Shared\models\ultratex` (создайте папку) |
| [birefnet.safetensors](https://huggingface.co/Comfy-Org/BiRefNet/resolve/main/background_removal/birefnet.safetensors) | `C:\Users\<имя пользователя>\AppData\Local\Comfy-Desktop\ComfyUI-Shared\models\background_removal` |

## 2. Скачайте ноды

- [s_tools](https://github.com/sofiakholina/sofiakholina-s_tools/archive/refs/heads/main.zip) → распакуйте, назовите папку `s_tools` и положите в `C:\Users\<имя пользователя>\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\custom_nodes`
- [comfyui_ultratex_modular](https://codeload.github.com/Mstafa-awad/UltraTex-ComfyUI-nodes/zip/8d434a2104be520ea699a9baac2327d124387111) → распакуйте, назовите папку `comfyui_ultratex_modular` и положите в `C:\Users\<имя пользователя>\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\custom_nodes`
- [ComfyUI-GGUF](https://cdn.comfy.org/city96/ComfyUI-GGUF/1.1.10/node.zip) → распакуйте, назовите папку `ComfyUI-GGUF` и положите в `C:\Users\<имя пользователя>\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\custom_nodes`

**Важно (!): внутри каждой папки сразу должен быть набор файлов, а не ещё одна папка.**

## 3. Установите дополнительные компоненты

Закройте ComfyUI. Win + R → в поле введите `cmd` → Enter. Вставляйте команды по одной (правая кнопка мыши) и нажимайте Enter.

**Библиотеки Python, без которых ноды не запустятся:**
```
"%LOCALAPPDATA%\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe" -m pip install trimesh moderngl glcontext "gguf>=0.13"
```

**Triton** (ускоряет). Сначала узнайте версию torch:
```
"%LOCALAPPDATA%\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe" -c "import torch; print(torch.__version__)"
```
Ответ начинается с `2.12` или `2.13` — установите Triton:
```
"%LOCALAPPDATA%\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe" -m pip install -U "triton-windows<3.8"
```
<details><summary>Если у вас другая версия torch</summary>

Замените в команде установки `<3.8`:

| torch | вместо `<3.8` |
|---|---|
| 2.14 | `<3.9` |
| 2.15 | `<3.10` |
| 2.10, 2.11 | `<3.7` |
| 2.9 | `<3.6` |
| 2.8 | `<3.5` |
| 2.7 | `<3.4` |
| 2.6 | `<3.3` |

Версии нет в таблице — Triton не ставьте. После обновления ComfyUI версия torch может смениться — проверьте снова.
</details>

<details><summary>Удалить Triton</summary>

```
"%LOCALAPPDATA%\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe" -m pip uninstall -y triton-windows
```
</details>

Comfy Desktop установлен не по умолчанию — замените в путях `%LOCALAPPDATA%\Comfy-Desktop\...` на свои.

## 4. Запуск

1. Нажмите на [3D-Texturing_GGUF.json](https://github.com/sofiakholina/sofiakholina-3D-Texturing/blob/main/workflows/3D-Texturing_GGUF.json).
2. Справа над текстом файла нажмите значок скачивания (стрелка вниз, подсказка «Download raw file»).
3. Запустите ComfyUI и перетащите скачанный файл в его окно.

Первая генерация дольше обычного.

---

<a name="english"></a>
# 3D-Texturing_GGUF — Comfy Desktop

Using Portable? → [3D-Texturing_GGUF_Portable](3D-Texturing_GGUF_Portable.md#english)

## 1. Download the models (11.2 GB)

| File | Put into |
|---|---|
| [flux-2-klein-base-9b-Q4_0.gguf](https://huggingface.co/unsloth/FLUX.2-klein-base-9B-GGUF/resolve/main/flux-2-klein-base-9b-Q4_0.gguf) | `C:\Users\<user name>\AppData\Local\Comfy-Desktop\ComfyUI-Shared\models\diffusion_models` |
| [Qwen3-8B-Q4_K_M.gguf](https://huggingface.co/unsloth/Qwen3-8B-GGUF/resolve/main/Qwen3-8B-Q4_K_M.gguf) | `C:\Users\<user name>\AppData\Local\Comfy-Desktop\ComfyUI-Shared\models\text_encoders` |
| [flux2-vae.safetensors](https://huggingface.co/Comfy-Org/flux2-dev/resolve/main/split_files/vae/flux2-vae.safetensors) | `C:\Users\<user name>\AppData\Local\Comfy-Desktop\ComfyUI-Shared\models\vae` |
| [dit_lora.safetensors](https://www.modelscope.ai/models/Yibo-Zhang/UltraTex/resolve/master/flux2/lora/dit_lora.safetensors) → rename to `ultratex_flux2.safetensors` | `C:\Users\<user name>\AppData\Local\Comfy-Desktop\ComfyUI-Shared\models\loras` |
| [decoder.pt](https://www.modelscope.ai/models/Yibo-Zhang/UltraTex/resolve/master/flux2/decoder.pt) → rename to `ultratex_flux2_decoder.pt` | `C:\Users\<user name>\AppData\Local\Comfy-Desktop\ComfyUI-Shared\models\ultratex` (create the folder) |
| [birefnet.safetensors](https://huggingface.co/Comfy-Org/BiRefNet/resolve/main/background_removal/birefnet.safetensors) | `C:\Users\<user name>\AppData\Local\Comfy-Desktop\ComfyUI-Shared\models\background_removal` |

## 2. Download the nodes

- [s_tools](https://github.com/sofiakholina/sofiakholina-s_tools/archive/refs/heads/main.zip) → unzip, name the folder `s_tools` and put it into `C:\Users\<user name>\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\custom_nodes`
- [comfyui_ultratex_modular](https://codeload.github.com/Mstafa-awad/UltraTex-ComfyUI-nodes/zip/8d434a2104be520ea699a9baac2327d124387111) → unzip, name the folder `comfyui_ultratex_modular` and put it into `C:\Users\<user name>\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\custom_nodes`
- [ComfyUI-GGUF](https://cdn.comfy.org/city96/ComfyUI-GGUF/1.1.10/node.zip) → unzip, name the folder `ComfyUI-GGUF` and put it into `C:\Users\<user name>\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\custom_nodes`

**Important: the files must be directly inside each folder, not in another nested folder.**

## 3. Install additional components

Close ComfyUI. Win + R → type `cmd` in the field → Enter. Paste the commands one by one (right mouse button) and press Enter.

**Python libraries the nodes need to run:**
```
"%LOCALAPPDATA%\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe" -m pip install trimesh moderngl glcontext "gguf>=0.13"
```

**Triton** (speeds it up). First check your torch version:
```
"%LOCALAPPDATA%\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe" -c "import torch; print(torch.__version__)"
```
The answer starts with `2.12` or `2.13` — install Triton:
```
"%LOCALAPPDATA%\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe" -m pip install -U "triton-windows<3.8"
```
<details><summary>If you have another torch version</summary>

Replace `<3.8` in the install command:

| torch | instead of `<3.8` |
|---|---|
| 2.14 | `<3.9` |
| 2.15 | `<3.10` |
| 2.10, 2.11 | `<3.7` |
| 2.9 | `<3.6` |
| 2.8 | `<3.5` |
| 2.7 | `<3.4` |
| 2.6 | `<3.3` |

Not in the table — do not install Triton. After a ComfyUI update the torch version may change — check again.
</details>

<details><summary>Remove Triton</summary>

```
"%LOCALAPPDATA%\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe" -m pip uninstall -y triton-windows
```
</details>

Comfy Desktop not in the default location — replace `%LOCALAPPDATA%\Comfy-Desktop\...` in the paths with yours.

## 4. Run

1. Click [3D-Texturing_GGUF.json](https://github.com/sofiakholina/sofiakholina-3D-Texturing/blob/main/workflows/3D-Texturing_GGUF.json).
2. Above the file text on the right, click the download icon (down arrow, tooltip "Download raw file").
3. Start ComfyUI and drag the downloaded file into its window.

The first generation takes longer.
