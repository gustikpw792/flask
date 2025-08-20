import mariadb
import sys


def dbconn():
    try:
        conn = mariadb.connect(
            user='root',
            password='',
            host='127.0.0.1',
            port=3306,
            database='posonetpendolo'
        )

        return conn.cursor()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform:{e}")
        sys.exit(1)


def show_paket():
    cur = dbconn()
    cur.execute("SELECT * FROM paket")

    row_headers = [x[0] for x in cur.description]
    data = []

    for result in cur.fetchall():
        data.append(dict(zip(row_headers, result)))

    return data
