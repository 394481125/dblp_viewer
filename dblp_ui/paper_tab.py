from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QSpinBox, QPushButton, QTableWidgetItem,
                             QLabel, QMessageBox, QSplitter)
from PyQt5.QtCore import Qt
from dblp_searcher.dblp_visualizer import generate_wordcloud
from dblp_ui.base_tab import BaseTab, ImageLoaderWorker, BaseTableWidget
from dblp_ui.base_workers import PaperSearchWorker


class PaperTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_signals()

    def init_ui(self):
        """初始化界面组件"""
        main_layout = QVBoxLayout()
        
        # 搜索控制区
        search_layout = QHBoxLayout()
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("输入文献关键词（如：transformer）")
        self.result_count = QSpinBox()
        self.result_count.setRange(1, 100)
        self.result_count.setValue(20)
        self.search_btn = QPushButton("开始搜索")
        search_layout.addWidget(QLabel("关键词："))
        search_layout.addWidget(self.keyword_input)
        search_layout.addWidget(QLabel("最大结果数："))
        search_layout.addWidget(self.result_count)
        search_layout.addWidget(self.search_btn)

        
        # 结果展示表格
        self.paper_table = BaseTableWidget()
        self.paper_table.resizeColumnsToContents()
        self.paper_table.setColumnCount(6)
        self.paper_table.setHorizontalHeaderLabels([
            "标题", "作者", "发表源", "年份", "DOI", "操作"
        ])

        self.paper_table.setColumnWidth(0, 800)
        self.paper_table.setColumnWidth(1, 100)
        self.paper_table.setColumnWidth(2, 100)
        self.paper_table.setColumnWidth(3, 50)
        self.paper_table.setColumnWidth(4, 100)
        self.paper_table.setColumnWidth(5, 200)

        # 词云展示区
        self.stats_label = QLabel()

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.progress_bar)  # 下部分为统计标签
        splitter.addWidget(self.paper_table)  # 上部分为论文表格
        splitter.addWidget(self.stats_label)  # 下部分为统计标签
        splitter.setChildrenCollapsible(False)  # 禁止折叠子部件

        main_layout.addLayout(search_layout)
        main_layout.addWidget(splitter, 1)  # 分割器占据拉伸空间
        self.setLayout(main_layout)


    def init_signals(self):
        """初始化信号连接"""
        self.keyword_input.returnPressed.connect(self.start_search)
        self.search_btn.clicked.connect(self.start_search)

    def start_search(self):
        """启动搜索流程"""
        keyword = self.keyword_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "提示", "请输入搜索关键词")
            return
            
        self.progress_bar.show()
        self.paper_table.setRowCount(0)  # 清空旧数据
        
        # 启动异步搜索线程
        self.worker = PaperSearchWorker(keyword, self.result_count.value())
        self.worker.search_finished.connect(self.handle_search_result)
        self.worker.search_failed.connect(self.handle_search_error)
        self.worker.start()

    def handle_search_result(self, papers):
        """处理搜索结果"""
        self.progress_bar.hide()
        if not papers:
            QMessageBox.information(self, "提示", "未找到相关文献")
            return

        # 填充表格数据
        self.paper_table.setRowCount(len(papers))
        for row, paper in enumerate(papers):
            self.paper_table.setItem(row, 0, QTableWidgetItem(paper['title']))
            self.paper_table.setItem(row, 1, QTableWidgetItem(", ".join(paper['authors'])))
            self.paper_table.setItem(row, 2, QTableWidgetItem(paper['venue']))
            self.paper_table.setItem(row, 3, QTableWidgetItem(str(paper['year'])))
            self.paper_table.setItem(row, 4, QTableWidgetItem(paper['doi']))
            # ... 其他字段填充
            
            # 添加操作按钮
            op_layout = QHBoxLayout()
            bib_btn = QPushButton("BibTeX")
            bib_btn.setMinimumHeight(20)  # 设置最小高度
            bib_btn.clicked.connect(lambda _, url=paper['url']: self.get_bibtex(url))
            abstract_btn = QPushButton("摘要")
            abstract_btn.setMinimumHeight(20)  # 设置最小高度
            abstract_btn.clicked.connect(lambda _, doi=paper['doi']: self.get_abstract(doi))
            op_layout.addWidget(bib_btn)
            op_layout.addWidget(abstract_btn)
            
            # 创建容器Widget并设置布局
            op_widget = QWidget()
            op_widget.setLayout(op_layout)
            self.paper_table.setCellWidget(row, 5, op_widget)

        # 生成词云（基于论文标题）
        titles = " ".join([p['title'] for p in papers])
        wc_path = generate_wordcloud(titles)
        # 启动后台线程加载图片
        self.image_loader = ImageLoaderWorker(wc_path)
        self.image_loader.image_loaded.connect(self.update_wordcloud_display)
        self.image_loader.start()

    def update_wordcloud_display(self, pixmap):
        """响应后台线程的图片加载完成信号，更新词云显示"""
        # 假设使用stats_label显示词云（根据实际UI布局调整）
        self.stats_label.setPixmap(pixmap)  # 适配标签宽度