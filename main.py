import requests
from bs4 import BeautifulSoup
import json
import os
import csv


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
}


def write_index_html():
    req = requests.get("https://vim.rtorr.com/", headers=headers)
    print(req.status_code)
    with open(f"data/htmls/index.html", 'w') as file:
        file.write(req.text)
    print(f"index.html writed")


def get_index_soup():
    with open("data/htmls/index.html") as file:
        src = file.read()
    return BeautifulSoup(src, "lxml")
    

def find_pages(soup):
    title = soup.find("h3", id_="languages")
    print(title)
    #items = title.find_next_sibling()
    #languages = items.find_childes()
    #print(items, languages)
    
    links = soup.css.select("a[lang]")
    return map(lambda link: link["href"].split('/')[-1], links)


def write_page_html(url):
    req = requests.get(url, headers=headers)
    print(req.status_code)
    with open(f"data/htmls/{url.split('/')[-2]}.html", 'w') as file:
        file.write(req.text)
    print(f"{url.split('/')[-2]}.html writed")


def get_page_soup(lang=''):
    with open(f"data/htmls/{lang}.html") as file:
        src = file.read()
    return BeautifulSoup(src, "lxml")


def delete_symbols(text, symbols = ('/', ' ', '-', '/', '(', ')', "__")):
    for s in symbols:
        while s in text:
            text = text.replace(s, '_')
    return text.strip('_')


def find_page_data(soup, lang=''):
    titles = soup.css.select("div:has(kbd)>h2")
    data = {}
    for title in titles:
        title_text = delete_symbols(title.text)
        data[title_text] = {}

        ul = title.find_next_sibling()
        items = ul.find_all("li")
        wells = None
        well = ul.find_next_sibling()
        if well is not None:
            wells = [well.text.split("Tip")[-1].strip("\n ")]
            other = well.find_next_sibling()
            if other is not None and other.name == "ul":
                items.extend(other.find_all("li"))
            elif other is not None and other.name=="div":
                wells.append(other.text.split("Tip")[-1].strip("\n "))
            #print(wells, sep="\n", end="\n"*2)
            data[title_text]["wells"] = wells
        for c, i in enumerate(items):
            full_item = i.text.strip(" \n").split('-')
            data[title_text][f"item_{c+1}"] = {"keys": full_item[0].rstrip(),
                                               "description": full_item[1].lstrip()}
    return data


def write_all_json_data(lang, datas):
    with open(f"data/all_data/{lang}.json", 'w') as file:
        json.dump(datas, file, indent=4, ensure_ascii=False)


def write_json_data(lang, title, text):
    with open(f"data/{lang}/{title}.json", "w") as file:
        #print(value)
        json.dump(text, file, indent=4, ensure_ascii=False)
    #print(lang, key)


def write_csv_data(lang, title, text):
    with open(f"data/{lang}/{title}.csv", "w") as file:
        #print(text.values())
        writer = csv.writer(file)
        for m in text.values():
            if isinstance(m, dict):
                writer.writerow(m.values())
                #print(m.keys())
            else:
                writer.writerow(m)
            #for n in m:
                #print(n, type(n), m, type(m))
                #if isinstance(n, dict):
                #    print(True, n.values())
                #    writer.writerow(n.values())
                #else:
                #    writer.writerow(m)



def main():
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/all_data", exist_ok=True)
    os.makedirs("data/htmls", exist_ok=True)
    
    write_index_html()
    soup = get_index_soup()
    langs = find_pages(soup)
    for lang in langs:
        print(lang)
        os.makedirs(f"data/{lang}/", exist_ok=True)

        write_page_html(f"https://vim.rtorr.com/lang/{lang}/")
        soup = get_page_soup(lang)
        data = find_page_data(soup, lang)

        write_all_json_data(lang, data)
        for key, value in data.items():
            write_json_data(lang, key, value)
            write_csv_data(lang, key, value)


if __name__ == "__main__":
    main()
