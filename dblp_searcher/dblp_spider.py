from bs4 import BeautifulSoup, SoupStrainer
import requests
import re
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# paper： 点击获取bibtex
def get_bibtex_from_url(dblp_url):
    """
    根据 DBLP 文献条目的 URL 获取 BibTeX 信息
    例如输入: https://dblp.org/rec/conf/ciarp/RozendoRNNL23
    实际抓取: https://dblp.org/rec/conf/ciarp/RozendoRNNL23.html?view=bibtex
    """
    bibtex_url = f"{dblp_url}?view=bibtex"
    try:
        response = requests.get(bibtex_url)
        response.raise_for_status()
        # soup = BeautifulSoup(response.text, "html.parser")
        soup = BeautifulSoup(response.text, 'lxml')

        # 找到 <div id="bibtex-section" class="section">
        bibtex_div = soup.find("div", id="bibtex-section")
        if bibtex_div:
            pre_tag = bibtex_div.find("pre")
            if pre_tag:
                return pre_tag.text.strip()
            else:
                return "未找到 <pre> 标签"
        else:
            return "未找到 bibtex-section div"
    except requests.RequestException as e:
        print(f"获取 BibTeX 时发生错误: {e}")
        return "请求错误"

# paper： 点击获取摘要
def get_abstract_by_doi(doi):
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,abstract,authors,year"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("abstract", "⚠️ 找不到摘要")
    else:
        return "❌ Semantic Scholar 查询失败"

# conference: 点击获取n年会议连接

def get_dblp_conference_links(index_url):
    """
    从 dblp 会议 index 页面中提取最近 n 个会议年份的链接和名称。

    参数：
        index_url: str - 会议 index 页 URL，例如 https://dblp.org/db/conf/cvpr/index.html
        recent_n: int - 只返回最近的 n 个会议（按年份倒序）

    返回：
        List[Tuple[会议名称, 会议链接]]
    """
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(index_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"请求失败，状态码：{response.status_code}")

    # soup = BeautifulSoup(response.text, 'html.parser')
    soup = BeautifulSoup(response.text, 'lxml')
    # 从 URL 提取会议简称（如 cvpr）
    match = re.search(r"/conf/([^/]+)/index\.html", index_url)
    if not match:
        raise ValueError("无法从 URL 中解析会议简称")
    conf_abbr = match.group(1).upper()

    results = []

    # 找到所有 li.entry.editor.toc 条目
    toc_items = soup.find_all('li', class_='entry editor toc')

    for item in toc_items:
        link_tag = item.find('a', href=True)
        if not link_tag:
            continue
        link = link_tag['href']

        # 提取年份
        item_id = item.get("id", "")
        year_match = re.search(r"(\d{4})", item_id or link)
        if not year_match:
            continue
        year = int(year_match.group(1))
        conf_name = f"{conf_abbr} {year}"
        results.append((year, conf_name, link))

    # 按年份倒序排序，只保留最近 n 个
    results = sorted(results, key=lambda x: x[0], reverse=True)

    # 去掉年份，只返回 (name, link)
    return [(name, link) for _, name, link in results]

# conference: 点击获取n卷期刊连接
def get_dblp_search_conference_links(index_url):
    """
    从 dblp 会议 index 页面中提取最近 n 个会议年份的链接和名称。

    参数：
        index_url: str - 会议 index 页 URL，例如 https://dblp.org/db/conf/cvpr/index.html
        recent_n: int - 只返回最近的 n 个会议（按年份倒序）

    返回：
        List[Tuple[会议名称, 会议链接]]
    """
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(index_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"请求失败，状态码：{response.status_code}")

    # soup = BeautifulSoup(response.text, 'html.parser')
    soup = BeautifulSoup(response.text, 'lxml')

    # 从 URL 提取会议简称（如 cvpr）
    match = re.search(r"/conf/([^/]+)/", index_url)
    if not match:
        raise ValueError("无法从 URL 中解析会议简称")
    conf_abbr = match.group(1).upper()

    results = []

    # 找到所有 li.entry.editor.toc 条目
    toc_items = soup.find_all('li', class_='entry editor toc')

    for item in toc_items:
        link_tag = item.find('a', href=True)
        if not link_tag:
            continue
        link = link_tag['href']

        # 提取年份
        item_id = item.get("id", "")
        year_match = re.search(r"(\d{4})", item_id or link)
        if not year_match:
            continue
        year = int(year_match.group(1))
        conf_name = f"{conf_abbr} {year}"
        results.append((year, conf_name, link))

    # 按年份倒序排序，只保留最近 n 个
    results = sorted(results, key=lambda x: x[0], reverse=True)

    # 去掉年份，只返回 (name, link)
    return [(name, link) for _, name, link in results]

