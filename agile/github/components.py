import os
import mimetypes
from urllib.parse import urlsplit

from pulsar.utils.httpurl import iri_to_uri


ONEMB = 2**20


class Component:

    def __init__(self, client):
        self.client = client

    def __repr__(self):
        return self.api_url
    __str__ = __repr__

    def __getattr__(self, name):
        return getattr(self.client, name)

    async def get_list(self, url, callback=None, **data):
        all_data = []
        while url:
            response = await self.http.get(url, data=data, auth=self.auth)
            response.raise_for_status()
            result = response.json()
            n = m = len(result)
            if callback:
                result = callback(result)
                m = len(result)
            all_data.extend(result)
            if m == n:
                data = None
                next = response.links.get('next', {})
                url = next.get('url')
            else:
                break
        return all_data


class Commit(Component):
    type = 'commits'

    def __init__(self, client, sha):
        super().__init__(client)
        self.sha = sha

    @property
    def api_url(self):
        return '%s/%s/%s' % (self.client, self.type, self.sha)

    async def get(self):
        response = await self.http.get(str(self))
        response.raise_for_status()
        return response.json()

    def comments(self, **data):
        """Return all comments for this commit
        """
        return self.get_list('%s/comments' % self, **data)


class Issue(Commit):
    type = 'issues'


class Pull(Commit):
    type = 'pulls'


class Release(Commit):
    type = 'releases'

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
        inputs = {
            'name': name,
            'Content-Type': content_type
        }
        url = '%s/%s' % (self.uploads_url, urlsplit(self.api_url).path)
        url = iri_to_uri(url, **inputs)
        response = await self.http.post(url, data=stream_upload(filename))
        response.raise_for_status()
        return response.json()


def stream_upload(filename):
    with open(stream_upload, 'rb') as file:
        while True:
            chunk = file.read(ONEMB)
            if not chunk:
                break
            yield chunk
