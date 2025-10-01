![](images/arXiv.png)

# Scraping Accepted Paper Lists from CVPR, NeurIPS, ICLR, ICCV, AAAI, ACL, etc.

This project provides a web scraper for extracting historical accepted paper lists from the Paper Copilot website and supports bulk downloading from arXiv.
For example, the CVPR 2022 dataset can be scraped. The collected accepted paper lists can be used for statistical analysis, trend prediction, paper recommendation, and author collaboration network construction.

⸻

## 🔍 Project Overview
	-	Developed for the Paper Copilot website, using dynamic HTML parsing to extract information.
	-	Scraped fields include:
	-	title: Paper title
	-	session: Session / topic
	-	authors: List of authors
	-	affiliations: Author affiliations
	-	pdf_url: PDF link
	-	Supports multiple top-tier conferences, including CVPR, NeurIPS, ICLR, ICCV, AAAI, ACL, etc.
	-	Supports bulk downloading of arXiv source files and extraction of fields into TXT files.

⸻

## 🚀 Quick Start

‘’‘bsah

# Scrape accepted paper lists for different years or conferences (may require minor modifications)
python cvpr2022.py

# Bulk download arXiv source files
python arXiv_download.py

# Bulk translate arXiv files to text
python latex2txt/arXiv2txt.py

’‘‘


📧[choucisan@gmail.com]
