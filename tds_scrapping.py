import requests
import csv
import re


gt = ''
HEADERS = {'Authorization': f'token {gt}'}

LOCATION = "Chicago"
MIN_FOLLOWERS = 100

def get_chicago_users():
    users = []
    page = 1

    while True:
        url = f"https://api.github.com/search/users?q=location:{LOCATION}+followers:>{MIN_FOLLOWERS}&page={page}&per_page=100"
        response = requests.get(url, headers=HEADERS)
        data = response.json()

        if 'items' not in data:
            break

        users.extend(data['items'])
        page += 1

        if len(data['items']) < 100:
            break

    return users

def get_user_details(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def clean_company_name(company):
    if company:
        company = company.strip()
        company = re.sub(r"^@", "", company)
        company = company.upper()
    return company or ""

def get_user_repositories(username):
    repos = []
    page = 1
    print(f"Fetching repositories for {username}")
    while True:
        url = f"https://api.github.com/users/{username}/repos?page={page}&per_page=100"
        response = requests.get(url, headers=HEADERS)
        data = response.json()

        if not data or 'message' in data:
            break

        repos.extend(data)
        page += 1

        if len(data) < 100 or len(repos) >= 500:
            break

    return repos[:500]


def write_users_csv(users_data):
    with open("users.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["login", "name", "company", "location", "email", "hireable", "bio", "public_repos", "followers", "following", "created_at"])

        for user in users_data:
            writer.writerow([
                user.get("login", ""),
                user.get("name", ""),
                clean_company_name(user.get("company", "")),
                user.get("location", ""),
                user.get("email", ""),
                str(user.get("hireable", "")).lower() if user.get("hireable") is not None else "",
                user.get("bio", ""),
                user.get("public_repos", 0),
                user.get("followers", 0),
                user.get("following", 0),
                user.get("created_at", "")
            ])

def write_repositories_csv(repositories_data):
    with open("repositories.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["login", "full_name", "created_at", "stargazers_count", "watchers_count", "language", "has_projects", "has_wiki", "license_name"])

        for repo in repositories_data:
            writer.writerow([
                repo["owner"]["login"],
                repo.get("full_name", ""),
                repo.get("created_at", ""),
                repo.get("stargazers_count", 0),
                repo.get("watchers_count", 0),
                repo.get("language", ""),
                str(repo.get("has_projects", False)).lower(),
                str(repo.get("has_wiki", False)).lower(),
                str(repo.get("license", {}).get("key", "")) if repo.get("license") else ""

            ])

def main():

    chicago_users = get_chicago_users()
    users_data = []
    repositories_data = []


    for user in chicago_users:
        username = user["login"]
        user_details = get_user_details(username)
        users_data.append(user_details)


        user_repos = get_user_repositories(username)
        repositories_data.extend(user_repos)


    write_users_csv(users_data)
    write_repositories_csv(repositories_data)

    print("Completed Successfully")

main()
