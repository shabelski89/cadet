import sqlite3


class Database:
    def __init__(self, name):
        self._conn = sqlite3.connect(name)
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()


if __name__ == "__main__":
    with Database('cadet.sqlite') as db:
        # db.execute("CREATE TABLE IF NOT EXISTS cadet(c_id INTEGER PRIMARY KEY, snd_name text, fst_name text,  "
        #            "f_name text, groups text, date text, mark int, desc text)")
        #
        # db.execute('INSERT INTO cadet (c_id, snd_name, fst_name, f_name, groups, date, mark, desc) '
        #            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (1, 'Иванов', 'Иван', 'Иванович', 'G-20',
        #                                                "14122020 19:07:25", 5, 'work done'))
        cadets = db.query('SELECT * FROM cadet;')
        print(cadets)
