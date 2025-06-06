from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QTableWidgetItem, QLabel,
                             QMessageBox, QListWidget, QSplitter)
from PyQt5.QtCore import Qt
from dblp_searcher.dblp_visualizer import generate_wordcloud
from dblp_ui.base_tab import BaseTab, ImageLoaderWorker, BaseTableWidget
from dblp_ui.base_workers import AuthorSearchWorker, AuthorPaperWorker


class AuthorTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.current_author_url = None  # 记录当前选中作者的DBLP链接
        self.init_ui()
        self.init_signals()

    def init_ui(self):
        """初始化作者检索界面"""
        main_layout = QVBoxLayout()
        
        # 作者搜索控制区
        search_layout = QHBoxLayout()
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("输入作者关键词（如：leskovec）")
        self.search_btn = QPushButton("搜索作者")
        search_layout.addWidget(QLabel("作者关键词："))
        search_layout.addWidget(self.keyword_input)
        search_layout.addWidget(self.search_btn)
        
        # 作者列表展示（用于用户选择）
        self.author_list = QListWidget()
        self.author_list.setMinimumHeight(50)
        self.author_list.setMaximumHeight(100)


        # 论文结果展示表格（与文献页签结构一致）
        self.paper_table = BaseTableWidget()
        self.paper_table.resizeColumnsToContents()
        self.paper_table.setColumnCount(4)
        self.paper_table.setHorizontalHeaderLabels([
            "标题", "作者", "DOI", "操作"
        ])
        self.paper_table.setColumnWidth(0, 800)
        self.paper_table.setColumnWidth(1, 100)
        self.paper_table.setColumnWidth(2, 100)
        self.paper_table.setColumnWidth(3, 200)
        
        # 词云展示区
        self.stats_label = QLabel()

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.author_list)  # 下部分为统计标签
        splitter.addWidget(self.progress_bar)  # 下部分为统计标签
        splitter.addWidget(self.paper_table)  # 上部分为论文表格
        splitter.addWidget(self.stats_label)  # 下部分为统计标签
        splitter.setChildrenCollapsible(False)  # 禁止折叠子部件

        main_layout.addLayout(search_layout)
        main_layout.addWidget(splitter, 1)  # 分割器占据拉伸空间
        self.setLayout(main_layout)


    def init_signals(self):
        """初始化信号连接"""
        self.search_btn.clicked.connect(self.start_author_search)
        # 添加回车键触发搜索
        self.keyword_input.returnPressed.connect(self.start_author_search)
        self.author_list.itemClicked.connect(self.on_author_selected)

    def start_author_search(self):
        """启动作者搜索流程"""
        keyword = self.keyword_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "提示", "请输入作者关键词")
            return
            
        self.progress_bar.show()
        self.author_list.clear()  # 清空旧作者列表
        self.paper_table.setRowCount(0)  # 清空旧论文数据
        
        # 启动作者搜索线程
        self.author_worker = AuthorSearchWorker(keyword)
        self.author_worker.search_finished.connect(self.handle_author_result)
        self.author_worker.search_failed.connect(self.handle_search_error)
        self.author_worker.start()

    def handle_author_result(self, authors):
        """处理作者搜索结果（展示作者列表供选择）"""
        self.progress_bar.hide()
        if not authors:
            QMessageBox.information(self, "提示", "未找到相关作者")
            return
        # 填充作者列表（显示姓名+机构）
        for author in authors:
            display_text = f"{author['author']} ({author['note']})"
            self.author_list.addItem(display_text)
            # 为列表项附加作者DBLP链接（通过setData方法存储）
            self.author_list.item(self.author_list.count()-1).setData(1, author['url'])

    def on_author_selected(self, item):
        """用户选择作者后触发论文获取"""
        self.current_author_url = item.data(1)  # 从列表项获取作者DBLP链接
        if not self.current_author_url:
            return
            
        self.progress_bar.show()
        self.paper_table.setRowCount(0)  # 清空旧论文数据
        
        # 启动论文获取线程
        self.paper_worker = AuthorPaperWorker(self.current_author_url)
        self.paper_worker.papers_fetched.connect(self.handle_paper_result)
        self.paper_worker.fetch_failed.connect(self.handle_search_error)
        self.paper_worker.start()

    def handle_paper_result(self, papers):
        """处理论文获取结果（填充表格+生成词云）"""
        self.progress_bar.hide()
        if not papers:
            QMessageBox.information(self, "提示", "该作者无论文记录")
            return
            
        # 填充论文表格（与文献页签逻辑一致）
        self.paper_table.setRowCount(len(papers))
        for row, paper in enumerate(papers):
            self.paper_table.setItem(row, 0, QTableWidgetItem(paper['title']))
            self.paper_table.setItem(row, 1, QTableWidgetItem(", ".join(paper['authors'])))
            self.paper_table.setItem(row, 2, QTableWidgetItem(paper['doi']))
            # ... 其他字段填充
            
            # 添加操作按钮（与文献页签逻辑一致）
            op_layout = QHBoxLayout()
            bib_btn = QPushButton("BibTeX")
            bib_btn.setMinimumHeight(20)  # 设置最小高度

            bib_btn.clicked.connect(lambda _, url=paper['url']: self.get_bibtex(url))
            abstract_btn = QPushButton("摘要")
            abstract_btn.setMinimumHeight(20)  # 设置最小高度

            abstract_btn.clicked.connect(lambda _, doi=paper['doi']: self.get_abstract(doi))
            op_layout.addWidget(bib_btn)
            op_layout.addWidget(abstract_btn)
            
            op_widget = QWidget()
            op_widget.setLayout(op_layout)
            self.paper_table.setCellWidget(row, 3, op_widget)

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