from PyQt5.QtCore import QThread, pyqtSignal

from dblp_searcher.dblp_api import search_author, search_venue, query_publications
from dblp_searcher.dblp_json2dic import parse_authors, parse_venues, parse_publications
from dblp_searcher.dblp_spider import crawl_dblp_profile, parse_dblp_entries, get_dblp_search_conference_links, \
    get_journal_volumes


class AuthorSearchWorker(QThread):
    """异步执行作者搜索的工作线程"""
    search_finished = pyqtSignal(list)  # 参数：作者列表（姓名/机构/DBLP链接）
    search_failed = pyqtSignal(str)     # 参数：错误信息

    def __init__(self, keyword):
        super().__init__()
        self.keyword = keyword

    def run(self):
        try:
            author_json = search_author(self.keyword)  # 调用作者搜索接口
            raw_authors = parse_authors(author_json)
            self.search_finished.emit(raw_authors)
        except Exception as e:
            self.search_failed.emit(f"作者搜索失败：{str(e)}")

class AuthorPaperWorker(QThread):
    """异步执行作者论文获取的工作线程"""
    papers_fetched = pyqtSignal(list)  # 参数：论文列表
    fetch_failed = pyqtSignal(str)     # 参数：错误信息

    def __init__(self, author_url):
        super().__init__()
        self.author_url = author_url

    def run(self):
        try:
            raw_papers = crawl_dblp_profile(self.author_url)  # 爬取作者简介页
            parsed_papers = parse_dblp_entries(raw_papers)  # 解析论文数据
            self.papers_fetched.emit(parsed_papers)
        except Exception as e:
            self.fetch_failed.emit(f"论文获取失败：{str(e)}")

class ConferenceSearchWorker(QThread):
    """异步执行会议搜索的工作线程"""
    search_finished = pyqtSignal(list)  # 参数：会议列表（名称/缩写/DBLP链接/届数）
    search_failed = pyqtSignal(str)     # 参数：错误信息

    def __init__(self, keyword):
        super().__init__()
        self.keyword = keyword

    def run(self):
        try:
            conference_json = search_venue(self.keyword)  # 调用会议搜索接口
            raw_conferences = parse_venues(conference_json)  # 解析会议数据
            self.search_finished.emit(raw_conferences)
        except Exception as e:
            self.search_failed.emit(f"会议搜索失败：{str(e)}")

class ConferenceVolumesSearchWorker(QThread):
    """异步执行会议搜索的工作线程"""
    search_finished = pyqtSignal(list)  # 参数：会议列表（名称/缩写/DBLP链接/届数）
    search_failed = pyqtSignal(str)     # 参数：错误信息

    def __init__(self, conference_url):
        super().__init__()
        self.conference_url = conference_url

    def run(self):
        try:
            conferencesVolumes = get_dblp_search_conference_links(self.conference_url)  # 调用会议搜索接口
            self.search_finished.emit(conferencesVolumes)
        except Exception as e:
            self.search_failed.emit(f"会议搜索失败：{str(e)}")

class ConferencePaperWorker(QThread):
    """异步执行会议论文获取的工作线程"""
    papers_fetched = pyqtSignal(list)  # 参数：会议论文列表
    fetch_failed = pyqtSignal(str)     # 参数：错误信息

    def __init__(self, conference_url):
        super().__init__()
        self.conference_url = conference_url

    def run(self):
        try:
            raw_papers = crawl_dblp_profile(self.conference_url)  # 爬取会议页
            parsed_papers = parse_dblp_entries(raw_papers)  # 解析论文数据
            self.papers_fetched.emit(parsed_papers)
        except Exception as e:
            self.fetch_failed.emit(f"论文获取失败：{str(e)}")

class journalSearchWorker(QThread):
    """异步执行期刊搜索的工作线程"""
    search_finished = pyqtSignal(list)  # 参数：期刊列表（名称/缩写/DBLP链接/届数）
    search_failed = pyqtSignal(str)  # 参数：错误信息

    def __init__(self, keyword):
        super().__init__()
        self.keyword = keyword

    def run(self):
        try:
            journal_json = search_venue(self.keyword)  # 调用期刊搜索接口
            raw_journals = parse_venues(journal_json)  # 解析期刊数据
            self.search_finished.emit(raw_journals)
        except Exception as e:
            self.search_failed.emit(f"期刊搜索失败：{str(e)}")

class journalVolumesSearchWorker(QThread):
    """异步执行期刊搜索的工作线程"""
    search_finished = pyqtSignal(list)  # 参数：期刊列表（名称/缩写/DBLP链接/届数）
    search_failed = pyqtSignal(str)  # 参数：错误信息

    def __init__(self, journal_url):
        super().__init__()
        self.journal_url = journal_url

    def run(self):
        try:
            journalsVolumes = get_journal_volumes(self.journal_url)  # 调用期刊搜索接口
            self.search_finished.emit(journalsVolumes)
        except Exception as e:
            self.search_failed.emit(f"期刊搜索失败：{str(e)}")

class journalPaperWorker(QThread):
    """异步执行期刊论文获取的工作线程"""
    papers_fetched = pyqtSignal(list)  # 参数：期刊论文列表
    fetch_failed = pyqtSignal(str)  # 参数：错误信息

    def __init__(self, journal_url):
        super().__init__()
        self.journal_url = journal_url

    def run(self):
        try:
            raw_papers = crawl_dblp_profile(self.journal_url)  # 爬取期刊页
            parsed_papers = parse_dblp_entries(raw_papers)  # 解析论文数据
            self.papers_fetched.emit(parsed_papers)
        except Exception as e:
            self.fetch_failed.emit(f"论文获取失败：{str(e)}")

class PaperSearchWorker(QThread):
    """异步执行文献搜索的工作线程"""
    search_finished = pyqtSignal(list)  # 参数：文献列表
    search_failed = pyqtSignal(str)     # 参数：错误信息

    def __init__(self, keyword, max_results):
        super().__init__()
        self.keyword = keyword
        self.max_results = max_results

    def run(self):
        try:
            raw_data = query_publications(self.keyword, self.max_results)
            parsed_data = parse_publications(raw_data)
            self.search_finished.emit(parsed_data)
        except Exception as e:
            self.search_failed.emit(f"搜索失败：{str(e)}")
