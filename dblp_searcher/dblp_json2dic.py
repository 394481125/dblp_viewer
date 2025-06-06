from dblp_searcher.dblp_api import query_publications,search_author,search_venue


def parse_publications(data):
    result_list = []
    try:
        hits = data.get("result", {}).get("hits", {}).get("hit", [])
        for hit in hits:
            info = hit.get("info", {})

            authors_raw = info.get("authors", {}).get("author", [])
            if isinstance(authors_raw, dict):
                authors = [authors_raw.get("text", "N/A")]
            elif isinstance(authors_raw, list):
                authors = [a.get("text", "N/A") for a in authors_raw]
            else:
                authors = []

            entry = {
                "title": info.get("title", "N/A"),
                "authors": authors,
                "venue": info.get("venue", "N/A"),
                "pages": info.get("pages", "N/A"),
                "year": info.get("year", "N/A"),
                "type": info.get("type", "N/A"),
                "access": info.get("access", "N/A"),
                "key": info.get("key", "N/A"),
                "doi": info.get("doi", "N/A"),
                "ee": info.get("ee", "N/A"),
                "url": info.get("url", "N/A"),
                "volume": info.get("volume", "N/A")  # only in some cases
            }
            result_list.append(entry)
    except Exception as e:
        print(f"解析 publication JSON 时出错: {e}")
    return result_list

def parse_authors(data):
    author_list = []
    try:
        hits = data.get("result", {}).get("hits", {}).get("hit", [])
        for hit in hits:
            info = hit.get("info", {})

            aliases_raw = info.get("aliases", {}).get("alias", [])
            if isinstance(aliases_raw, dict):
                aliases = [aliases_raw.get("text", "N/A")]
            elif isinstance(aliases_raw, list):
                aliases = [a.get("text", "N/A") if isinstance(a, dict) else a for a in aliases_raw]
            else:
                aliases = []

            notes_raw = info.get("notes", {}).get("note", [])
            if isinstance(notes_raw, dict):
                notes = [notes_raw.get("text", "N/A")]
            elif isinstance(notes_raw, list):
                notes = [n.get("text", "N/A") if isinstance(n, dict) else n for n in notes_raw]
            else:
                notes = []

            entry = {
                "author": info.get("author", "N/A"),
                "url": info.get("url", "N/A"),
                "aliases": aliases,
                "note": notes
            }
            author_list.append(entry)
    except Exception as e:
        print(f"解析 author JSON 时出错: {e}")
    return author_list

def parse_venues(data):
    venue_list = []
    try:
        hits = data.get("result", {}).get("hits", {}).get("hit", [])
        for hit in hits:
            info = hit.get("info", {})

            entry = {
                "venue": info.get("venue", "N/A"),
                "acronym": info.get("acronym", "N/A"),
                "type": info.get("type", "N/A"),
                "url": info.get("url", "N/A")
            }
            venue_list.append(entry)
    except Exception as e:
        print(f"解析 venue JSON 时出错: {e}")
    return venue_list

def display_publications(pub_results):
    print("\n📚 文献结果:")
    for i, item in enumerate(pub_results, 1):
        print(f"\n文献 #{i}:")
        for key in [
            "title", "authors", "venue", "pages", "year", "type", "access",
            "key", "doi", "ee", "url", "volume"
        ]:
            value = item.get(key)
            if isinstance(value, list):
                value = ', '.join(value)
            print(f"  {key}: {value}")

def display_authors(author_results):
    print("\n👤 作者结果:")
    for i, item in enumerate(author_results, 1):
        print(f"\n作者 #{i}:")
        print(f"  author: {item['author']}")
        print(f"  url: {item['url']}")
        print(f"  aliases: {', '.join(item['aliases']) if item['aliases'] else 'None'}")
        print(f"  note: {', '.join(item['note']) if item['note'] else 'None'}")

def display_venues(venue_results):
    print("\n🏛️ 出版源结果:")
    for i, item in enumerate(venue_results, 1):
        print(f"\n出版源 #{i}:")
        print(f"  venue: {item['venue']}")
        print(f"  acronym: {item['acronym']}")
        print(f"  type: {item['type']}")
        print(f"  url: {item['url']}")

if __name__ == "__main__":
    # 查询文献
    pub_json = query_publications("transformer vision", max_results=10)
    pub_results = parse_publications(pub_json)
    display_publications(pub_results)

    # 查询作者
    author_json = search_author("Geoffrey Hinton", max_results=3)
    author_results = parse_authors(author_json)
    display_authors(author_results)

    # 查询出版源
    venue_json = search_venue("CVPR", max_results=3)
    venue_results = parse_venues(venue_json)
    display_venues(venue_results)

