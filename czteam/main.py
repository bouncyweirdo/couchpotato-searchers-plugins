import time
from bs4 import BeautifulSoup
from couchpotato.core.helpers.variable import tryInt
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider

log = CPLog(__name__)


class Base(TorrentProvider):

    # Todo: Finish the parser

    urls = {
        'test': 'http://torrents.czteam.ro',
        'login': 'http://torrents.czteam.ro/takelogin.php',
        'login_check': 'http://torrents.czteam.ro/my.php',
        'search': 'http://torrents.czteam.ro/browse.php?%s',
        'baseurl': 'http://torrents.czteam.ro/%s',
    }

    http_time_between_calls = 1  # Seconds

    def _searchOnTitle(self, title, movie, quality, results):

        url = self.urls['search'] % self.buildUrl(title, movie, quality)
        data = self.getHTMLData(url)
        if data:
            html = BeautifulSoup(data)

            try:
                entries = html.find_all('tr', attrs={'id': 'torrent-row'})
                if not entries:
                    return False

                for result in entries[0:]:
                    log.info(result)
                    torrent_id = result['tid']
                    torrent_name = result.find('b').getText()
                    torrent_url = self.urls['baseurl'] % 'download/{}/{}.torrent'.format(torrent_id, torrent_name)
                    torrent_detail_url = self.urls['baseurl'] % 'details.php?id={}'.format(torrent_id)

                    results.append({
                        'id': torrent_id,
                        'name': torrent_name,
                        'size': 4000,
                        'url': torrent_url,
                        'detail_url': torrent_detail_url,
                    })
                    log.info(results)
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
