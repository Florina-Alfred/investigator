import requests
from pprint import pprint
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class RepoLongevityData:
    name: str
    full_name: str
    description: str
    owner: str
    stars: int
    forks: int
    watchers: int
    open_issues_count: int
    topics: List[str]
    languages: Dict[str, int]
    num_contributors: int
    num_releases: int
    num_open_issues: int
    num_closed_issues: int
    num_open_prs: int
    num_closed_prs: int
    last_updated: str
    created_at: str
    pushed_at: str


REPO_OWNER = "sharkdp"
REPO_NAME = "fd"


# REPO_OWNER = "skim-rs"
# REPO_NAME = "skim"


def fetch_github_api(url, paginated=False):
    results = []
    page = 1
    while True:
        paged_url = url
        if paginated:
            if '?' in url:
                paged_url = f"{url}&page={page}&per_page=100"
            else:
                paged_url = f"{url}?page={page}&per_page=100"
        response = requests.get(paged_url)
        if (
            response.status_code == 403
            and "X-RateLimit-Remaining" in response.headers
            and response.headers["X-RateLimit-Remaining"] == "0"
        ):
            print(f"Rate limit exceeded for {paged_url}. Please try again later.")
            return None
        elif response.ok:
            data = response.json()
            if paginated:
                if not data or len(data) == 0:
                    break
                results.extend(data)
                if len(data) < 100:
                    break
                page += 1
            else:
                return data
        else:
            print(f"Failed to fetch {paged_url}: {response.status_code}")
            return None
    return results


def main():
    endpoints = {
        "repo": f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}",
        "contributors": f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contributors",
        "issues": f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues?state=all",
        "pulls": f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls?state=all",
        "releases": f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases",
        "topics": f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/topics",
        "languages": f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/languages",
    }
    all_data = {}
    paginated_keys = ["contributors", "issues", "pulls", "releases"]
    for key, url in endpoints.items():
        paginated = key in paginated_keys
        data = fetch_github_api(url, paginated=paginated)
        all_data[key] = data

    repo_data = all_data["repo"] if all_data["repo"] else {}
    contributors = all_data["contributors"] if all_data["contributors"] else []
    releases = all_data["releases"] if all_data["releases"] else []
    issues = all_data["issues"] if all_data["issues"] else []
    pulls = all_data["pulls"] if all_data["pulls"] else []
    topics = all_data["topics"].get("names", []) if all_data["topics"] else []
    languages = all_data["languages"] if all_data["languages"] else {}

    num_open_issues = len([i for i in issues if i.get("state") == "open" and not i.get("pull_request")])
    num_closed_issues = len([i for i in issues if i.get("state") == "closed" and not i.get("pull_request")])
    num_open_prs = len([p for p in pulls if p.get("state") == "open"])
    num_closed_prs = len([p for p in pulls if p.get("state") == "closed"])

    longevity_data = RepoLongevityData(
        name=repo_data.get("name", ""),
        full_name=repo_data.get("full_name", ""),
        description=repo_data.get("description", ""),
        owner=repo_data.get("owner", {}).get("login", ""),
        stars=repo_data.get("stargazers_count", 0),
        forks=repo_data.get("forks_count", 0),
        watchers=repo_data.get("watchers_count", 0),
        open_issues_count=repo_data.get("open_issues_count", 0),
        topics=topics,
        languages=languages,
        num_contributors=len(contributors),
        num_releases=len(releases),
        num_open_issues=num_open_issues,
        num_closed_issues=num_closed_issues,
        num_open_prs=num_open_prs,
        num_closed_prs=num_closed_prs,
        last_updated=repo_data.get("updated_at", ""),
        created_at=repo_data.get("created_at", ""),
        pushed_at=repo_data.get("pushed_at", "")
    )

    pprint(longevity_data)


if __name__ == "__main__":
    main()
