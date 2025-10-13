import urllib
from dataclasses import dataclass
import urllib.request
import feedparser

url = 'http://export.arxiv.org/api/query?search_query=ti:humanoid+safe&start=0&max_results=3'
# url = 'http://export.arxiv.org/api/query?search_query=all:humanoid&start=0&max_results=3'
data = urllib.request.urlopen(url)
data = feedparser.parse(data.read().decode('utf-8'))

@dataclass
class Paper:
    title: str
    summary: str
    link: str

papers = []
for entry in data.entries:
    papers.append(Paper(title=entry.title, summary=entry.summary, link=entry.link))

# print(papers)
print("-"*80)
for paper in papers:
    print(f"Title: {paper.title}\n\tSummary: {paper.summary}\n\n\tLink: {paper.link}\n\n")
print("-"*80)

