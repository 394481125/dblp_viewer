import requests
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://dblp.org/search"

def query_publications(keyword, max_results=1000):
    url = f"{BASE_URL}/publ/api?q={keyword}&format=json&h={max_results}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"查询文献失败: {e}")
        return {}

def search_author(author_name, max_results=1000):
    url = f"{BASE_URL}/author/api?q={author_name}&format=json&h={max_results}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"查询作者失败: {e}")
        return {}

def search_venue(venue_name, max_results=1000):
    url = f"{BASE_URL}/venue/api?q={venue_name}&format=json&h={max_results}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"查询出版源失败: {e}")
        return {}

if __name__ == "__main__":
    # 查询文献
    pub_json = query_publications("transformer vision", max_results=3)
    print(pub_json)

    # 查询作者
    author_json = search_author("Geoffrey Hinton", max_results=3)
    print(author_json)

    # 查询出版源
    venue_json = search_venue("CVPR", max_results=3)
    print(venue_json)