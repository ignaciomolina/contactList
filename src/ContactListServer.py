import time
from datetime import datetime

import jsonpickle
import redis
from flask import Flask
from flask import make_response
from flask import request

from Contact import Contact
from Group import Group
from User import User


__author__ = 'Ignacio Molina Cuquerella'
__email__ = 'neldan@gmail.com'


app = Flask(__name__)


@app.route('/', methods=['GET'])
def users_list():

    from_date = 0
    to_date = int(round(time.time() * 1000))  # current time in millis

    if request.args.get('from'):
        date = request.args.get('from')
        from_date = datetime.strptime(str(date), '%d/%m/%Y').timestamp() * 1000
    if request.args.get('to'):
        date = request.args.get('to')
        to_date = datetime.strptime(str(date), '%d/%m/%Y').timestamp() * 1000

    users_set = set()

    for userId in r_server.zrangebyscore('user:set', from_date, to_date):
        user = jsonpickle.decode(r_server.get('user:%s' %
                                     (userId.decode('utf-8'))).decode('utf-8'))
        users_set.add(user)

    return jsonpickle.encode(users_set, unpicklable=False)


@app.route('/', methods=['POST'])
def add_user():

    data = request.get_json(silent=False)

    if not data.get('username'):
        return make_response('\'username\' required.', 400)

    user = User(data['username'])
    user.from_json(data)

    millis = int(round(time.time() * 1000))

    if not r_server.zscore('user:set', user.username):
        r_server.zadd('user:set', user.username, millis)
        r_server.set('user:%s' % user.username, jsonpickle.encode(user))
        return 'localhost:5000/%s' % user.username

    return make_response("That user already exist!", 400)


@app.route('/<user_id>/', methods=['GET'])
def get_user(user_id):

    if not r_server.zscore('user:set', user_id):
        return make_response("That user does not exist", 404)

    user = jsonpickle.decode(r_server.get('user:%s' % user_id).decode('utf-8'))

    return jsonpickle.encode(user, unpicklable=False)


@app.route('/<user_id>/', methods=['PUT'])
def change_user(user_id):

    if not r_server.zscore('user:set', user_id):
        return make_response("That user does not exist", 404)

    data = request.get_json(silent=False)

    if data.get('username') and data['username'] != user_id:
        return make_response('\'username\' can\'t be modified', 400)

    user = jsonpickle.decode(r_server.get('user:%s' % user_id).decode('utf-8'))
    user.from_json(data)

    r_server.set('user:%s' % user_id, jsonpickle.encode(user))

    return make_response('', 204)


@app.route('/<user_id>/', methods=['DELETE'])
def remove_user(user_id):

    r_server.zrem('user:set', user_id)
    r_server.delete('user:%s' % user_id)
    for key in r_server.keys('group:%s:*' % user_id):
        r_server.delete(key)

    for key in r_server.keys('contact:%s:*' % user_id):
        r_server.delete(key)

    return make_response('', 200)


@app.route('/<user_id>/groups/', methods=['GET'])
def groups_list(user_id):

    from_date = 0
    to_date = int(round(time.time() * 1000))  # current time in millis

    if request.args.get('from'):
        date = request.args.get('from')
        from_date = datetime.strptime(str(date), '%d/%m/%Y').timestamp() * 1000
    if request.args.get('to'):
        date = request.args.get('to')
        to_date = datetime.strptime(str(date), '%d/%m/%Y').timestamp() * 1000

    groups_set = set()

    if not r_server.zscore('user:set', user_id):
        return make_response('That user does not exist', 404)

    for group_id in r_server.zrangebyscore('group:%s:set' % user_id, from_date,
                                           to_date):
        group = jsonpickle.decode(
            r_server.get('group:%s:%s' %
                         (user_id, group_id.decode('utf-8'))).decode('utf-8'))
        groups_set.add(group)

    return jsonpickle.encode(groups_set, unpicklable=False)


@app.route('/<user_id>/groups/', methods=['POST'])
def add_group(user_id):

    if not r_server.zscore('user:set', user_id):
        return make_response('That user does not exist', 404)

    data = request.get_json(silent=False)

    if not data.get('name'):
        return make_response('\'name\' required.', 400)

    group = Group(data['name'])
    group.from_json(data)

    millis = int(round(time.time() * 1000))

    if not r_server.zscore('group:%s:set' % user_id, group.name):
        r_server.zadd('group:%s:set' % user_id, group.name, millis)
        r_server.set('group:%s:%s' % (user_id, group.name),
                     jsonpickle.encode(group))
        return 'localhost:5000/%s/groups/%s' % (user_id, group.name)

    return make_response("That group already exist!", 400)


@app.route('/<user_id>/groups/<group_id>/', methods=['GET'])
def get_group(user_id, group_id):

    if not r_server.zscore('user:set', user_id):
        return make_response("That user does not exist", 404)

    if not r_server.zscore('group:%s:set' % user_id, group_id):
        return make_response("That group does not exist", 404)

    group = jsonpickle.decode(r_server.get('group:%s:%s' % (user_id,
                                                    group_id)).decode('utf-8'))

    return jsonpickle.encode(group, unpicklable=False)


