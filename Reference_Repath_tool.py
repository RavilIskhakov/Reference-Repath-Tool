import maya.cmds as cmds
import maya.OpenMayaUI as omui

try:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance


def _maya_main_window():
    ptr = omui.MQtUtil.mainWindow()
    if ptr is not None:
        return wrapInstance(int(ptr), QtWidgets.QWidget)
    return None


def _extract_path(text):
    text = (text or "").strip().strip('"').strip("'")
    if not text:
        return ""
    if "not found" in text.lower() and " : " in text:
        text = text.rsplit(" : ", 1)[-1].strip()
    return text.replace("\\", "/")


def _real_reference_nodes():
    nodes = []
    for ref_node in cmds.ls(type="reference") or []:
        if ref_node.endswith("sharedReferenceNode"):
            continue
        nodes.append(ref_node)
    return nodes


def _scan_lost_references():
    result = []
    for ref_node in _real_reference_nodes():
        try:
            fn = cmds.referenceQuery(ref_node, filename=True, withoutCopyNumber=True)
        except Exception:
            fn = None
        try:
            loaded = cmds.referenceQuery(ref_node, isLoaded=True)
        except Exception:
            loaded = False
        result.append((ref_node, fn or "", bool(loaded)))
    result.sort(key=lambda x: x[2])
    return result


def _find_reference_node(old_path):
    old_norm = old_path.replace("\\", "/").lower()
    old_name = old_norm.rsplit("/", 1)[-1]
    matches = []
    for ref_node in _real_reference_nodes():
        try:
            cur = cmds.referenceQuery(ref_node, filename=True, withoutCopyNumber=True)
        except Exception:
            continue
        if not cur:
            continue
        cur_norm = cur.replace("\\", "/").lower()
        cur_name = cur_norm.rsplit("/", 1)[-1]
        if cur_norm == old_norm:
            matches.insert(0, ref_node)
        elif cur_name == old_name:
            matches.append(ref_node)
    return matches


_DARK_QSS = """
QWidget {
    background-color: #2b2b2b;
    color: #dcdcdc;
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
}
QLabel#title {
    font-size: 15px;
    font-weight: bold;
    color: #ffffff;
}
QLabel#hint {
    color: #8a8a8a;
    font-size: 11px;
}
QLabel#sign {
    color: #6a6a6a;
    font-size: 10px;
}
QLineEdit, QListWidget {
    background-color: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 5px;
    selection-background-color: #4a708b;
}
QLineEdit:focus, QListWidget:focus {
    border: 1px solid #5a8db0;
}
QListWidget::item {
    padding: 4px 2px;
}
QListWidget::item:selected {
    background-color: #4a708b;
    color: #ffffff;
}
QPushButton {
    background-color: #3c3c3c;
    border: 1px solid #4a4a4a;
    border-radius: 4px;
    padding: 6px 12px;
}
QPushButton:hover { background-color: #484848; }
QPushButton:pressed { background-color: #2e2e2e; }
QPushButton#resolve {
    background-color: #3a6e3a;
    border: 1px solid #4c8c4c;
    font-weight: bold;
    font-size: 13px;
}
QPushButton#resolve:hover { background-color: #468446; }
QPushButton#resolve:pressed { background-color: #2f5a2f; }
"""


