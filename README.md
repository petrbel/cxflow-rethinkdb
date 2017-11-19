# cxflow-rethinkdb

RethinkDB extension for `cxflow` framework.

## Development Status

[![CircleCI](https://circleci.com/gh/Cognexa/cxflow-rethinkdb/tree/master.svg?style=shield)](https://circleci.com/gh/Cognexa/cxflow-rethinkdb/tree/master)
[![Development Status](https://img.shields.io/badge/status-CX%20Regular-brightgreen.svg?style=flat)]()
[![MIT license](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)
[![Master Developer](https://img.shields.io/badge/master-Petr%20Bělohlávek-lightgrey.svg?style=flat)]()

## Requirements
See [Cognexa/cxflow](Cognexa/cxflow) for supported operating systems and Python version.

The list of Python package requirements is listed in [requirements.txt](requirements.txt).

## Installation
The package is available through the official PyPI repository; hence, the recommended installation is with pip:

```bash
pip install cxflow-rethinkdb
```
## Usage
When `cxflow-rethinkdb` installed, the following classes are available:

- `cxflow_rethinkdb.RethinkDBHook`

In addition, basic wrappers for common RethinkDB queries are provided.

- `cxflow_rethinkdb.utils`

### CLI
This extension enables a basic CLI for RethinkDB manipulation.
This is useful in cases one debugs classes employing the RethinkDB (in context of cxflow).

Example of possible calls follow.

**credentials/admin.json**
```json
{
  "host": "localhost",
  "port": 28015,
  "user": "admin",
  "password": "superHardSecret"
}
```

**Create `my_database` database**
```bash
cx-rethinkdb create-db my_database -c credentials/admin.json
``` 

**Inside, create `table1` and `table2` tables**
```bash
cx-rethinkdb create-table my_database table1 -c credentials/admin.json
cx-rethinkdb create-table my_database table2 -c credentials/admin.json
``` 


**documents/doc1.json**
```json
{
    "actor": "Lawrence",
    "movie": "Hunger Games"
} 
```

**documents/doc2.json**
```json
{
    "actor": "Lawrence",
    "movie": "Hunger Games 2"
} 
```

**Insert documents from file system (JSON files)**
```bash
cx-rethinkdb insert my_database table1 documents/doc1.json -c credentials/admin.json
cx-rethinkdb insert my_database table1 documents/doc2.json -c credentials/admin.json
``` 

**And select them all**
```bash
cx-rethinkdb select-all my_database table1 -c credentials/admin.json
```

**Select by ID**
The ID might vary among runs.
```bash
cx-rethinkdb select-by-id my_database table1 'a6b12fb1-e018-4307-991d-aae39d9299a9' -c credentials/admin.json
```

**Create another user**
Usually, multiple users with different passwords access the database.
Let's create user `my_user` with password set to `secret`.

```bash
cx-rethinkdb create-user my_user secret -c credentials/admin.json
```

Let's create the credential file for `my_user`:

**credentials/my_user.json**
```json
{
  "host": "localhost",
  "port": 28015,
  "user": "my_user",
  "password": "secret"
}
```

From now on, we can use this user for our queries.

**Select them all**
Let's try again the select from above:
```bash
cx-rethinkdb select-all my_database table1 -c credentials/my_user.json
```
This should throw an error:
```
rethinkdb.errors.ReqlPermissionError: User `my_user` does not have the required `read` permission in:
r.db('my_database').table('table1')
```

By default, new users do not have any permissions.

**Grant permission to a table**
```bash
cx-rethinkdb grant-permission my_user '{"read": true, "write": true}' my_database table1 -c credentials/admin.json
```

The passed permission dict. is a standard [RethinkDB structure](https://www.rethinkdb.com/api/javascript/grant/).

From now on, `my_user` will be able to both select and insert documents to `my_database.table1`.

**Grant permission to a table**
Analogously, admin can grant permissions not only to a single table but to a whole database.

```bash
cx-rethinkdb grant-permission my_user '{"read": true, "write": true}' my_database -c credentials/admin.json
```

So when new table is created, `my_user` has already the granted permissions.

```bash
cx-rethinkdb create-table my_database table3 -c credentials/admin.json
cx-rethinkdb insert my_database table3 documents/doc2.json -c credentials/my_user.json
```

### cxflow Hook
Add the following lines to the [MNIST example](Cognexa/cxflow-examples/mnist_mlp) config hook section.
Make sure that `local_config/rethinkdb.json` contains the credentials as described above.
The user in the credentials must have write access to the specified database/table (already created).

The `variables` entry is optional (all variables are logged by default).
```yaml
  - cxflow_rethinkdb.RethinkDBHook:
      credentials_file: credentials/my_user.json
      db: my_database
      table: table1
      variables:
        - accuracy
```