def get_journal_volumes(index_url):
    """
    爬取dblp期刊主页中的期刊卷号和对应链接。

    参数：
        index_url: str - 期刊主页URL，如 https://dblp.org/db/journals/pami/index.html
        recent_n: int or None - 返回最近的n个卷号，默认返回全部

    返回：
        List[(卷号字符串, 链接字符串)]，例如 [('Volume 47: 2025', 'https://dblp.org/db/journals/pami/pami47.html'), ...]
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(index_url, headers=headers)
    if r.status_code != 200:
        raise Exception(f"请求失败，状态码：{r.status_code}")

    # soup = BeautifulSoup(r.text, 'html.parser')
    soup = BeautifulSoup(r.text, 'lxml')

    volumes = []
    # 查找所有<li>标签下的<a>标签
    for li in soup.find_all('li'):
        for a_tag in li.find_all('a', href=True):
            if a_tag:
                href = a_tag['href']
                text = a_tag.get_text(strip=True)
                # 判断 href 是否包含期刊卷页链接（简单过滤）
                # if 'db/journals' in href and 'html' in href and text.lower().startswith('volume'):
                if 'db/journals' in href and 'html' in href:
                    volumes.append((text, href))

    # 按卷号排序（假设格式固定，提取数字排序）
    def extract_volume_num(volume_str):
        import re
        m = re.findall(r'\d+', volume_str)
        return [int(num) for num in m] if m else []

    volumes = sorted(volumes, key=lambda x: extract_volume_num(x[0]), reverse=True)

    return volumes

# authors: 点击获取作者所有论文

def crawl_dblp_profile(url):

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Encoding": "gzip, deflate"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml',parse_only=SoupStrainer('ul', class_='publ-list'))
    papers = []
    current_year = None

    for li in soup.find_all('li', class_='entry'):
        # 更新年份信息
        if 'class' in li.attrs and li['class'] == ['year']:
            current_year = li.text.strip()
            continue

        # 只处理论文条目
        if 'class' in li.attrs and 'entry' in li['class']:
            try:
                # 标题
                title_tag = li.find('span', class_='title')
                title = title_tag.text.strip() if title_tag else "N/A"

                # 作者
                author_tags = li.find_all('span', itemprop='author')
                authors = [a.text.strip() for a in author_tags] if author_tags else []

                # 发表 venue
                venue_tag = li.find('span', class_='venue')
                venue = venue_tag.text.strip() if venue_tag else "N/A"

                # 页码
                pages_tag = li.find('span', itemprop='pagination')
                pages = pages_tag.text.strip() if pages_tag else "N/A"

                # 类型
                type_classes = li.get('class', [])
                type_ = next((cls for cls in type_classes if cls != 'entry'), 'N/A')

                # 访问权限
                access = "open access" if li.find('img', alt='open access') else "N/A"

                # dblp key
                key = li.get('id', 'N/A')

                # DOI 和电子版链接
                doi = "N/A"
                ee = "N/A"
                for a_tag in li.find_all('a', href=True):
                    href = a_tag['href']
                    if href.startswith('https://doi.org/'):\
                        doi = re.sub(r"https?://doi\.org/", "", href)
                    elif 'electronic edition' in a_tag.text.lower():
                        ee = href

                # 详情页 URL
                detail_tag = li.find('a', href=re.compile(r'/rec/'))
                url = f"{detail_tag['href']}" if detail_tag else "N/A"

                # 卷号
                volume_tag = li.find('span', itemprop='volumeNumber')
                volume = volume_tag.text.strip() if volume_tag else "N/A"

                entry = {
                    "title": title,
                    "authors": authors,
                    "venue": venue,
                    "pages": pages,
                    "year": current_year,
                    "type": type_,
                    "access": access,
                    "key": key,
                    "doi": doi,
                    "ee": ee,
                    "url": url,
                    "volume": volume
                }

                papers.append(entry)
            except Exception as e:
                print(f"Error parsing entry: {e}")

    return papers


def parse_dblp_entries(entries):
    result_list = []
    try:
        for item in entries:
            entry = {
                "title": item.get("title", "N/A"),
                "authors": item.get("authors", []),
                "venue": item.get("venue", "N/A"),
                "pages": item.get("pages", "N/A"),
                "year": item.get("year", "N/A"),
                "type": item.get("type", "N/A"),
                "access": item.get("access", "N/A"),
                "key": item.get("key", "N/A"),
                "doi": item.get("doi", "N/A"),
                "ee": item.get("ee", "N/A"),
                "url": item.get("url", "N/A"),
                "volume": item.get("volume", "N/A"),
            }
            result_list.append(entry)
    except Exception as e:
        print(f"解析条目时出错: {e}")
    return result_list


# if __name__ == "__main__":
#     # 示例 DOI（你也可以换成任意一个真实 DOI）
#     example_doi = "10.1109/CVPR52688.2022.01846"  # 来自CVPR 2022的一篇论文
#     print(f"🔍 正在获取摘要，DOI: {example_doi}")
#
#     abstract = get_abstract_by_doi(example_doi)
#
#     print("\n📄 获取到的摘要：")
#     print(abstract)
#
#     print(get_bibtex_from_url('https://dblp.org/rec/conf/ciarp/RozendoRNNL23'))
#
#
#     url = "https://dblp.org/db/conf/iclr/index.html"
#     latest_confs = get_dblp_conference_links(url, recent_n=10)
#     for name, link in latest_confs:
#         print(f"{name}: {link}")

        # url = "https://dblp.org/db/journals/pami/index.html"
        #     vols = get_journal_volumes(url, recent_n=5)
        #     for name, link in vols:
        #         print(f"{name}: {link}")
        #
        # url = "https://dblp.org/pid/202/1700.html"
        # results = crawl_dblp_profile(url)
        #
        # for idx, paper in enumerate(results, 1):
        #     print(f"{idx}. {paper['title']} ({paper['year']})")
        #     print(f"   Authors: {', '.join(paper['authors'])}")
        #     print(f"   Venue: {paper['venue']}")
        #     print(f"   Pages: {paper['pages']}")
        #     print(f"   Type: {paper['type']}")
        #     print(f"   Access: {paper['access']}")
        #     print(f"   Key: {paper['key']}")
        #     print(f"   DOI: {paper['doi']}")
        #     print(f"   EE: {paper['ee']}")
        #     print(f"   URL: {paper['url']}")
        #     print(f"   Volume: {paper['volume']}\n")
