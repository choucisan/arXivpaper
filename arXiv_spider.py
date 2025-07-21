#papers form cvpr
import requests
from bs4 import BeautifulSoup
import csv
import re
import html
import concurrent.futures


def fetch_html(batch):
    url = "https://papercopilot.com/wp-admin/admin-ajax.php"
    params = {
        "action": "load_paperlist",
        "batch": batch,
        "conf": "cvpr",
        "year": 2023,
        "mode": "detail",
        "track": "main"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.text





def parse_arxivs(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    rows = soup.select("tr")
    arxivs = []
    seen_links = set()  # 用于去重

    for i, row in enumerate(rows):
        tds = row.find_all("td")
        if len(tds) < 3:
            continue

        td_html_2 = tds[2].decode_contents()
        td_html_2 = html.unescape(td_html_2)
        td_html_2 = td_html_2.replace('\\"', '"').replace("\\'", "'")
        td_html_2 = re.sub(r"href='\"(.*?)\"'", r'href="\1"', td_html_2)
        td_html_2 = re.sub(r"title='\"(.*?)\"'", r'title="\1"', td_html_2)

        soup_td_2 = BeautifulSoup(td_html_2, "html.parser")
        arxiv_tag = soup_td_2.find("a", title="Arxiv")

        arxiv_link = None
        if arxiv_tag and arxiv_tag.get("href"):
            # 替换 \\/ 为 /（反转义）
            arxiv_link = arxiv_tag["href"].replace("\\/", "/")

            # 去重处理
            if arxiv_link in seen_links:
                continue
            seen_links.add(arxiv_link)

            print(f"No. {len(arxivs) + 1} paper:")
            print("arXiv URL:", arxiv_link)

            arxivs.append({
                "arxiv_url": arxiv_link
            })

    return arxivs



def save_csv(arxivs, path="cvpr2023arXiv.csv"):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "arxiv_url"
        ])
        writer.writeheader()
        for arxiv in arxivs:
            writer.writerow(arxiv)



def fetch_and_parse(batch):
    print(f" is grasping batch {batch}..." )
    try:
        html_text = fetch_html(batch)
        arxivs = parse_arxivs(html_text)
        print(f"batch {batch} captures {len(arxivs)} arxivs ")
        return arxivs
    except Exception as e:
        print(f"batch {batch} failed to grab: {e}")
        return []




def main():
    max_batch = 3
    all_arxivs = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(fetch_and_parse, batch) for batch in range(max_batch)]

        for future in concurrent.futures.as_completed(futures):
            arxivs = future.result()
            all_arxivs.extend(arxivs)

    save_csv(all_arxivs)
    print(f"\n has captured a total of {len(all_arxivs)} arxivs and saved them to the CSV file ")

if __name__ == "__main__":
    main()