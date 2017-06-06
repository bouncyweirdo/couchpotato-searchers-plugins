from bs4 import BeautifulSoup
from couchpotato.core.helpers.variable import tryInt
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider
import re

log = CPLog(__name__)


class Base(TorrentProvider):

    urls = {
        'test': 'https://www.myxz.org/',
        'login': 'https://www.myxz.org/takelogin.php',
        'login_check': 'https://www.myxz.org/my.php',
        'search': 'https://www.myxz.org/browse.php?%s',
        'baseurl': 'https://www.myxz.org/%s',
    }

    http_time_between_calls = 1  # Seconds

    def _searchOnTitle(self, title, movie, quality, results):

        url = self.urls['search'] % self.buildUrl(title, movie, quality)
        data = self.getHTMLData(url)

        if data:
            html = BeautifulSoup(data)

            try:
                torrent_rows = html.find_all("tr", class_="browse")
            # Continue only if at least one Release is found
                if not torrent_rows:
                    log.debug("Data returned from provider does not contain any torrents")
                else:
                    for result in torrent_rows:
                        cells = result.find_all("td")
                        title = cells[1].find("a").find("b").getText(strip=True)
                        download_url = self.urls['baseurl'] % cells[2].find_all(href=re.compile("dwn.php"))[0]["href"]
                        if not all([title, download_url]):
                            log.debug('No torrent title and download url.')
                            continue

                        seeders = tryInt(''.join([s for s in cells[6].getText(strip=True) if s.isdigit()]))
                        leechers = tryInt(cells[7].getText(strip=True))

                        detail_url = self.urls['baseurl'] % cells[1].find("a")["href"]
                        torrent_id = detail_url.split('=')[1].split('&')[0]
                        torrent_size = cells[5].getText(strip=True)
                        size = self.parseSize(torrent_size) or -1

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
                log.error('Failed getting results from {}: {}'.format(self.getName(), e))

        else:
            log.debug('No search results found.')

    def getLoginParams(self):
        log.info('Logging in to www.myxz.org with user [{}]'.format(self.conf('username')))
        return {
            'username': self.conf('username'),
            'password': self.conf('password'),
            'ssl': 'yes',
        }

    @staticmethod
    def loginSuccess(output):
        return 'logout.php' in output.lower()

    loginCheckSuccess = loginSuccess
