import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from dblp_ui.paper_tab import PaperTab
from dblp_ui.author_tab import AuthorTab  # 新增导入作者页签
from dblp_ui.journal_tab import JournalTab
from dblp_ui.conference_tab import ConferenceTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DBLP学术检索系统")
        self.setGeometry(100, 100, 1400, 900)  # 初始窗口大小
        
        # 创建页签容器
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # 添加各功能页签
        self.tab_widget.addTab(PaperTab(), "文献检索")
        self.tab_widget.addTab(AuthorTab(), "作者检索")  # 取消注释启用作者页签
        self.tab_widget.addTab(JournalTab(), "期刊检索")
        self.tab_widget.addTab(ConferenceTab(), "会议检索")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())