import rethinkdb as r

import logging
from typing import Optional, Iterable


def create_db(credentials: dict, db_name: str) -> dict:
    """
    Create a database.

    :param credentials: dict containing at least `host`, `port`, `user` and `password` keys
    :param db_name: name of the database to be created
    :return: RethinkDB response
    """
    logging.info('Creating database `%s`', db_name)

    with r.connect(**credentials) as conn:
        return r.db_create(db_name).run(conn)


def create_table(credentials: dict, db_name: str, table_name: str) -> dict:
    """
    Create a table.

    :param credentials: dict containing at least `host`, `port`, `user` and `password` keys
    :param db_name: name of the database in which the table will be created
    :param table_name: name of the table to be created
    :return: RethinkDB response
    """
    logging.info('Creating table `%s.%s`', db_name, table_name)

    with r.connect(db=db_name, **credentials) as conn:
        return r.db(db_name).table_create(table_name).run(conn)


def create_user(credentials: dict, user: str, password: str) -> dict:
    """
    Create a user.

    :param credentials: dict containing at least `host`, `port`, `user` and `password` keys
    :param user: name of new user to be created
    :param password: password to be set to the new user
    :return: RethinkDB response
    """
    logging.info('Creating user `%s`', user)

    with r.connect(**credentials) as conn:
        return r.db('rethinkdb').table('users').insert({'id': user, 'password': password}).run(conn)


def grant_permission(credentials: dict, user: str, permissions: dict, db_name: str, table_name: Optional[str]=None) -> dict:
    """
    Grand permission to a user.

    If `table_name` is set to `None`, permission is granted to the whole database.

    :param credentials: dict containing at least `host`, `port`, `user` and `password` keys
    :param user: name of the user to which the permissions will be granted
    :param permissions: dict of standard RethinkDB permissions, e.g. `{'read': true, 'write': true}`
    :param db_name: name of the database to which the permissions will be granted
    :param table_name: name of the table to which the permissions will be granted. If `None`, the permissions will
                       be applied to the whole database.
    :return: RethinkDB response
    """
    logging.info('Grating user `%s` permissions `%s` to `%s.%s`', user, permissions, db_name, table_name)

    with r.connect(**credentials) as conn:
        query = r.db(db_name)
        if table_name is not None:
            query = query.table(table_name)

        return query.grant(user, permissions).run(conn)


def insert(credentials: dict, db_name: str, table_name: str, document: dict) -> dict:
    """
    Create new document in the specified table.

    :param credentials: dict containing at least `host`, `port`, `user` and `password` keys
    :param db_name: name of the database in which the document will be inserted
    :param table_name: name of the table in which the document will be inserted
    :param document: document to be inserted
    :return: RethinkDB response
    """
    logging.info('Inserting a document to %s.%s', db_name, table_name)

    with r.connect(db=db_name, **credentials) as conn:
        return r.db(db_name).table(table_name).insert(document).run(conn)


def select_all(credentials: dict, db_name: str, table_name: str) -> Iterable[dict]:
    """
    Select all documents from the specified table.

    :param credentials: dict containing at least `host`, `port`, `user` and `password` keys
    :param db_name: name of the database from which the documents will be selected
    :param table_name: name of the table from which the documents will be selected
    :return: RethinkDB response
    """
    logging.info('Selecting all documents from %s.%s', db_name, table_name)

    with r.connect(db=db_name, **credentials) as conn:
        return r.db(db_name).table(table_name).run(conn)


def select_by_id(credentials: dict, db_name: str, table_name: str, doc_id: str) -> dict:
    """
    Select a document with a specified ID (from the specified table).

    :param credentials: dict containing at least `host`, `port`, `user` and `password` keys
    :param db_name: name of the database from which the document will be selected
    :param table_name: name of the table from which the document will be selected
    :param doc_id: document ID
    :return: RethinkDB response
    """
    logging.info('Selecting document with ID `%s` from %s.%s', doc_id, db_name, table_name)

    with r.connect(db=db_name, **credentials) as conn:
        document = r.db(db_name).table(table_name).get(doc_id).run(conn)

    if document is None:
        raise KeyError('Document with ID `{}` was not found in `{}.{}`'.format(doc_id, db_name, table_name))
    return document
