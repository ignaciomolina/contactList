__author__ = "Ignacio Molina Cuquerella"
__email__ = "neldan@gmail.com"


class User:
    """
    Class that has information relative to an user of the service.
    """

    def __init__(self, username, name='', lastname='', description=''):
        self._username = username
        self.name = name
        self.lastname = lastname
        self.description = description

    def _get_username(self):
        return self._username

    username = property(_get_username)

    def _set_name(self, name):
        self._name = name

    def _get_name(self):
        return self._name

    name = property(_get_name, _set_name)

    def _set_lastname(self, lastname):
        self._lastname = lastname

    def _get_lastname(self):
        return self._lastname

    lastname = property(_get_lastname, _set_lastname)

    def _set_description(self, description):
        self._description = description

    def _get_description(self):
        return self._description

    description = property(_get_description, _set_description)

    def from_json(self, json):
        """
        :param json: JSON with optional fields information to set the User
        """
        if json.get('name'):
            self.name = json['name']
        if json.get('lastname'):
            self.lastname = json['lastname']
        if json.get('description'):
            self.description = json['description']
