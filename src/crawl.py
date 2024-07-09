import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# 爬取网页并返回 BeautifulSoup 对象
def fetch_page(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')


# 爬取数据的主函数
def scrape_data(url):
    soup = fetch_page(url)

    # 提取网页标题
    title = soup.title.string

    # 提取所有段落文本
    paragraphs = [p.text for p in soup.find_all('p')]

    # 提取所有链接和对应的文本
    links_data = []
    links = soup.find_all('a', href=True)
    for link in links:
        link_text = link.text
        link_href = link.get('href')

        # 跳过锚链接和相对路径链接
        if not link_href.startswith('http'):
            link_href = urljoin(url, link_href)

        try:
            # 爬取链接页面的文本
            link_soup = fetch_page(link_href)
            link_paragraphs = [p.text for p in link_soup.find_all('p')]

            links_data.append({
                'text': link_text,
                'href': link_href,
                'content': link_paragraphs
            })
        except requests.exceptions.RequestException as e:
            print(f"无法访问链接 {link_href}: {e}")

    # 组织爬取的数据
    data = {
        'title': title,
        'paragraphs': paragraphs,
        'links': links_data
    }
    return data


# 爬取指定网页的数据
url = 'https://cdn.cnbj1.fds.api.mi-img.com/ics-resources/articles/60547bdbec317cb4ee2c0a19.html'
scraped_data = scrape_data(url)

# 将数据存入JSON文件
with open('../data/mi_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(scraped_data, json_file, ensure_ascii=False, indent=4)

print("数据已成功存入 iphone_guide_data.json 文件")