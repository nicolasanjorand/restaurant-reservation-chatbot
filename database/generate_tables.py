import sqlite3


def create_tables():
    sql_statements = [
        """CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY, 
                nom TEXT, 
                numero TEXT UNIQUE, 
                date TEXT,
                tel TEXT,
                nb_personne INT
        );"""]

    # create a database connection
    try:
        with sqlite3.connect('../actions/sqlite.db') as conn:
            cursor = conn.cursor()
            for statement in sql_statements:
                cursor.execute(statement)

            conn.commit()
    except sqlite3.Error as e:
        print(e)


if __name__ == '__main__':
    create_tables()