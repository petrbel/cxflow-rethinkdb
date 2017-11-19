from argparse import ArgumentParser
import logging
import json

from .utils import create_db, create_table, create_user, grant_permission, insert, select_all, select_by_id


def main():
    # create parser
    main_parser = ArgumentParser('cxflow-rethinkdb')
    subparsers = main_parser.add_subparsers(help='cxflow-rethinkdb commands')

    # create create-db subparser
    create_db_parser = subparsers.add_parser('create-db')
    create_db_parser.set_defaults(subcommand='create-db')
    create_db_parser.add_argument('db_name', help='name of the db to be created')

    # create create-table subparser
    create_table_parser = subparsers.add_parser('create-table')
    create_table_parser.set_defaults(subcommand='create-table')
    create_table_parser.add_argument('db_name', help='name of the db in which the table will be created')
    create_table_parser.add_argument('table_name', help='name of the table to be created')

    # create create-user subparser
    create_user_parser = subparsers.add_parser('create-user')
    create_user_parser.set_defaults(subcommand='create-user')
    create_user_parser.add_argument('user', help='name of the user to be created')
    create_user_parser.add_argument('password', help='password of the user to be created')

    # create grant-permission subparser
    grant_permission_parser = subparsers.add_parser('grant-permission')
    grant_permission_parser.set_defaults(subcommand='grant-permission')
    grant_permission_parser.add_argument('user', help='name of the user to which the permissions will be granted')
    grant_permission_parser.add_argument('permissions', help='permissions JSON string')
    grant_permission_parser.add_argument('db_name', help='name of the db to which the permissions will be granted')
    grant_permission_parser.add_argument('table_name', nargs='?', default=None, help='name of the table to which '
                                                                                     'the permissions will be granted')

    # create insert subparser
    insert_parser = subparsers.add_parser('insert')
    insert_parser.set_defaults(subcommand='insert')
    insert_parser.add_argument('db_name', help='name of the db to which the document will be inserted')
    insert_parser.add_argument('table_name', help='name of the table to which the document will be inserted')
    insert_parser.add_argument('document', help='path to the JSON document to be inserted')

    # create select-all subparser
    select_all_parser = subparsers.add_parser('select-all')
    select_all_parser.set_defaults(subcommand='select-all')
    select_all_parser.add_argument('db_name', help='name of the db from which documents will be selected')
    select_all_parser.add_argument('table_name', help='name of the table from which documents will be selected')

    # create select-by-id subparser
    select_by_id_parser = subparsers.add_parser('select-by-id')
    select_by_id_parser.set_defaults(subcommand='select-by-id')
    select_by_id_parser.add_argument('db_name', help='name of the db from which documents will be selected')
    select_by_id_parser.add_argument('table_name', help='name of the table from which documents will be selected')
    select_by_id_parser.add_argument('id', help='document ID')

    # add common arguments
    for parser in [main_parser, create_db_parser, create_table_parser, create_user_parser, grant_permission_parser,
                   insert_parser, select_all_parser, select_by_id_parser]:
        parser.add_argument('-c', '--credentials', help='path to the credentials file')
        parser.add_argument('-v', '--verbose', action='store_true', help='increase verbosity do level DEBUG')

    args = main_parser.parse_args()

    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    logging.info('Loading credentials')
    with open(args.credentials, 'r') as file:
        credentials = json.load(file)

    if args.subcommand == 'create-db':
        create_db(credentials=credentials, db_name=args.db_name)
    elif args.subcommand == 'create-table':
        create_table(credentials=credentials, db_name=args.db_name, table_name=args.table_name)
    elif args.subcommand == 'create-user':
        create_user(credentials=credentials, user=args.user, password=args.password)
    elif args.subcommand == 'grant-permission':
        permissions = json.loads(args.permissions)
        grant_permission(credentials=credentials, user=args.user, db_name=args.db_name, table_name=args.table_name, permissions=permissions)
    elif args.subcommand == 'insert':
        with open(args.document, 'r') as file:
            document = json.load(file)
        insert(credentials=credentials, db_name=args.db_name, table_name=args.table_name, document=document)
    elif args.subcommand == 'select-all':
        cursor = select_all(credentials=credentials, db_name=args.db_name, table_name=args.table_name)
        for document in cursor:
            print(document)
    elif args.subcommand == 'select-by-id':
        document = select_by_id(credentials=credentials, db_name=args.db_name, table_name=args.table_name, doc_id=args.id)
        print(document)
    else:
        pass


if __name__ == '__main__':
    main()
