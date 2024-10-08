from urllib.parse import urlparse, urljoin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import yaml
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from serpapi import DuckDuckGoSearch as _RunSearch
import requests


class SearchEngine:
    def __init__(self):
        self.last_search = {"res": [], "prompt": ""}
        #with open(r'/var/www/html/keys/keys.yaml') as keys_file: #Server Side
        with open(r'keys/keys.yaml') as keys_file:
            self.key = yaml.load(keys_file, yaml.FullLoader)['keys']['web-search']['serp-api']

    def update_links(self, prompt, start_entry=0, search_website=None):
        if search_website is not None:
            prompt += f' site:{search_website}'
        params = {
            "q": prompt,
            "engine": "duckduckgo",
            "api_key": self.key,
            "start": start_entry
        }

        search = _RunSearch(params)
        raw_search_results = search.get_dict()

        results = []
        if 'organic_results' not in raw_search_results:
            print("\u001b[31mMISSING SEARCH RESULTS:", raw_search_results)
        for curr_raw_result in raw_search_results["organic_results"]:
            results.append({
                'url': curr_raw_result["link"],
                'icon': curr_raw_result.get("favicon", None),
                'title': curr_raw_result.get("title", None)
            })

        self.last_search["res"] = results
        self.last_search["prompt"] = prompt

    def get_urls_by_indices(self, first=0, last=25, get_logos=False):
        links = self.last_search['res']
        if not first <= last <= len(links):
            print(f"\u001b[33mBad arguments: requesting [{first, last}] pages while only {len(links)} are available")

        return links[first:last]

    def get_first_website(self):
        return self.get_website(0)

    def get_website(self, link_number=None, url=None):
        if (link_number is None) == (url is None):
            print("\u001b[31mError: Cannot specify both link number and url, has to be just one of those\u001b[0m")
            return

        urls = list(map(lambda item: item['url'], self.last_search['res']))
        if url is not None and url in urls:
            link_number = urls.index(url)
            website_url = self.last_search["res"][link_number]['url']
        elif link_number is not None:
            website_url = self.last_search["res"][link_number]['url']
        else:
            print("\u001b[31mError: Invalid argument was provided\u001b[0m")
            return

        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--disable-browser-side-navigation')
        options.add_argument("window-size=19200,10800")
        driver = webdriver.Chrome(options=options)

        driver.get(website_url)
        WebDriverWait(driver, 10).until(lambda driver: len(driver.find_elements(By.XPATH, "//body/*")) > 0)
        website_content = driver.page_source

        driver.quit()
        soup = BeautifulSoup(website_content, 'html.parser')
        link_tags = soup.find_all('link', rel='stylesheet')
        css_content = []
        for link in link_tags:
            css_url = link.get('href')
            if not bool(urlparse(css_url).netloc):
                css_url = urljoin(website_url, css_url)
            try:
                css_response = requests.get(css_url)
                if css_response.status_code == 200:
                    css_content.append(css_response.text)
                else:
                    return {
                        'url': website_url,
                        'html': soup.prettify(),
                        'title': self.last_search['res'][link_number]['title'],
                        'icon': self.last_search['res'][link_number]['icon'],
                        'error': f'The following code was returned: {css_response.status_code}'
                    }
            except Exception as e:
                print(f'\u001b[33mWarning! Exception happened: \n{e}\u001b[0m')

        return {
            'url': website_url,
            'title': self.last_search["res"][link_number]['title'],
            'icon': self.last_search["res"][link_number]['icon'],
            'html': soup.prettify(),
            'css': css_content
        }


# Use case:
if __name__ == '__main__':
    # Create the engine
    search_engine = SearchEngine()
    # Use update-links method to refresh the search results (stored inside the class).
    # Start entry is 0 by default, it's the pagination offset
    search_engine.update_links("Japanese car under 6000 dollars and 130k miles", start_entry=0, search_website=None)
    # Open link (default opens 0th link, otherwise use link_number argument)
    page = search_engine.get_website(url=search_engine.get_website(1)['url'])

    print('\n\n\n\u001b[32mHTML\u001b[0m\n', page['html'])
    print('\n\n\n\u001b[32mCSS\u001b[0m\n', page['css'])
    print()
