import os
import csv
import shutil
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_source(number, path):
    url = f'https://arxiv.org/e-print/{number}'
    print('Downloading:', url)
    try:
        urllib.request.urlretrieve(url, path)
    except Exception as e:
        print(f' Failed to download {number}: {e}')


def download_source_with_cache(number, path):
    cache_dir = 'cache_arxiv'
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, 'last_downloaded_source.tar.gz')
    cache_number_path = os.path.join(cache_dir, 'last_arxiv_number.txt')

    if os.path.exists(cache_path) and os.path.exists(cache_number_path):
        last_number = open(cache_number_path).read().strip()
        if last_number == number:
            shutil.copyfile(cache_path, path)
            print(f' Cache hit for {number}')
            return

    download_source(number, path)
    shutil.copyfile(path, cache_path)
    with open(cache_number_path, 'w') as f:
        f.write(number)


def extract_arxiv_number(url):

    match = url.strip().split('/')[-1]
    return match.replace('.pdf', '')


def batch_download_from_csv(csv_path, save_dir='downloads/cvpr2022', max_workers=2):
    os.makedirs(save_dir, exist_ok=True)

    tasks = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get('pdf_url') or row.get('arxiv_url')
            if not url:
                print('Missing URL in row:', row)
                continue

            arxiv_number = extract_arxiv_number(url)
            save_path = os.path.join(save_dir, f'{arxiv_number}.tar.gz')

            if os.path.exists(save_path):
                print(f'Already exists: {arxiv_number}')
                continue

            tasks.append((arxiv_number, save_path))


    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download_source_with_cache, number, path) for number, path in tasks]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f'Error during downloading: {e}')


if __name__ == '__main__':
    batch_download_from_csv('cvpr2022arXiv.csv', max_workers=2)