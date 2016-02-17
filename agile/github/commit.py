

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
