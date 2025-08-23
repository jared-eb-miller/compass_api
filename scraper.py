import requests
from bs4 import BeautifulSoup

url = "https://liberty-insight.symplicity.com/students/index.php?tab=sessions"
print('GET:', url)
response = requests.get(url)
print('HTTP CODE:', response.status_code)
print('ON URL:', response.url)


soup = BeautifulSoup(response.text, "html.parser")

print(soup.title.string)
# Example: print all links
for link in soup.find_all("a"):
    print(link.get("href"))