class ReferenceRepathTool(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(ReferenceRepathTool, self).__init__(parent or _maya_main_window())
        self.setWindowTitle("Reference Repath Tool")
        self.setMinimumWidth(620)
        self.setStyleSheet(_DARK_QSS)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window)
        self._build_ui()
        self._scan()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        title = QtWidgets.QLabel("Reference Repath Tool")
        title.setObjectName("title")
        layout.addWidget(title)

        row = QtWidgets.QHBoxLayout()
        lbl = QtWidgets.QLabel("Рефы в сцене (незагруженные сверху):")
        row.addWidget(lbl)
        row.addStretch()
        scan_btn = QtWidgets.QPushButton("Scan scene")
        scan_btn.clicked.connect(self._scan)
        row.addWidget(scan_btn)
        layout.addLayout(row)

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setMinimumHeight(150)
        self.list_widget.itemSelectionChanged.connect(self._on_list_select)
        layout.addWidget(self.list_widget)

        layout.addWidget(QtWidgets.QLabel(
            "Потерянный реф (можно вставить строку Warning целиком):"))
        old_row = QtWidgets.QHBoxLayout()
        self.old_field = QtWidgets.QLineEdit()
        self.old_field.setPlaceholderText(
            "E:/.../SM_MainCharacter_tris_rig2.ma")
        old_browse = QtWidgets.QPushButton("Browse")
        old_browse.clicked.connect(self._browse_old)
        old_row.addWidget(self.old_field)
        old_row.addWidget(old_browse)
        layout.addLayout(old_row)

        layout.addWidget(QtWidgets.QLabel("Исправленная версия:"))
        new_row = QtWidgets.QHBoxLayout()
        self.new_field = QtWidgets.QLineEdit()
        self.new_field.setPlaceholderText(
            "E:/.../SM_MainCharacter_tris_rig2_FIXED.ma")
        new_browse = QtWidgets.QPushButton("Browse")
        new_browse.clicked.connect(self._browse_new)
        new_row.addWidget(self.new_field)
        new_row.addWidget(new_browse)
        layout.addLayout(new_row)

        self.resolve_btn = QtWidgets.QPushButton("RESOLVE")
        self.resolve_btn.setObjectName("resolve")
        self.resolve_btn.setMinimumHeight(40)
        self.resolve_btn.clicked.connect(self._resolve)
        layout.addWidget(self.resolve_btn)

        self.status = QtWidgets.QLabel("")
        self.status.setObjectName("hint")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        sign = QtWidgets.QLabel("tg: @haiiroever")
        sign.setObjectName("sign")
        sign.setAlignment(QtCore.Qt.AlignRight)
        layout.addWidget(sign)

    def _scan(self):
        self.list_widget.clear()
        data = _scan_lost_references()
        if not data:
            self.status.setText("Рефов в сцене не найдено.")
            return
        lost = 0
        for ref_node, fn, loaded in data:
            mark = "loaded" if loaded else "LOST"
            if not loaded:
                lost += 1
            item = QtWidgets.QListWidgetItem("[%s]  %s" % (mark, fn))
            item.setData(QtCore.Qt.UserRole, (ref_node, fn))
            if not loaded:
                item.setForeground(QtGui.QColor("#e0a04a"))
            self.list_widget.addItem(item)
        self.status.setText(
            "Найдено рефов: %d  (потерянных/незагруженных: %d)" % (len(data), lost))

    def _on_list_select(self):
        items = self.list_widget.selectedItems()
        if not items:
            return
        ref_node, fn = items[0].data(QtCore.Qt.UserRole)
        self.old_field.setText(fn)

    def _browse_old(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select OLD (lost) reference file", "",
            "Maya Files (*.ma *.mb);;All Files (*.*)")
        if path:
            self.old_field.setText(path)

    def _browse_new(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select NEW (fixed) reference file", "",
            "Maya Files (*.ma *.mb);;All Files (*.*)")
        if path:
            self.new_field.setText(path)

    def _resolve(self):
        old_path = _extract_path(self.old_field.text())
        new_path = _extract_path(self.new_field.text())

        if not old_path:
            self.status.setText("Не указан путь потерянного рефа.")
            return
        if not new_path:
            self.status.setText("Не указан путь исправленной версии.")
            return

        self.old_field.setText(old_path)

        ref_nodes = _find_reference_node(old_path)
        if not ref_nodes:
            self.status.setText(
                "Не найден reference node для:\n%s\n"
                "Проверь имя файла / выбери ноду из списка." % old_path)
            return

        ref_node = ref_nodes[0]
        try:
            cmds.file(new_path, loadReference=ref_node)
            loaded_path = cmds.referenceQuery(ref_node, filename=True)
            self.status.setText(
                "OK: Reference перенаправлен.\nNode: %s\nНовый файл: %s"
                % (ref_node, loaded_path))
            print("// Reference '%s' -> %s" % (ref_node, new_path))
            self._scan()
        except Exception as e:
            self.status.setText("Ошибка: %s" % str(e))
            cmds.warning(str(e))


_tool_instance = None


def show():
    global _tool_instance
    try:
        if _tool_instance:
            _tool_instance.close()
            _tool_instance.deleteLater()
    except Exception:
        pass
    _tool_instance = ReferenceRepathTool()
    _tool_instance.show()
    return _tool_instance


if __name__ == "__main__":
    show()