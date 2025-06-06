from PyQt5.QtWidgets import QWidget, QMessageBox, QDialog, QVBoxLayout, QTextEdit, QPushButton, \
    QAbstractItemView, QHeaderView, QProgressBar
from dblp_searcher.dblp_spider import get_bibtex_from_url, get_abstract_by_doi
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QTableWidget, QMenu, QApplication
from PyQt5.QtCore import Qt
from dblp_searcher.dblp_translate import baidu_translate


class BaseTab(QWidget):
    def __init__(self):
        super().__init__()

        # 加载进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setRange(0, 0)  # 无限加载模式
        self.progress_bar.hide()

    def handle_search_error(self, error_msg):
        """处理搜索错误"""
        self.progress_bar.hide()
        QMessageBox.critical(self, "错误", error_msg)

    def show_info(self,title, bibtex):
        dialog = CopyableInfoDialog(self, title, bibtex)
        dialog.exec_()

    def get_bibtex(self, dblp_url):
        """获取BibTeX信息"""
        bibtex = get_bibtex_from_url(dblp_url)
        self.show_info('Bibtex',bibtex)

    def get_abstract(self, doi):
        """获取论文摘要"""
        abstract = get_abstract_by_doi(doi)
        if abstract is not None:
            abstract = baidu_translate(abstract)
        self.show_info('摘要',abstract)

# 信息框类
class CopyableInfoDialog(QDialog):
    def __init__(self, parent=None, title="信息", content=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(500, 400)  # 设置合适的窗口大小

        # 创建垂直布局
        layout = QVBoxLayout(self)

        # 创建只读的文本编辑框用于显示信息
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlainText(content)
        self.text_edit.setReadOnly(True)  # 设为只读模式
        layout.addWidget(self.text_edit)

        # 添加复制按钮
        self.copy_button = QPushButton("复制到剪贴板", self)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(self.copy_button)

        # 添加确定按钮
        self.ok_button = QPushButton("确定", self)
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())
        # 可以添加复制成功的提示

# 图像加载类
class ImageLoaderWorker(QThread):
    """后台加载图片的工作线程"""
    image_loaded = pyqtSignal(QPixmap)  # 参数：加载完成的图片对象

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path  # 图片路径

    def run(self):
        # 在后台线程加载图片
        pixmap = QPixmap(self.image_path)
        self.image_loaded.emit(pixmap)  # 加载完成后发送信号

# 自定义表格类

class BaseTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super(BaseTableWidget, self).__init__(parent)

        # 表头可点击排序
        self.setSortingEnabled(True)

        # 支持多选
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)

        # 禁止编辑
        self.setEditTriggers(QTableWidget.NoEditTriggers)

        # 列宽可拖动
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # 自动调整列宽以适应内容（可选）
        self.horizontalHeader().setStretchLastSection(False)

        # 表格不可编辑（可根据需要修改）
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置右键菜单策略
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_menu)

    def open_menu(self, position):
        menu = QMenu()

        if self.selectedIndexes():
            copy_action = menu.addAction("复制选中单元格")
            action = menu.exec_(self.viewport().mapToGlobal(position))
            if action == copy_action:
                self.copy_selected_cells()

    def copy_selected_cells(self):
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return

        copied_text = ""

        for selection in selected_ranges:
            for row in range(selection.topRow(), selection.bottomRow() + 1):
                row_data = []
                for col in range(selection.leftColumn(), selection.rightColumn() + 1):
                    item = self.item(row, col)
                    row_data.append(item.text() if item else "")
                copied_text += "\t".join(row_data) + "\n"

        # 将复制内容放入剪贴板
        QApplication.clipboard().setText(copied_text.strip())
