

class Component:
    """Base class for github components
    """
    def __init__(self, client):
        self.client = client

    def __repr__(self):
        return self.api_url
    __str__ = __repr__

    def __getattr__(self, name):
        return getattr(self.client, name)

    @classmethod
    def id_from_data(cls, data):
        return data['id']

    @classmethod
    def as_id(cls, data):
        if isinstance(data, dict):
            return cls.id_from_data(data)
        return data


class RepoComponents(Component):

    @property
    def api_url(self):
        return '%s/%s' % (self.client, self.__class__.__name__.lower())

    async def get(self, id):
        """Get data for this component
        """
        id = self.as_id(id)
        url = '%s/%s' % (self, id)
        response = await self.http.get(url, auth=self.auth)
        response.raise_for_status()
        return response.json()

    async def create(self, data):
        """Create a new component
        """
        response = await self.http.post(str(self), json=data, auth=self.auth)
        response.raise_for_status()
        return response.json()

    async def delete(self, id):
        """Delete a component by id
        """
        id = self.as_id(id)
        response = await self.http.delete('%s/%s' % (self.api_url, id),
                                          auth=self.auth)
        response.raise_for_status()

    async def get_list(self, url=None, callback=None, limit=100, **data):
        """Get a list of this github component
        :param url: full url
        :param Comp: a :class:`.Component` class
        :param callback: Optional callback
        :param limit: Optional number of items to retrieve
        :param data: additional query data
        :return: a list of ``Comp`` objects with data
        """
        url = url or str(self)
        data = dict(((k, v) for k, v in data.items() if v))
        all_data = []
        if limit:
            data['per_page'] = min(limit, 100)
        while url:
            response = await self.http.get(url, params=data, auth=self.auth)
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
        return all_data


class RepoComponentsId(RepoComponents):

    def __init__(self, root, id):
        super().__init__(root)
        self.id = id

    @property
    def api_url(self):
        return '%s/%s/%s' % (self.client, self.id,
                             self.__class__.__name__.lower())


class Commits(RepoComponents):

    @classmethod
    def id_from_data(cls, data):
        return data['sha']

    def comments(self, commit):
        """Fetch comments for a given commit
        """
        commit = self.as_id(commit)
        return self.get_list(url='%s/%s/comments' % (self, commit))


class Issues(RepoComponents):

    @classmethod
    def id_from_data(cls, data):
        return data['number']

    def comments(self, issue):
        """Return all comments for this issue/pull request
        """
        commit = self.as_id(issue)
        return self.get_list(url='%s/%s/comments' % (self, commit))


class Comments(RepoComponentsId):
    pass


class Pulls(Issues):
    pass
