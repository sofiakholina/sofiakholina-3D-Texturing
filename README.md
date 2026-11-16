# sofiakholina-3D-Texturing

**Русский** · [English](#english)

**Текстурирование своей 3D-модели по фото в ComfyUI: 4 workflow + установщик.**

Workflow:

- **3D-Texturing - текстура по одному фото**
- **3D-Texturing_MV - текстура по 1-4 фото** (перед, спина, бока)
- **3D-Texturing_GGUF - облегчённая версия для 6-8 GB VRAM**
- **3D-Texturing_MV_GGUF - облегчённая версия для 6-8 GB VRAM**

Workflow GGUF использовать только при 6-8 GB VRAM, на большей VRAM (12+) дают сильное замедление без выигрыша.

**Workflow генерации 3D-модели по изображению здесь:** [sofiakholina-3D-Generation](https://github.com/sofiakholina/sofiakholina-3D-Generation).

## Установка

**Только для Windows, видеокарт NVIDIA с актуальным драйвером (от 6 GB VRAM для GGUF-версий, от 12 GB для остальных) и ComfyUI версии 0.45+. Свободное место на диске: ComfyUI — около 6 GB, модели — около 42 GB для 4-х workflow.**

### Автоматически

1. Установите ComfyUI: [Comfy Desktop](https://www.comfy.org/download), также подойдёт [ComfyUI Portable](https://github.com/Comfy-Org/ComfyUI/releases).
2. Скачайте этот репозиторий: зелёная кнопка **Code** вверху страницы → **Download ZIP**, распакуйте в любую папку. После установки эту папку можно удалить (для Check.bat и Uninstall.bat скачайте архив заново).
3. Закройте ComfyUI.
4. Запустите **Install.bat**. 
Если Windows покажет «Система Windows защитила ваш компьютер» — **Подробнее → Выполнить в любом случае**.
5. Выберите, какие workflow установить (Enter — рекомендуемые для вашей видеокарты), и ответьте, скачивать ли модели. При повторном запуске Install.bat загрузка продолжится с места остановки.
6. Запустите ComfyUI: workflow — в левой панели, **Рабочие процессы** (клавиша W).

Проверка: при открытом ComfyUI запустите **Check.bat** — он покажет, все ли ноды и модели на месте.

**После обновления Comfy Desktop** запустите Install.bat ещё раз.

**Удаление:** Uninstall.bat. Удаляет всё, что установил установщик; модели — только после вашего подтверждения. Файлы — в Корзину (с флешки и сетевых дисков — сразу, без Корзины).

### Вручную

Выполните инструкцию для нужного workflow из папки [manual](manual): `<имя workflow>_Desktop` — для Comfy Desktop, `<имя workflow>_Portable` — для Portable.

## Если не работает

1. При открытом ComfyUI запустите **Check.bat** — он покажет, чего не хватает.
2. Перезапустите ComfyUI.
3. После обновления Comfy Desktop запустите Install.bat ещё раз.
4. Не помогло — напишите мне в Telegram: https://t.me/sofiakholina и приложите скриншот ошибки.

## Известные особенности

- После 3D-Texturing_GGUF остальные workflow в том же сеансе ComfyUI выдают ошибку в ноде Prep — перезапустите ComfyUI.
- Portable не запускается с ошибкой c10.dll — установите Microsoft Visual C++ Redistributable: https://aka.ms/vc14/vc_redist.x64.exe
- Install.bat пишет «Triton не работает» — установите тот же Microsoft Visual C++ Redistributable и запустите Install.bat ещё раз.
- В старом интерфейсе Comfy (не Nodes 2.0) видны служебные настройки Save 3D — их не нужно менять.

## Лицензия

GPL-3.0 (файл LICENSE). Сторонние ноды, workflow и модели — со своими лицензиями, см. [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Ноды s_tools — [sofiakholina-s_tools](https://github.com/sofiakholina/sofiakholina-s_tools).

**FLUX Non-Commercial License:** полученные текстуры можно использовать в том числе коммерчески; сам запуск модели для платной работы лицензия не разрешает. Перед работой на заказ проверьте условия: https://github.com/black-forest-labs/flux2/blob/main/model_licenses/LICENSE-FLUX-NON-COMMERICAL

---

## English

**Texture your own 3D model from photos in ComfyUI: 4 workflows + installer.**

Workflows:

- **3D-Texturing - texture from one photo**
- **3D-Texturing_MV - texture from 1-4 photos** (front, back, sides)
- **3D-Texturing_GGUF - lighter version for 6-8 GB VRAM**
- **3D-Texturing_MV_GGUF - lighter version for 6-8 GB VRAM**

Use the GGUF workflows only with 6-8 GB VRAM: with more VRAM (12+) they are much slower with no gain.

**Workflows for generating a 3D model from an image:** [sofiakholina-3D-Generation](https://github.com/sofiakholina/sofiakholina-3D-Generation).

## Install

**Windows only, NVIDIA GPU with a current driver (6 GB VRAM or more for the GGUF versions, 12 GB or more for the others), ComfyUI 0.45+. Free disk space: ComfyUI — about 6 GB, models — about 42 GB for the 4 workflows.**

Workflow notes are in Russian.

### Automatic

1. Install ComfyUI: [Comfy Desktop](https://www.comfy.org/download); [ComfyUI Portable](https://github.com/Comfy-Org/ComfyUI/releases) works too.
2. Download this repository: green **Code** button at the top of the page → **Download ZIP**, unzip it to any folder. You can delete this folder after installing (download the archive again for Check.bat and Uninstall.bat).
3. Close ComfyUI.
4. Run **Install.bat**. 
If Windows shows "Windows protected your PC", click **More info → Run anyway**.
5. Choose which workflows to install (Enter — recommended for your GPU) and whether to download the models. Running Install.bat again resumes the download.
6. Start ComfyUI: the workflows are in the left sidebar, **Workflows** (W key).

To verify: with ComfyUI open, run **Check.bat**; it shows whether all nodes and models are in place.

**After a Comfy Desktop update**, run Install.bat again.

**Uninstall:** Uninstall.bat. Removes everything the installer installed; models only after you confirm. Files go to the Recycle Bin (from USB and network drives they are deleted immediately, without the Recycle Bin).

### Manual

Follow the guide for your workflow in the [manual](manual) folder: `<workflow name>_Desktop` for Comfy Desktop, `<workflow name>_Portable` for Portable.

## Troubleshooting

1. With ComfyUI open, run **Check.bat** — it shows what is missing.
2. Restart ComfyUI.
3. After a Comfy Desktop update, run Install.bat again.
4. Still not working — message me on Telegram: https://t.me/sofiakholina and attach a screenshot of the error.

## Known issues

- After 3D-Texturing_GGUF the other workflows fail at the Prep node in the same ComfyUI session — restart ComfyUI.
- Portable fails with a c10.dll error: install the Microsoft Visual C++ Redistributable: https://aka.ms/vc14/vc_redist.x64.exe
- Install.bat says "Triton does not work": install the same Microsoft Visual C++ Redistributable and run Install.bat again.
- In the legacy Comfy UI (not Nodes 2.0) the internal settings of Save 3D are visible; you don't need to change them.

## License

GPL-3.0 (see LICENSE). Third-party nodes, workflows and models keep their own licenses, see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). s_tools nodes: [sofiakholina-s_tools](https://github.com/sofiakholina/sofiakholina-s_tools).

**FLUX Non-Commercial License:** the textures you get may be used commercially; running the model itself for paid work is not allowed by the license. Check https://github.com/black-forest-labs/flux2/blob/main/model_licenses/LICENSE-FLUX-NON-COMMERICAL before client work.