@app.route('/<user_id>/groups/<group_id>/', methods=['PUT'])
def change_group(user_id, group_id):

    if not r_server.zscore('user:set', user_id):
        return make_response("That user does not exist", 404)

    if not r_server.zscore('group:%s:set' % user_id, group_id):
        return make_response("That group does not exist", 404)

    data = request.get_json(silent=False)

    if data.get('name') and data['name'] != group_id:
        return make_response('\'username\' can\'t be modified', 400)

    group = jsonpickle.decode(r_server.get('group:%s:%s' %
                                           (user_id, group_id)).decode('utf-8'))
    group.from_json(data)

    r_server.set('group:%s:%s' % (user_id, group_id), jsonpickle.encode(group))

    return make_response('', 204)


@app.route('/<user_id>/groups/<group_id>/', methods=['DELETE'])
def remove_group(user_id, group_id):

    r_server.zrem('group:%s:set' % user_id, group_id)
    r_server.delete('group:%s:%s' % (user_id, group_id))

    for key in r_server.keys('contact:%s:%s:*' % (user_id, group_id)):
        r_server.delete(key)

    return make_response('', 200)


@app.route('/<user_id>/groups/<group_id>/contacts/', methods=['GET'])
def contacts_list(user_id, group_id):

    from_date = 0
    to_date = int(round(time.time() * 1000))  # current time in millis

    if request.args.get('from'):
        date = request.args.get('from')
        from_date = datetime.strptime(str(date), '%d/%m/%Y').timestamp() * 1000
    if request.args.get('to'):
        date = request.args.get('to')
        to_date = datetime.strptime(str(date), '%d/%m/%Y').timestamp() * 1000

    contact_set = set()

    if not r_server.zscore('user:set', user_id):
        return make_response('That user does not exist', 404)

    if not r_server.zscore('group:%s:set' % user_id, group_id):
        return make_response('That group does not exist', 404)

    for contact_id in r_server.zrangebyscore('contact:%s:%s:set' % (user_id,
                                                                    group_id),
                                             from_date, to_date):
        contact = jsonpickle.decode(
            r_server.get('contact:%s:%s:%s' % (user_id, group_id,
                                   contact_id.decode('utf-8'))).decode('utf-8'))
        contact_set.add(contact)

    return jsonpickle.encode(contact_set, unpicklable=False)


@app.route('/<user_id>/groups/<group_id>/contacts/', methods=['POST'])
def add_contact(user_id, group_id):

    if not r_server.zscore('user:set', user_id):
        return make_response('That user does not exist', 404)

    if not r_server.zscore('group:%s:set' % user_id, group_id):
        return make_response('That group does not exist', 404)

    data = request.get_json(silent=False)

    try:
        contact_id = r_server.incr('contact:%s:%s:lastID')

        contact = Contact(contact_id)
        contact.from_json(data)
    except AttributeError as e:
        r_server.decr('contact:%s:%s:lastID')
        return make_response(str(e), 400)

    millis = int(round(time.time() * 1000))

    if not r_server.zscore('contact:%s:%s:set' % (user_id, group_id),
                           contact_id):
        r_server.zadd('contact:%s:%s:set' % (user_id, group_id),
                      contact_id, millis)
        r_server.set('contact:%s:%s:%s' % (user_id, group_id, contact_id),
                     jsonpickle.encode(contact))
        return 'localhost:5000/%s/groups/%s/contacts/%s' % (user_id, group_id,
                                                            contact_id)

    return make_response("That group already exist!", 400)


@app.route('/<user_id>/groups/<group_id>/contacts/<contact_id>', methods=['GET'])
def get_contact(user_id, group_id, contact_id):

    if not r_server.zscore('user:set', user_id):
        return make_response("That user does not exist", 404)

    if not r_server.zscore('group:%s:set' % user_id, group_id):
        return make_response("That group does not exist", 404)

    if not r_server.zscore('contact:%s:%s:set' % (user_id, group_id),
                           contact_id):
        return make_response("That contact does not exist", 404)

    contact = jsonpickle.decode(r_server.get('contact:%s:%s:%s' % (user_id,
                                                                   group_id,
                                                                   contact_id))
                                .decode('utf-8'))

    return jsonpickle.encode(contact, unpicklable=False)


@app.route('/<user_id>/groups/<group_id>/contacts/<contact_id>', methods=['PUT'])
def change_contact(user_id, group_id, contact_id):

    if not r_server.zscore('user:set', user_id):
        return make_response("That user does not exist", 404)

    if not r_server.zscore('group:%s:set' % user_id, group_id):
        return make_response("That group does not exist", 404)

    if not r_server.zscore('contact:%s:%s:set' % (user_id, group_id),
                           contact_id):
        return make_response("That contact does not exist", 404)

    data = request.get_json(silent=False)

    contact = jsonpickle.decode(r_server.get('contact:%s:%s:%s' % (user_id,
                                         group_id, contact_id)).decode('utf-8'))
    try:
        contact.from_json(data)
    except AttributeError as e:
        return make_response(str(e), 400)

    r_server.set('contact:%s:%s:%s' % (user_id, group_id, contact_id),
                 jsonpickle.encode(contact))

    return make_response('', 204)


@app.route('/<user_id>/groups/<group_id>/contacts/<contact_id>', methods=['DELETE'])
def remove_contact(user_id, group_id, contact_id):

    r_server.zrem('contact:%s:%s:set' % (user_id, group_id), contact_id)
    r_server.delete('contact:%s:%s:%s' % (user_id, group_id, contact_id))

    return make_response('', 200)


if __name__ == '__main__':
    r_server = redis.Redis('localhost')
    app.run()
