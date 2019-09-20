import pymysql

mysql_host = '172.105.241.159'
mysql_user = 'root'
mysql_password = 'cjc!40812848'
mysql_database = 'scoresaber'
mysql_charset = 'utf8'

def insert(table, columns, values):
    conn = pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_password, db=mysql_database, charset=mysql_charset)
    curs = conn.cursor()

    tmp = "%s"
    tmp += ", %s" * (len(values)-1)
    curs.execute("insert into {}({}) values ({})".format(table, ",".join(columns), tmp), values)
    conn.commit()

    conn.close()

def update(table, wheres, sets):
    conn = pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_password, db=mysql_database, charset=mysql_charset)
    curs = conn.cursor()

    curs.execute("update {} set {} where {}".format(table, sets, wheres))
    conn.commit()

    conn.close()

def delete(table, where, values):
    conn = pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_password, db=mysql_database, charset=mysql_charset)
    curs = conn.cursor()

    curs.execute("delete from {} where {}".format(table, where), values)
    conn.commit()

    conn.close()

def select(table, select, after):
    conn = pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_password, db=mysql_database, charset=mysql_charset)
    curs = conn.cursor(pymysql.cursors.DictCursor)

    sql = "select {} from {}".format(select, table)
    if len(after) > 0:
        sql += " " + after
    curs.execute(sql)
    rows = curs.fetchall()

    conn.close()

    return rows