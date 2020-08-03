import requests
import bs4

"""Function that do web scraping and return result from
wikipedia"""

def url(word):
    res=requests.get("https://en.wikipedia.org/wiki/"+word)
    soup=bs4.BeautifulSoup(res.text,'lxml')
    para=soup.select('p')
    res=""
    if len(para)>5:
        for i in range(5):
            res+=para[i].getText()
    return res
