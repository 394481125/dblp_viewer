from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QTableWidgetItem, QLabel,
                             QMessageBox, QListWidget, QSplitter)
from PyQt5.QtCore import Qt
from dblp_searcher.dblp_visualizer import generate_wordcloud
from dblp_ui.base_tab import BaseTab, ImageLoaderWorker, BaseTableWidget
from dblp_ui.base_workers import ConferencePaperWorker, ConferenceSearchWorker, ConferenceVolumesSearchWorker


class ConferenceTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.current_conference_url = None  # 记录当前选中会议的DBLP链接
        self.init_ui()
        self.init_signals()

    def init_ui(self):
        """初始化会议检索界面"""
        main_layout = QVBoxLayout()
        
        # 会议搜索控制区
        search_layout = QHBoxLayout()
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("输入会议关键词（如：SIGKDD）")
        self.search_btn = QPushButton("搜索会议")
        search_layout.addWidget(QLabel("会议关键词："))
        search_layout.addWidget(self.keyword_input)
        search_layout.addWidget(self.search_btn)
        
        # 会议列表展示（用于用户选择）
        self.conference_list = QListWidget()
        self.conference_list.setMinimumHeight(50)
        self.conference_list.setMaximumHeight(100)
        
        # 新增：期卷列表展示（用于用户选择）
        self.volume_list = QListWidget()
        self.volume_list.hide()  # 初始隐藏，选择会议后显示
        self.volume_list.setMinimumHeight(50)
        self.volume_list.setMaximumHeight(100)

        # 论文结果展示表格（列头适配会议场景）
        self.paper_table = BaseTableWidget()
        self.paper_table.setColumnCount(4)
        self.paper_table.setHorizontalHeaderLabels([
            "标题", "作者", "doi", "操作"
        ])
        self.paper_table.setColumnWidth(0, 800)
        self.paper_table.setColumnWidth(1, 100)
        self.paper_table.setColumnWidth(2, 100)
        self.paper_table.setColumnWidth(3, 200)
        
        # 统计信息展示区（示例：会议热度趋势图）
        self.stats_label = QLabel()

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.conference_list)  # 上部分为论文表格
        splitter.addWidget(self.volume_list)  # 上部分为论文表格
        splitter.addWidget(self.progress_bar)  # 上部分为论文表格
        splitter.addWidget(self.paper_table)  # 上部分为论文表格
        splitter.addWidget(self.stats_label)  # 下部分为统计标签
        splitter.setChildrenCollapsible(False)  # 禁止折叠子部件
        
        # 布局组装
        main_layout.addLayout(search_layout)
        main_layout.addWidget(splitter, 1)  # 分割器占据拉伸空间
        self.setLayout(main_layout)

    def init_signals(self):
        """初始化信号连接"""
        self.search_btn.clicked.connect(self.start_conference_search)
        self.conference_list.itemClicked.connect(self.on_conference_selected)
        self.keyword_input.returnPressed.connect(self.start_conference_search)
        # 新增：期卷列表点击信号
        self.volume_list.itemClicked.connect(self.on_volume_selected)

    def on_volume_selected(self, item):
        """用户选择期卷后触发论文获取"""
        volume_url = item.data(1)  # 从列表项获取期卷DBLP链接
        if not volume_url:
            return
            
        self.progress_bar.show()
        self.paper_table.setRowCount(0)  # 清空旧论文数据
        
        # 启动论文获取线程（使用期卷URL）
        self.paper_worker = ConferencePaperWorker(volume_url)
        self.paper_worker.papers_fetched.connect(self.handle_paper_result)
        self.paper_worker.fetch_failed.connect(self.handle_search_error)
        self.paper_worker.start()

    def start_conference_search(self):
        """启动会议搜索流程"""
        keyword = self.keyword_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "提示", "请输入会议关键词")
            return
            
        self.progress_bar.show()
        self.conference_list.clear()  # 清空旧会议列表
        self.paper_table.setRowCount(0)  # 清空旧论文数据
        
        # 启动会议搜索线程
        self.conference_worker = ConferenceSearchWorker(keyword)
        self.conference_worker.search_finished.connect(self.handle_conference_result)
        self.conference_worker.search_failed.connect(self.handle_search_error)
        self.conference_worker.start()

    def handle_conference_result(self, conferences):
        """处理会议搜索结果（展示会议列表供选择）"""
        self.progress_bar.hide()
        if not conferences:
            QMessageBox.information(self, "提示", "未找到相关会议")
            return
        # 填充会议列表（显示：缩写 | 会议名称）
        for conference in conferences:
            display_text = f"{conference['acronym']} | {conference['venue']}"
            self.conference_list.addItem(display_text)
            # 为列表项附加会议DBLP链接（通过setData方法存储）
            self.conference_list.item(self.conference_list.count()-1).setData(1, conference['url'])

    def on_conference_selected(self, item):
        """用户选择会议后触发期卷搜索"""
        self.current_conference_url = item.data(1)  # 从列表项获取会议DBLP链接
        if not self.current_conference_url:
            return
            
        self.progress_bar.show()
        self.volume_list.clear()  # 清空旧期卷列表
        self.paper_table.setRowCount(0)  # 清空旧论文数据
        self.volume_list.hide()  # 搜索期间隐藏
        
        # 启动期卷搜索线程
        self.volume_worker = ConferenceVolumesSearchWorker(self.current_conference_url)
        self.volume_worker.search_finished.connect(self.handle_volume_result)
        self.volume_worker.search_failed.connect(self.handle_search_error)
        self.volume_worker.start()

    def handle_volume_result(self, volumes):
        # 处理期卷搜索结果（展示期卷列表供选择）
        self.progress_bar.hide()
        if not volumes:
            QMessageBox.information(self, "提示", "未找到该会议的期卷记录")
            return
        
        # 展示期卷列表
        self.volume_list.clear()
        self.volume_list.show()
        for volume in volumes:
            volume_name, volume_url = volume  # 解析期卷格式：(名称, url)
            self.volume_list.addItem(volume_name)
            # 为列表项附加期卷DBLP链接（通过setData方法存储）
            self.volume_list.item(self.volume_list.count()-1).setData(1, volume_url)

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