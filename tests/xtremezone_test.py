"""
    Manual made test
    Must be keep in sync with the torrent file
"""
import re

import requests
import local_settings
from bs4 import BeautifulSoup


def parseSize(size):
    size_gb = ['gb', 'gib']
    size_mb = ['mb', 'mib']
    size_kb = ['kb', 'kib']


    size_raw = size.lower()
    size = float(re.sub(r'[^0-9.]', '', size).strip())

    for s in size_gb:
        if s in size_raw:
            return size * 1024

    for s in size_mb:
        if s in size_raw:
            return size

    for s in size_kb:
        if s in size_raw:
            return size / 1024

    return 0


urls = {
    'test': 'https://www.myxz.org/',
    'login': 'https://www.myxz.org/takelogin.php',
    'login_check': 'https://www.myxz.org/my.php',
    'search': 'https://www.myxz.org/browse.php?%s',
    'baseurl': 'https://www.myxz.org/%s',
}

test_url = 'https://www.myxz.org/browse.php?search=life+2017&incldead=0&c29=1'

session = requests.Session()
result = session.post('https://www.myxz.org/takelogin.php', {'username': local_settings.USERNAME, 'password': local_settings.PASSWORD})

if not 'logout.php' in result.text.lower():
    print('Login failed')
else:
    result = session.get(test_url)
    html = BeautifulSoup(result.text)

    results = []
    try:
        torrent_rows = html.find_all("tr", class_="browse")
        # Continue only if at least one Release is found
        if not torrent_rows:
            print("Data returned from provider does not contain any torrents")
        else:
            for result in torrent_rows:
                cells = result.find_all("td")
                title = cells[1].find("a").find("b").getText(strip=True)
                download_url = urls['baseurl'] % cells[2].find_all(href=re.compile("dwn.php"))[0]["href"]
                if not all([title, download_url]):
                    print('No torrent title and download url.')
                    continue

                seeders = int(''.join([s for s in cells[8].getText(strip=True) if s.isdigit()]))
                leechers = int(''.join([s for s in cells[9].getText(strip=True) if s.isdigit()]))

                detail_url = urls['baseurl'] % cells[1].find("a")["href"]
                torrent_id = detail_url.split('=')[1].split('&')[0]
                torrent_size = cells[6].getText(strip=True)
                size = parseSize(torrent_size) or -1

                results.append({
                    'id': torrent_id,
                    'name': title,
                    'size': size,
                    'seeders': seeders,
                    'leechers': leechers,
                    'url': download_url,
                    'detail_url': detail_url,
                })

    except Exception as e:
        print('Failed getting results: {}'.format(e))

    print(results)
session.close()