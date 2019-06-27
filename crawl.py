import os
import json
import codecs
import argparse
from tqdm import tqdm

import urllib
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# for linux


# for chrome
chrome_options = Options()
chrome_options.add_argument('blink-settings=imagesEnabled=false')  # no photo
chrome_options.add_argument('--headless')  # no ui
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(chrome_options=chrome_options)

# set max wait time
driver.set_page_load_timeout(5)
driver.set_script_timeout(5)

search_prefix = 'https://www.quora.com/search?q=%s'
web_prefix = 'https://www.quora.com%s'


def question2url(question):
    query = urllib.parse.quote(question)
    query.replace('%20', '+')
    url = search_prefix % query
    return url


def get_question_link(url):
    driver.get(url)
    search = BeautifulSoup(driver.page_source, 'lxml')
    for item in search.find_all("div", {"class": "pagedlist_item"}):
        node = item.contents[0].contents[0]
        metadata = json.loads(node['data-clog-metadata'])
        if metadata['query_index'] == 1:
            question = node.contents[0]
            title, content = question.contents
            link = web_prefix % title.find('a', href=True)['href']
            return link


def clean_date(date):
    date = date.replace('Answered', '').strip()
    return date


def get_answer_info(link):
    driver.get(link)
    page = BeautifulSoup(driver.page_source, 'lxml')
    raw_date = page.find('a', {'class': 'answer_permalink'}).get_text()
    date = clean_date(raw_date)
    content = ''
    for item in page.find_all('span', {'class': 'ui_qtext_rendered_qtext'}):
        if item.find_all('p'):
            content = item.get_text()
    return {
        'date': date,
        'content': content
    }


def get_question_info(link):
    driver.get(link)
    thread = BeautifulSoup(driver.page_source, 'lxml')
    # title
    node = thread.find('div', {'class': 'header'})
    node = node.contents[0].contents[0].contents[2]
    question = node.get_text()
    # answers
    answer_links = set()
    for item in thread.find_all('a', href=True):
        if link.split('/')[-1] + '/answer/' in item['href']:
            if item['href'] not in answer_links:
                answer_links.add(item['href'])
    answers = []
    for answer_link in answer_links:
        try:
            answer_link = web_prefix % answer_link
            answer = get_answer_info(answer_link)
            answers.append(answer)
        except:
            continue
    return {
        'link': link,
        'search_question': question,
        'answers': answers
    }


def crawl(question):
    url = question2url(question)
    link = get_question_link(url)
    data = get_question_info(link)
    return data


if __name__ == "__main__":
    prefix = 'questions/chunk_%s.tsv'
    output = 'crawled/chunk_%s.tsv'
    assert os.path.exists('crawled'), 'Please create dir `crawled` first.'

    parser = argparse.ArgumentParser()
    parser.add_argument('--ids', '-i', type=str, help='Chunk ids to be crawled.')
    args = parser.parse_args()

    ids = args.ids.strip().split(',')
    for idx in ids:
        try:
            num_idx = int(idx)
            assert 200 > num_idx >= 0
            print(f'Crawling {idx} ...')
        except:
            print(f"{idx} is not a true id.\nPlease input id from 0 to 89.")
            continue
        with codecs.open(prefix % idx, 'r', encoding='utf8') as f:
            lines = f.readlines()
        crawled_ids = set()
        try:
            with codecs.open(output % idx, 'r', encoding='utf8') as f:
                crawled_ids = set([line.split('\t')[0] for line in f.readlines()])
            print(f'Load {len(crawled_ids)} documents from {output % idx}')
        except:
            pass
        with codecs.open(output % idx, 'a', encoding='utf8') as w:
            for line in tqdm(lines):
                qid, question = line.strip().split('\t')
                if qid in crawled_ids:
                    continue
                try:
                    crawled = crawl(question)
                    crawled['qid'] = qid
                    crawled['question'] = question
                    w.write("%s\n" % json.dumps(crawled))
                except BaseException as e:
                    print('='*40)
                    print("%s\t%s" % (qid, e))
                    continue
    driver.close()
    driver.quit()

