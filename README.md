![](images/arXiv.png)


# 爬取CVPR、NeurIPS、ICLR、ICCV、AAAI、ACL 等Accepted Paper List


一个用于爬取Paper Copilot网站上历年顶会接收论文列表的爬虫脚本并支持arxiv批量下载，以cvpr2022为例。爬取接受paper list 数据可以用于统计分析、趋势预测、论文推荐、作者合作网络构建等科研辅助任务。

## 🔍 项目简介

- 本项目面向 Paper Copilot 网站开发，目标是爬取其提供的顶会接收论文列表。
- 网站内容采用 AJAX 异步加载 技术，项目通过解析动态 HTML 数据实现信息提取。
- 爬取字段包括：title（论文标题）、session（分会场/主题）、authors（作者列表）、affiliations（作者单位）、pdf_url（PDF 链接）。
- 支持多个顶会，如 CVPR、NeurIPS、ICLR、ICCV、AAAI、ACL 等。
- 支持arxiv批量下载tex源文件

## 🚀 快速启动

```bash
# 爬取不同年份、不同会议需要稍微修改
python cvpr2022.py

#批量下载arxiv文件
python arXiv_download.py
```


📮[choucisan@gmail.com]
