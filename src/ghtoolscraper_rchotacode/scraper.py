from ghtoolscraper_rchotacode._fetcher import fetch_page, fetch_repo, fetch_content
import os
from multiprocessing.pool import ThreadPool
from threading import Lock
from ghtoolscraper_rchotacode._rate_limit_exception import RateLimitException
from itertools import cycle
import time
import json

class ThreadedScraper:
    def __init__(self, query : str, tokens : list, per_page : int = 10, max_threads : int = 5, 
                 output_dir : str = "./repos", timeout : int = 5):
        self.query = query
        self.per_page = per_page
        self.max_threads = max_threads
        self.lock = Lock()
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.tokens = cycle(tokens)
        self.timeout = timeout
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Mozilla/5.0',
            'Authorization': f'Bearer {next(self.tokens)}'
        }
    
    def _tokenized_request(self, func, *args) -> dict:
        stop = False
        response = None
        while not stop:
            try:
                response = func(*args, headers=self.headers)
                stop = True
            except RateLimitException:
                self.headers['Authorization'] = f'Bearer {next(self.tokens)}'
                time.sleep(self.timeout)
            except Exception as e:
                print(f"Error: {e}")
                stop = True
        return response


    def scrape(self, page_start = 1):
        threads = ThreadPool(self.max_threads)

        first_page = self._tokenized_request(fetch_page, self.query, page_start, self.per_page)
        total_count = first_page['total_count']

        final_run = 1 if total_count % self.per_page == 0 else 0
        total_runs = (total_count // self.per_page) - page_start + final_run

        for page in range(page_start, total_runs):
            page_results = self._tokenized_request(fetch_page, self.query, page, self.per_page)
            if len(page_results['items']) == 0:
                break
            for repo in page_results['items']:
                threads.apply(self._scrape_page, args=(repo, page))
        threads.close()

    def _scrape_page(self, repo, page):
        with self.lock:
            try:
                os.makedirs(f'{self.output_dir}/page_{page}/{repo["full_name"]}', exist_ok=False)
            except FileExistsError:
                print(f"Directory {self.output_dir}/page_{page}/{repo['full_name']} already exists. Skipping.")
                return
        tree_url = f"https://api.github.com/repos/{repo['full_name']}/git/trees/{repo['default_branch']}?recursive=1"
        tree = self._tokenized_request(fetch_repo, tree_url)
        if 'tree' not in tree:
            print(f"Error fetching tree for {repo['full_name']}: {tree.get('message', 'Unknown error')}")
            return
        nested_tree, index_map = self._nest_tree(tree['tree'])
        
        with open(f"{self.output_dir}/page_{page}/{repo['full_name']}/tree.json", 'w') as f:
            json.dump({
                "tree": nested_tree,
                "index_map": index_map,
                }, f)
            print(f"Saved tree for {repo['full_name']} to {self.output_dir}/page_{page}/{repo['full_name']}/tree.json")


    def _nest_tree(self, tree):
        nested_tree = {}
        index_map = {}
        index = 0
        for item in tree:
            if item['type'] == 'blob':
                current_level = nested_tree
                path = item['path'].split('/')
                if len(path) > 1:
                    for part in path[:-1]:
                        if part not in current_level:
                            current_level[part] = {}
                        current_level = current_level[part]
                current_level[path[-1]] = index
                index_map[index] = item['sha']
                index += 1
        return nested_tree, index_map
    
