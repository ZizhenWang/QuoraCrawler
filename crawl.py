import os
import json
import codecs
import zipfile
import argparse
from tqdm import tqdm

import urllib
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

search_prefix = 'https://www.quora.com/search?q=%s'
web_prefix = 'https://www.quora.com%s'


class ProxyPool(object):

    pluginfile = 'proxy_auth_plugin.zip'
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """
    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """
    proxy = []

    def __init__(self, patient=-1):
        self.patient = patient
        self.counter = 0
        self.driver = None
        self.driver = self._get_driver()
        print("ProxyPool init succeed.")

    def angry(self):
        if self.patient > 0:
            self.counter += 1
            if self.counter == self.patient:
                self.counter = 0
                self.driver = self._get_driver()

    def _get_driver(self):
        if self.driver is not None:
            self.driver.close()
            self.driver.quit()

        chrome_options = Options()

        # proxy = self.proxy.pop(0)
        # self.proxy.append(proxy)
        # with zipfile.ZipFile(self.pluginfile, 'w') as zp:
        #     zp.writestr("manifest.json", self.manifest_json)
        #     zp.writestr("background.js",
        #                 self.background_js % (proxy['ip'], proxy['port'], proxy['user'], proxy['pwd']))
        #     chrome_options.add_extension(self.pluginfile)

        chrome_options.add_argument('blink-settings=imagesEnabled=false')  # no photo
        chrome_options.add_argument('--headless')  # no ui
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')

        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.set_page_load_timeout(10)
        driver.set_script_timeout(10)
        print("Get new webdriver.")
        return driver


def question2url(question):
    query = urllib.parse.quote(question)
    query.replace('%20', '+')
    url = search_prefix % query
    return url


def get_question_link(driver, url):
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


def get_answer_info(driver, link):
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


def get_question_info(driver, link):
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
            answer = get_answer_info(driver, answer_link)
            answers.append(answer)
        except:
            continue
    return {
        'search_question': question,
        'answers': answers
    }


def crawl(driver, qid, question):
    data = {'qid': qid, 'question': question}
    url = question2url(question)
    try:
        link = get_question_link(driver, url)
    except BaseException as e:
        raise ValueError("Get question %s (qid %s) link failed.\n"
                         "[ Error info ]:\n %s" % (question, qid, e))
    data['link'] = link
    try:
        q = get_question_info(driver, link)
    except BaseException as e:
        raise ValueError("Get question %s (qid %s) info failed.\n"
                         "[ Error info ]:\n %s" % (question, qid, e))
    data['search_question'] = q['search_question']
    data['answers'] = q['answers']
    return data


if __name__ == "__main__":
    prefix = 'questions/chunk_%s.tsv'
    output = 'crawled/chunk_%s.json'
    assert os.path.exists('crawled'), 'Please create dir `crawled` first.'

    parser = argparse.ArgumentParser()
    parser.add_argument('--ids', '-i', type=str, help='Chunk ids to be crawled.')
    args = parser.parse_args()

    ids = args.ids.strip().split(',')
    pool = ProxyPool()
    for idx in ids:
        # id validation
        try:
            num_idx = int(idx)
            assert 90 > num_idx >= 0
            print(f'Crawling {idx} ...')
        except:
            print(f"{idx} is not a true id.\nPlease input id from 0 to 89.")
            continue

        # load crawled ids
        with codecs.open(prefix % idx, 'r', encoding='utf8') as f:
            lines = f.readlines()
        crawled_ids = set()
        try:
            with codecs.open(output % idx, 'r', encoding='utf8') as f:
                crawled_ids = set([json.loads(line)['qid'] for line in f.readlines()])
            print(f'Load {len(crawled_ids)} documents from {output % idx}')
        except:
            pass

        # crawl data
        with codecs.open(output % idx, 'a', encoding='utf8') as w:
            for line in tqdm(lines):
                qid, question = line.strip().split('\t')
                if qid in crawled_ids:
                    continue
                try:
                    crawled = crawl(pool.driver, qid, question)
                    w.write("%s\n" % json.dumps(crawled))
                except BaseException as e:
                    print('='*40)
                    try:
                        print(e)
                    except BaseException:
                        continue
                    pool.angry()
                    continue
    # data = crawl(pool.driver, '0', 'When to repair or replace the auto glass ?')
    # print('='*40)
    # print(data)

