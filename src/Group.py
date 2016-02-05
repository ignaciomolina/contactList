__author__ = "Ignacio Molina Cuquerella"
__email__ = "neldan@gmail.com"


class Group:
    """
    Class that has information relative to a group of contacts.
    """
    def __init__(self, name, description='No information'):
        self._name = name
        self._description = description

    def _get_name(self):
        return self._name

    name = property(_get_name)

    def _set_description(self, description):
        self._description = description

    def _get_description(self):
        return self._description

    description = property(_get_description, _set_description)

    def from_json(self, json):
        """
        :param json: JSON with optional fields information to set the Group
        """
        if json.get('description'):
            self.description = json['description']
