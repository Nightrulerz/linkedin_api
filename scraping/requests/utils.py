from random import choice
from scraping.requests.useragents import user_agents



def get_browser_data():
    # Can add more browsers and versions
    return choice([
        {"impersonate": "chrome110", "browser": "chrome", "version": "110"},
        {"impersonate": "chrome119", "browser": "chrome", "version": "119"},
        {"impersonate": "chrome107", "browser": "chrome", "version": "107"},
        {"impersonate": "chrome104", "browser": "chrome", "version": "104"},
        {"impersonate": "chrome101", "browser": "chrome", "version": "101"},
        {"impersonate": "chrome100", "browser": "chrome", "version": "100"},
        {"impersonate": "chrome99", "browser": "chrome", "version": "99"},
    ])
    
def get_request_data():
    request_data = get_browser_data()
    useragent = choice(user_agents["chrome"][request_data["version"]])
    request_data["useragent"] = useragent
    return request_data
