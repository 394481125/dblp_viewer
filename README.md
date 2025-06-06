# DBLP学术检索系统

## 项目简介
本项目是一个基于DBLP学术数据库的桌面检索工具，支持文献、作者、期刊、会议四大维度的学术信息检索。通过图形化界面提供便捷的搜索功能，并集成论文信息展示、词云统计、BibTeX获取及摘要翻译等实用功能。

## 功能特性
- **多维度检索**：支持文献关键词检索、作者信息检索、期刊及会议的期卷检索
- **可视化统计**：基于检索结果自动生成论文标题词云，直观展示研究热点
- **扩展功能**：
  - 点击论文条目可获取BibTeX引用格式
  - 支持通过DOI获取论文摘要（集成百度翻译）
  - 表格支持排序、多选复制等操作

## 安装与运行
### 环境要求
- Python 3.8+
- Windows/macOS/Linux 系统（推荐Windows）

### 安装步骤
1. 克隆项目仓库：
   ```bash
   git clone https://github.com/394481125/dblp_viewer.git
   cd dblp
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

### 运行程序
```bash
python main.py
```

### 构建EXE
```bash
python pyinstaller -F -w .\main.py
```

## 依赖项
具体依赖见 `requirements.txt` 文件。

## 项目结构
```
dblp/
├── dblp_searcher/       # 核心搜索逻辑模块
│   ├── dblp_api.py      # DBLP接口调用
│   ├── dblp_spider.py   # 网页爬取工具
│   ├── dblp_visualizer.py # 词云生成
│   └── dblp_translate.py # 翻译工具
├── dblp_ui/             # 界面模块
│   ├── paper_tab.py     # 文献检索页签
│   ├── author_tab.py    # 作者检索页签
│   ├── journal_tab.py   # 期刊检索页签
│   ├── conference_tab.py # 会议检索页签
│   └── base_tab.py      # 基础页签组件
├── assets/             # 静态资源（词云示例图）
├── main.py             # 主程序入口
└── requirements.txt     # 依赖清单
```

## 注意事项
- 百度翻译功能需要在 `dblp_searcher/dblp_translate.py` 中配置API密钥
- 首次运行可能需要下载DBLP缓存数据，耗时较长请耐心等待
- 若检索无结果，请检查网络连接或关键词拼写
