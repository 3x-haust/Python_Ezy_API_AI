import requests
import base64
import json
import time
import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

os.makedirs("result", exist_ok=True)

def load_existing_data(filename="pytest_fastapi_code_collection.jsonl"):
    full_path = os.path.join("result", filename)
    repos = []
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    repo = json.loads(line)
                    repos.append(repo)
                except json.JSONDecodeError:
                    continue
    return {"repos": repos}

def load_checked_repos(filename="checked_repos.json"):
    full_path = os.path.join("result", filename)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"pytest_fastapi": [], "checked": []}

def load_date_tracking(filename="date_tracking.json"):
    full_path = os.path.join("result", filename)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "current_start_date": "2008-01-01", 
        "current_end_date": "2008-01-15",
        "final_end_date": "2025-03-20",
        "last_page": 1
    }

def save_data(data, filename="pytest_fastapi_code_collection.jsonl"):
    full_path = os.path.join("result", filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        for repo in data["repos"]:
            f.write(json.dumps(repo, ensure_ascii=False) + '\n')

def append_repo_data(repo_data, filename="pytest_fastapi_code_collection.jsonl"):
    full_path = os.path.join("result", filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(repo_data, ensure_ascii=False) + '\n')

def save_checked_repos(data, filename="checked_repos.json"):
    full_path = os.path.join("result", filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_date_tracking(data, filename="date_tracking.json"):
    full_path = os.path.join("result", filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_repo_data(repo_data):
    repo_owner = repo_data["repo_owner"]
    repo_name = repo_data["repo_name"]
    
    os.makedirs("result", exist_ok=True)
    filename = os.path.join("result", f"{repo_owner}_{repo_name}.jsonl")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps({"repo_info": {
            "repo_name": repo_name,
            "repo_owner": repo_owner,
            "repo_url": repo_data["repo_url"]
        }}, ensure_ascii=False) + '\n')
        
        for test_file in repo_data["test_files"]:
            f.write(json.dumps({"type": "test_file", "path": test_file["path"], "content": test_file["content"]}, ensure_ascii=False) + '\n')
        
        for source_file in repo_data["source_files"]:
            f.write(json.dumps({"type": "source_file", "path": source_file["path"], "content": source_file["content"]}, ensure_ascii=False) + '\n')
    
    print(f"Saved repository data to {filename}")

def get_processed_repos(data):
    return {f"{repo['repo_owner']}/{repo['repo_name']}" for repo in data["repos"]}

def get_next_page_url(response):
    links = response.headers.get('Link', '')
    if not links:
        return None
    
    for link in links.split(','):
        parts = link.split(';')
        if len(parts) == 2 and 'rel="next"' in parts[1]:
            return parts[0].strip()[1:-1]
    return None

class TokenManager:
    def __init__(self):
        self.tokens = self._load_tokens_from_env()
        self.current_token_index = 0
        self.token_reset_times = {token: 0 for token in self.tokens}
        
    def _load_tokens_from_env(self):
        tokens_str = os.environ.get('GITHUB_TOKENS', '')
        if not tokens_str:
            single_token = os.environ.get('TOKEN', '')
            return [single_token] if single_token else []
        return [token.strip() for token in tokens_str.split(',') if token.strip()]
    
    def get_current_token(self):
        if not self.tokens:
            return None
        return self.tokens[self.current_token_index]
    
    def rotate_token(self):
        if len(self.tokens) <= 1:
            return False
        
        self.current_token_index = (self.current_token_index + 1) % len(self.tokens)
        print(f"Rotating to token {self.current_token_index + 1}/{len(self.tokens)}")
        return True
    
    def update_token_reset_time(self, token, reset_time):
        self.token_reset_times[token] = reset_time
    
    def get_current_headers(self):
        token = self.get_current_token()
        headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if token:
            headers['Authorization'] = f"token {token}"
        return headers

async def handle_rate_limit(response, session, token_manager):
    remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
    
    current_token = token_manager.get_current_token()
    if current_token:
        token_manager.update_token_reset_time(current_token, reset_time)
    
    if remaining <= 5:
        if token_manager.rotate_token():
            print(f"Rate limit approaching, rotating to next token")
            return False
        
        current_time = time.time()
        sleep_time = reset_time - current_time + 10
        
        if sleep_time > 0:
            print(f"API rate limit reached for all tokens. Waiting {sleep_time:.0f} seconds...")
            while sleep_time > 0:
                hours, remainder = divmod(sleep_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                print(f"Remaining wait time: {int(hours)} hours {int(minutes)} minutes {int(seconds)} seconds")
                await asyncio.sleep(1)
                sleep_time -= 1
            return True
    
    return False

async def fetch_content(session, url, token_manager):
    headers = token_manager.get_current_headers()
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json(), response
            
            if response.status == 403 and 'rate limit' in (await response.text()).lower():
                if token_manager.rotate_token():
                    print(f"Rate limit hit, rotating token and retrying")
                    await asyncio.sleep(1)
                    return await fetch_content(session, url, token_manager)
            
            return None, response
    except Exception as e:
        print(f"Request error: {url} - {str(e)}")
        return None, None

async def process_repo_file(session, repo_owner, repo_name, file, file_type, repo_data, token_manager):
    file_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file["path"]}'
    file_data, file_response = await fetch_content(session, file_url, token_manager)
    
    if file_response:
        await handle_rate_limit(file_response, session, token_manager)
    
    if file_data and not isinstance(file_data, list) and 'content' in file_data:
        content = file_data.get('content', '')
        try:
            decoded_content = base64.b64decode(content).decode('utf-8', errors='ignore')
            
            file_info = {
                "path": file["path"],
                "content": decoded_content
            }
            
            repo_data[file_type].append(file_info)
            print(f"File added: {file['path']}")
        except Exception as e:
            print(f"File decoding error: {file['path']} - {str(e)}")

async def process_repository(session, repo_owner, repo_name, token_manager, result_data, checked_repos, processed_repos):
    repo_full_name = f"{repo_owner}/{repo_name}"
    
    if repo_full_name in processed_repos:
        print(f"Already processed repository: {repo_full_name}")
        return False
        
    if repo_full_name in checked_repos["checked"]:
        print(f"Already checked repository: {repo_full_name}")
        return False
    
    print(f"Checking repository: {repo_full_name}")
    
    repo_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/requirements.txt'
    req_data, req_response = await fetch_content(session, repo_url, token_manager)
    
    if req_response:
        await handle_rate_limit(req_response, session, token_manager)
    
    checked_repos["checked"].append(repo_full_name)
    save_checked_repos(checked_repos)
    
    if req_data and 'content' in req_data:
        content = req_data.get('content', '')
        decoded_content = base64.b64decode(content).decode('utf-8', errors='ignore')
        
        if 'pytest' in decoded_content.lower() and ('fastapi' in decoded_content.lower() or 'fast-api' in decoded_content.lower()):
            print(f'Found pytest and FastAPI: {repo_full_name}')
            checked_repos["pytest_fastapi"].append(repo_full_name)
            save_checked_repos(checked_repos)
            
            repo_data = {
                "repo_name": repo_name,
                "repo_owner": repo_owner,
                "repo_url": f"https://github.com/{repo_owner}/{repo_name}",
                "test_files": [],
                "source_files": []
            }
            
            repo_info_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}'
            repo_info, repo_info_response = await fetch_content(session, repo_info_url, token_manager)
            
            if repo_info_response:
                await handle_rate_limit(repo_info_response, session, token_manager)
            
            default_branch = 'main'
            if repo_info:
                default_branch = repo_info.get('default_branch', 'main')
            
            tree_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/git/trees/{default_branch}?recursive=1'
            tree_data, tree_response = await fetch_content(session, tree_url, token_manager)
            
            if tree_response:
                await handle_rate_limit(tree_response, session, token_manager)
            
            if tree_data:
                test_files = []
                source_files = []
                
                for file in tree_data.get('tree', []):
                    if file['type'] == 'blob' and file['path'].endswith('.py'):
                        if file['path'].startswith('tests/') or '/tests/' in file['path'] or file['path'].startswith('test_') or '/test_' in file['path']:
                            test_files.append(file)
                        elif 'test' not in file['path'].lower():
                            source_files.append(file)
                
                file_tasks = []
                
                for file_type, files in [("test_files", test_files), ("source_files", source_files)]:
                    for file in files[:50]:
                        task = process_repo_file(session, repo_owner, repo_name, file, file_type, repo_data, token_manager)
                        file_tasks.append(task)
                
                await asyncio.gather(*file_tasks)
                
                result_data["repos"].append(repo_data)
                append_repo_data(repo_data)
                
                save_repo_data(repo_data)
                
                print(f"Repository processing complete: {repo_full_name} (Test files: {len(repo_data['test_files'])}, Source files: {len(repo_data['source_files'])})")
                return True
    
    return False

async def collect_pytest_fastapi_repos_async():
    result_filename = "pytest_fastapi_code_collection.jsonl"
    checked_filename = "checked_repos.json"
    date_tracking_filename = "date_tracking.json"
    
    result_data = load_existing_data(result_filename)
    checked_repos = load_checked_repos(checked_filename)
    date_tracking = load_date_tracking(date_tracking_filename)
    
    processed_repos = get_processed_repos(result_data)
    
    token_manager = TokenManager()
    if not token_manager.tokens:
        print("Warning: No GitHub API tokens found. API rate limits will be very restrictive.")
    else:
        print(f"Loaded {len(token_manager.tokens)} GitHub tokens")
    
    current_start_date = datetime.strptime(date_tracking["current_start_date"], "%Y-%m-%d")
    current_end_date = datetime.strptime(date_tracking["current_end_date"], "%Y-%m-%d")
    final_end_date = datetime.strptime(date_tracking["final_end_date"], "%Y-%m-%d")
    page = date_tracking["last_page"]
    
    print(f"Search date range: {current_start_date.date()} ~ {current_end_date.date()}")
    print(f"Page: {page}")
    
    full_result_path = os.path.join("result", result_filename)
    if not os.path.exists(full_result_path):
        os.makedirs(os.path.dirname(full_result_path), exist_ok=True)
        with open(full_result_path, 'w', encoding='utf-8') as f:
            pass
    
    total_repos_checked = 0
    concurrency_limit = 100
    
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            while current_start_date <= final_end_date:
                date_range = f"created:{current_start_date.date()}..{current_end_date.date()}"
                base_url = f'https://api.github.com/search/repositories?q=language:Python+{date_range}&sort=stars&per_page=100&page={page}'
                
                print(f"\nProcessing date range {current_start_date.date()} ~ {current_end_date.date()}, page {page}...\n")
                
                data, response = await fetch_content(session, base_url, token_manager)
                
                if response:
                    await handle_rate_limit(response, session, token_manager)
                    
                    if response.status != 200:
                        print(f"API request failed: Status code {response.status}")
                        text = await response.text()
                        print(text)
                        
                        await asyncio.sleep(60)
                        continue
                    
                    next_url = get_next_page_url(response)
                
                if not data:
                    print("No data received from API")
                    await asyncio.sleep(60)
                    continue
                
                items_count = len(data.get('items', []))
                total_count = data.get('total_count', 0)
                
                print(f"Total {total_count} repositories in this query.")
                print(f"Found {items_count} repositories on this page.")
                
                if items_count == 0:
                    print("No results on this page.")
                    
                    if page > 10 or total_count <= page * 100:
                        current_start_date = current_end_date + timedelta(days=1)
                        current_end_date = current_start_date + timedelta(days=14)
                        
                        if current_end_date > final_end_date:
                            current_end_date = final_end_date
                        
                        page = 1
                        
                        date_tracking["current_start_date"] = current_start_date.strftime("%Y-%m-%d")
                        date_tracking["current_end_date"] = current_end_date.strftime("%Y-%m-%d")
                        date_tracking["last_page"] = page
                        save_date_tracking(date_tracking)
                        
                        print(f"Moving to next date range: {current_start_date.date()} ~ {current_end_date.date()}")
                        continue
                    else:
                        page += 1
                        date_tracking["last_page"] = page
                        save_date_tracking(date_tracking)
                        print(f"Moving to next page: {page}")
                        continue
                
                tasks = []
                for repo in data.get('items', []):
                    repo_name = repo['name']
                    repo_owner = repo['owner']['login']
                    total_repos_checked += 1
                    
                    task = process_repository(
                        session, repo_owner, repo_name, token_manager, 
                        result_data, checked_repos, processed_repos
                    )
                    tasks.append(task)
                    
                    if len(tasks) >= concurrency_limit:
                        await asyncio.gather(*tasks)
                        tasks = []
                
                if tasks:
                    await asyncio.gather(*tasks)
                
                print(f"\nCurrent progress:")
                print(f"- Total repositories checked: {len(checked_repos['checked'])}")
                print(f"- Total pytest+FastAPI repositories: {len(checked_repos['pytest_fastapi'])}")
                print(f"- Total repositories with data collected: {len(result_data['repos'])}")
                print(f"- Current date range: {current_start_date.date()} ~ {current_end_date.date()}")
                print(f"- Current page: {page}")
                
                if next_url and page < 10:
                    page += 1
                    date_tracking["last_page"] = page
                    save_date_tracking(date_tracking)
                    print(f"Moving to next page: {page}")
                else:
                    current_start_date = current_end_date + timedelta(days=1)
                    current_end_date = current_start_date + timedelta(days=14)
                    
                    if current_end_date > final_end_date:
                        current_end_date = final_end_date
                    
                    page = 1
                    
                    date_tracking["current_start_date"] = current_start_date.strftime("%Y-%m-%d")
                    date_tracking["current_end_date"] = current_end_date.strftime("%Y-%m-%d")
                    date_tracking["last_page"] = page
                    save_date_tracking(date_tracking)
                    
                    print(f"Moving to next date range: {current_start_date.date()} ~ {current_end_date.date()}")
                
                await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
        print(f"Last processed date range: {current_start_date.date()} ~ {current_end_date.date()}, page: {page}")
        
        date_tracking["current_start_date"] = current_start_date.strftime("%Y-%m-%d")
        date_tracking["current_end_date"] = current_end_date.strftime("%Y-%m-%d")
        date_tracking["last_page"] = page
        save_date_tracking(date_tracking)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        print(f"Last processed date range: {current_start_date.date()} ~ {current_end_date.date()}, page: {page}")
        
        date_tracking["current_start_date"] = current_start_date.strftime("%Y-%m-%d")
        date_tracking["current_end_date"] = current_end_date.strftime("%Y-%m-%d")
        date_tracking["last_page"] = page
        save_date_tracking(date_tracking)
    
    print(f"\nProgram terminated. Checked {total_repos_checked} repositories.")
    print(f"Total {len(checked_repos['checked'])} repositories checked.")
    print(f"Found {len(checked_repos['pytest_fastapi'])} repositories with both pytest and FastAPI.")
    print(f"Data for {len(result_data['repos'])} repositories saved to {result_filename}.")
    print(f"Last processed date range info saved to {date_tracking_filename}.")

async def main():
    token_manager = TokenManager()
    if not token_manager.tokens:
        print("Warning: No GitHub API tokens configured. API rate limits will be very restrictive.")
        print("Configure GitHub tokens in .env file as GITHUB_TOKENS=token1,token2,token3")
    else:
        print(f"Loaded {len(token_manager.tokens)} GitHub tokens")
    
    await collect_pytest_fastapi_repos_async()

if __name__ == "__main__":
    asyncio.run(main())