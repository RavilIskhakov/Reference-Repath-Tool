<img width="620" height="554" alt="image" src="https://github.com/user-attachments/assets/7fb8b626-e941-49f7-8be2-a189a5918b4d" />
Reference Repath Tool
Простой тулзовый скрипт для Maya, чтобы быстро чинить потерянные рефы. Сканишь сцену, выбираешь сломанный реф из списка (или просто вставляешь строку Warning из Script Editor), указываешь путь к рабочему файлу и жмёшь Resolve.
Делал и тестил на Maya 2026 (PySide6). На старых версиях работает через PySide2.
Что умеет

Сканит сцену и показывает все рефы, потерянные сверху и подсвечены.
Можно вставить строку Warning целиком, путь сам вытащится.
Кнопки Browse для обоих путей.
Ищет ноду сначала по полному пути, потом по имени файла, так что подцепит даже если путь немного отличается.
Resolve перенаправляет реф и подгружает его.
Тёмный интерфейс.

Установка
Кинуть reference_repath_tool.py в папку скриптов Maya:

Windows: Documents/maya/<версия>/scripts/
Linux: ~/maya/<версия>/scripts/

И запустить из Script Editor (Python):
pythonimport reference_repath_tool
reference_repath_tool.show()
Или просто вставить весь файл в Script Editor и выполнить, окно откроется само.
Как пользоваться

Жмёшь Scan scene.
Выбираешь сломанный реф из списка (или вставляешь путь / строку Warning вручную).
Указываешь рабочую версию через Browse.
Жмёшь RESOLVE.

Reference Repath Tool
A small tool for Maya to quickly fix broken references. Scan the scene, pick the lost reference from the list (or just paste the Warning line from the Script Editor), point it at the working file, and hit Resolve.
Built and tested on Maya 2026 (PySide6). Works on older versions through PySide2.
Features

Scans the scene and lists all references, with lost ones at the top and highlighted.
You can paste the full Warning line — the path is extracted automatically.
Browse buttons for both paths.
Matches the node by full path first, then by file name, so it still works if the path differs slightly.
Resolve repaths the reference and reloads it.
Dark interface.

Installation
Drop reference_repath_tool.py into your Maya scripts folder:

Windows: Documents/maya/<version>/scripts/
Linux: ~/maya/<version>/scripts/

Then run it from the Script Editor (Python):
pythonimport reference_repath_tool
reference_repath_tool.show()
Or just paste the whole file into the Script Editor and execute it — the window opens by itself.
Usage

Click Scan scene.
Select the lost reference from the list (or paste the path / Warning line manually).
Set the working version via Browse.
Click RESOLVE.

