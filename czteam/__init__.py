from couchpotato.core.helpers.encoding import tryUrlencode
from couchpotato.core.media.movie.providers.base import MovieProvider

from .main import Base


def autoload():
    return CzTeam()


class CzTeam(MovieProvider, Base):
    cat_ids = [
        ([37], ['3d']),
        ([33], ['720p', '1080p']),
        ([28], ['dvdr']),
        ([20], ['brrip', 'dvdrip', 'scr', 'r5', 'tc', 'ts', 'cam']),
    ]
    cat_backup_id = 1

    def buildUrl(self, title, media, quality):
        query = tryUrlencode({
            'search': '%s %s' % (title, media['info']['year']),
            'cat': self.getCatId(quality)[0],
            'incldead': 0,
            'tip': 1,
        })
        return query


config = [{
    'name': 'czteam',
    'groups': [
        {
            'tab': 'searcher',
            'list': 'torrent_providers',
            'name': 'CzTeam',
            'description': '<a href="http://torrents.czteam.ro">CzTeam</a>',
            'wizard': True,
            'options': [
                {
                    'name': 'enabled',
                    'type': 'enabler',
                    'default': False,
                },
                {
                    'name': 'username',
                    'default': '',
                },
                {
                    'name': 'password',
                    'default': '',
                    'type': 'password',
                },
                {
                    'name': 'seed_ratio',
                    'label': 'Seed ratio',
                    'type': 'float',
                    'default': 1,
                    'description': 'Will not be (re)moved until this seed ratio is met.',
                },
                {
                    'name': 'seed_time',
                    'label': 'Seed time',
                    'type': 'int',
                    'default': 48,
                    'description': 'Will not be (re)moved until this seed time (in hours) is met.',
                },
                {
                    'name': 'extra_score',
                    'advanced': True,
                    'label': 'Extra Score',
                    'type': 'int',
                    'default': 0,
                    'description': 'Starting score for each release found via this provider.',
                }
            ],
        },
    ],
}]
