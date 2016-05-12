import os
import stat
import mimetypes
from urllib.parse import urlsplit

from pulsar.utils.httpurl import iri_to_uri


ONEMB = 2**20


class Component:
    """Base class for github components
    """
    def __init__(self, client, data=None):
        self.client = client
        if isinstance(data, dict):
            self.data = data
            self.id = self.id_from_data(data)
        else:
            self.data = {}
            self.id = data

    def __repr__(self):
        return self.api_url
    __str__ = __repr__

    def __getattr__(self, name):
        return getattr(self.client, name)

    def __getitem__(self, name):
        return self.data[name]

    @classmethod
    def id_from_data(cls, data):
        return data['id']

    async def get(self):
        """Get data for this component
        """
        response = await self.http.get(str(self), auth=self.auth)
        response.raise_for_status()
        self.data = response.json()
        return self.data

    async def delete(self):
        """Delete this component
        """
        response = await self.http.delete(str(self), auth=self.auth)
        response.raise_for_status()

    async def get_list(self, url, Comp=None, callback=None, limit=100, **data):
        """Get a list of this github component
        :param url: full url
        :param Comp: a :class:`.Component` class
        :param callback: Optional callback
        :param limit: Optional number of items to retrieve
        :param data: additional query data
        :return: a list of ``Comp`` objects with data
        """
        data = dict(((k, v) for k, v in data.items() if v))
        all_data = []
        if limit:
            data['per_page'] = min(limit, 100)
        while url:
            response = await self.http.get(url, json=data, auth=self.auth)
            response.raise_for_status()
            result = response.json()
            n = m = len(result)
            if callback:
                result = callback(result)
                m = len(result)
            all_data.extend(result)
            if limit and len(all_data) > limit:
                all_data = all_data[:limit]
                break
            elif m == n:
                data = None
                next = response.links.get('next', {})
                url = next.get('url')
            else:
                break
        return [Comp(self, data) for data in all_data] if Comp else all_data


class Issue(Component):
    type = 'issues'

    @property
    def api_url(self):
        return '%s/%s/%s' % (self.client, self.type, self.id)

    def comments(self, **data):
        """Return all comments for this commit
        """
        return self.get_list('%s/comments' % self, **data)


class Pull(Issue):
    type = 'pulls'


class Commit(Issue):
    type = 'commits'

    @classmethod
    def id_from_data(cls, data):
        return data['sha']


class Release(Issue):
    type = 'releases'

    @classmethod
    def id_from_data(cls, data):
        return data['id']

    async def assets(self, **kw):
        """Return assets for this release
        """
        data = await self.get_list('%s/assets' % self, **kw)
        return [Asset(self.client, d) for d in data]

    async def upload(self, filename, content_type=None):
        """Upload a file to a release

        :param filename: filename to upload
        :param content_type: optional content type
        :return: json object from github
        """
        name = os.path.basename(filename)
        if not content_type:
            content_type, _ = mimetypes.guess_type(name)
        if not content_type:
            raise ValueError('content_type not known')
        inputs = {'name': name}
        url = '%s%s/assets' % (self.uploads_url, urlsplit(self.api_url).path)
        url = iri_to_uri(url, inputs)
        info = os.stat(filename)
        size = info[stat.ST_SIZE]
        response = await self.http.post(
            url, data=stream_upload(filename), auth=self.auth,
            headers={'content-type': content_type,
                     'content-length': str(size)})
        response.raise_for_status()
        return Asset(self.client, response.json())


class Asset(Issue):
    type = 'releases/assets'


def stream_upload(filename):
    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(ONEMB)
            if not chunk:
                break
            yield chunk
