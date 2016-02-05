import re

__author__ = 'Ignacio Molina Cuquerella'
__email__ = 'neldan@gmail.com'


class Contact:
    """
    Class that has contact information about a person.
    """

    def __init__(self, contact_id, name='', lastname='', phone='', mail='',
                 address=''):
        self._id = contact_id
        self.name = name
        self.lastname = lastname
        self.phone = phone
        self.mail = mail
        self.address = address

    def _get_id(self):
        return self._id

    id = property(_get_id)

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

    def _set_phone(self, phone):
        self._phone = phone

    def _get_phone(self):
        return self._phone

    phone = property(_get_phone, _set_phone)

    def _set_mail(self, mail):
        if re.search("^.*@.*", mail) is None:
            raise AttributeError("Malformed e-mail.")
        self._mail = mail

    def _get_mail(self):
        return self._mail

    mail = property(_get_mail, _set_mail)

    def _set_address(self, address):
        self._address = address

    def _get_address(self):
        return self._address

    address = property(_get_address, _set_address)

    def from_json(self, json):
        """
        :param json: JSON with optional fields information to set the Contact
        """
        if json.get('name'):
            self.name = json['name']
        if json.get('lastname'):
            self.lastname = json['lastname']
        if json.get('phone'):
            self.phone = json['phone']
        if json.get('mail'):
            self.mail = json['mail']
        if json.get('address'):
            self.address = json['address']
