import time
from bs4 import BeautifulSoup
from couchpotato.core.helpers.variable import tryInt
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider

log = CPLog(__name__)


class Base(TorrentProvider):

    urls = {
        'test': 'http://scenefz.net',
        'login': 'http://scenefz.net/takelogin.php',
        'login_check': 'http://scenefz.net/my.php',
        'search': 'http://scenefz.net/browse.php?%s',
        'baseurl': 'http://scenefz.net/%s',
    }

    http_time_between_calls = 1  # Seconds

    def _searchOnTitle(self, title, movie, quality, results):

        url = self.urls['search'] % self.buildUrl(title, movie, quality)
        data = self.getHTMLData(url)
        if data:
            html = BeautifulSoup(data)

            try:
                result_table = html.find('table', attrs={'id': 'torrenttable'})
                if not result_table:
                    return False

                entries = result_table.find_all('tr')

                for result in entries[0:]:
                    try:
                        if result['id'] == 'tdivider_title':
                            continue
                    except: pass
                    if result.find_all(id='tdivider_title'):
                        continue

                    all_cells = result.find_all('td')

                    torrent = all_cells[1].find('a')
                    download = all_cells[5].find_all('a')[2]

                    torrent_id = torrent['href']
                    torrent_id = torrent_id.replace('details.php?id=', '')

                    torrent_name = torrent.getText()

                    torrent_size = self.parseSize(str(all_cells[2].getText()).replace(',', '.'))
                    seed_leech = all_cells[4].find_all('a')
                    torrent_seeders = tryInt(seed_leech[0].getText())
                    torrent_leechers = tryInt(seed_leech[1].getText())
                    torrent_url = self.urls['baseurl'] % download['href']
                    torrent_detail_url = self.urls['baseurl'] % torrent['href']

                    results.append({
                        'id': torrent_id,
                        'name': torrent_name,
                        'size': torrent_size,
                        'seeders': torrent_seeders,
                        'leechers': torrent_leechers,
                        'url': torrent_url,
                        'detail_url': torrent_detail_url,
                    })
            except Exception as e:
                log.error('Failed getting results from {}: {}'.format(self.getName(), e))

    def getLoginParams(self):
        log.info('Logging in to scenefz.net with user [{}]'.format(self.conf('username')))
        return {
            'username': self.conf('username'),
            'password': self.conf('password'),
        }

    @staticmethod
    def loginSuccess(output):
        return 'loading...' in output.lower()

    loginCheckSuccess = loginSuccess
