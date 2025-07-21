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
        "year": 2022,
        "mode": "detail",
        "track": "main"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.text



def parse_papers(html_text):
    soup = BeautifulSoup(html_text, "html.parser")

    rows = soup.select("tr")
    papers = []

    for i, row in enumerate(rows):
        print(f"\nNo. {i + 1} paper:")

        tds = row.find_all("td")

        td_html_2 = tds[2].decode_contents()
        td_html_2 = html.unescape(td_html_2)

        title_match = re.search(r'^(.*?)<br', td_html_2)
        title = title_match.group(1).strip() if title_match else "no title"

        soup_td_2 = BeautifulSoup(td_html_2, "html.parser")
        pdf_tag = soup_td_2.find("a", href=True)
        pdf_url = pdf_tag['href'] if pdf_tag else None
        if pdf_url:
            pdf_url = pdf_url.strip('\'"')
            pdf_url = pdf_url.replace('\\/', '/')
            pdf_url = pdf_url.replace('\\', '').replace('"', '').replace("'", "")
        else:
            pdf_url = None

        td_html_3 = tds[3].decode_contents()
        td_html_3 = html.unescape(td_html_3)
        td_html_3 = td_html_3.replace('\\"', '"').replace("\\/", "/").replace("\\", "")

        session_match = re.search(r'<small>(.*?)</small>', td_html_3, re.DOTALL)
        session = session_match.group(1).strip() if session_match else " no Session"

        td_html_4 = tds[4].decode_contents()
        td_html_4 = html.unescape(td_html_4)
        td_html_4 = td_html_4.replace('\\"', '"').replace('\\/', '/')
        td_html_4 = td_html_4.replace("class='\"author-link\"'", 'class="author-link"')
        td_html_4 = td_html_4.replace('="\"', '="').replace('\""', '"')

        soup_td_4 = BeautifulSoup(td_html_4, 'html.parser')
        authors = [span.get_text(strip=True) for span in soup_td_4.find_all('span', class_='author-link')]
        authors = authors[:2]

        td_html_5 = tds[5].decode_contents()
        td_html_5 = html.unescape(td_html_5)
        td_html_5 = td_html_5.replace('\\"', '"').replace('\\/', '/')



        abbrs = re.findall(r'data-abbr=[\'"]+([^\'"]+)[\'"]+', td_html_5)

        affiliations = []
        for abbr in abbrs:
            if abbr not in affiliations:
                affiliations.append(abbr)
            if len(affiliations) == 1:
                break


        print(" title :", title)
        print(" direction :", session)
        print(" Lead author :", ", ".join(authors))
        print(" Main unit :", affiliations[0])
        print("PDF:", pdf_url)

        paper = {
            "title": title,
            "session": session,
            "authors":", ".join(authors),
            "affiliations": affiliations[0],
            "pdf_url": pdf_url,
        }
        papers.append(paper)

    return papers



def save_csv(papers, path="cvpr2022.csv"):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "title", "session", "authors", "affiliations", "pdf_url"
        ])
        writer.writeheader()
        for paper in papers:
            writer.writerow(paper)


def fetch_and_parse(batch):
    print(f" is grasping batch {batch}..." )
    try:
        html_text = fetch_html(batch)
        papers = parse_papers(html_text)
        print(f"batch {batch} captures {len(papers)} papers ")
        return papers
    except Exception as e:
        print(f"batch {batch} failed to grab: {e}")
        return []




def main():
    max_batch = 3
    all_papers = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(fetch_and_parse, batch) for batch in range(max_batch)]

        for future in concurrent.futures.as_completed(futures):
            papers = future.result()
            all_papers.extend(papers)

    save_csv(all_papers)
    print(f"\n has captured a total of {len(all_papers)} papers and saved them to the CSV file ")

if __name__ == "__main__":
    main()


