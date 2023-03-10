import sqlite3 as sl
# from tkinter import StringVar


# datafilepath = StringVar()


def connect_to_db(datafilepath: str):
    con = sl.connect(datafilepath)
    return con


def create_table(con, create_table_string: str):
    cur = con.cursor()
    cur.execute(create_table_string)
    cur.close()
    con.commit()



def insert_query(con, insert_query_string):
    cur = con.cursor()
#    print(insert_query_string)
#    assert isinstance(cur, object)

    cur.execute(insert_query_string)
    cur.close()
#    con.commit()


def select_query(con, select_query_string):
    print(select_query_string)
    cur = con.cursor()
    cur.execute(select_query_string)
    results = cur.fetchall()
    cur.close()
    return results


def get_cursor(con):
    cur = con.cursor()


def close_cursor(cur):
    cur.close()


def commit(con):
    con.commit()


def close_connection(con):
    con.close()
