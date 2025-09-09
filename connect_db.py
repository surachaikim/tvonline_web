import os
import pymysql
from datetime import datetime

# HOST = "192.168.1.123"
HOST = os.getenv('DB_HOST', '127.0.0.1')
USER = os.getenv('DB_USER', 'root')
PASS = os.getenv('DB_PASS', '1234')
DATABASE = os.getenv('DB_NAME', 'tvhub')




class db:

    def sql_fetchall(sql):
        try:
            conn = pymysql.connect(host=HOST, user=USER, passwd=PASS,
                                   db=DATABASE, cursorclass=pymysql.cursors.DictCursor)
            with conn.cursor() as cur:
                cur.execute(sql)
                row = cur.fetchall()
        except:
            cur.close()
            conn.close()
        finally:
            cur.close()
            conn.close()
        return row

    def sql_fetchone(sql):
        try:
            conn = pymysql.connect(host=HOST, user=USER, passwd=PASS,
                                   db=DATABASE, cursorclass=pymysql.cursors.DictCursor)
            with conn.cursor() as cur:
                cur.execute(sql)
                row = cur.fetchone()
        except:
            cur.close()
            conn.close()
        finally:
            cur.close()
            conn.close()
        return row

    def sql_fetchone_params(sql, params):
        try:
            conn = pymysql.connect(host=HOST, user=USER, passwd=PASS,
                                   db=DATABASE, cursorclass=pymysql.cursors.DictCursor)
            with conn.cursor() as cur:
                cur.execute(sql, params)
                row = cur.fetchone()
        except:
            cur.close()
            conn.close()
        finally:
            cur.close()
            conn.close()
        return row

    def sql_commit(sql, string):
        try:
            conn = pymysql.connect(host=HOST, user=USER, passwd=PASS,
                                   db=DATABASE, cursorclass=pymysql.cursors.DictCursor)
            with conn.cursor() as cur:
                cur.execute(sql, (string))
                conn.commit()
        except:
            cur.close()
            conn.close()
        finally:
            cur.close()
            conn.close()

    def sql_run_commit(sql):
        try:
            conn = pymysql.connect(host=HOST, user=USER, passwd=PASS,
                                   db=DATABASE, cursorclass=pymysql.cursors.DictCursor)
            with conn.cursor() as cur:
                cur.execute(sql)
                conn.commit()
        except:
            cur.close()
            conn.close()
        finally:
            cur.close()
            conn.close()

    def sql_fetchall_params(sql, params):
        try:
            conn = pymysql.connect(host=HOST, user=USER, passwd=PASS,
                                   db=DATABASE, cursorclass=pymysql.cursors.DictCursor)
            with conn.cursor() as cur:
                cur.execute(sql, params)
                row = cur.fetchall()
        except:
            cur.close()
            conn.close()
        finally:
            cur.close()
            conn.close()
        return row


class share:

    def format_number(info, digit):
        item = round(info, digit)
        return item

    def format_cunumber(info, digit):
        item = ""
        if digit == 0:
            item = str("{:,.0f}".format(info))
        elif digit == 1:
            item = str("{:,.1f}".format(info))
        elif digit == 2:
            item = str("{:,.2f}".format(info))
        elif digit == 3:
            item = str("{:,.3f}".format(info))
        elif digit == 4:
            item = str("{:,.4f}".format(info))
        elif digit == 5:
            item = str("{:,.5f}".format(info))
        elif digit == 6:
            item = str("{:,.6f}".format(info))
        elif digit == 7:
            item = str("{:,.7f}".format(info))
        elif digit == 8:
            item = str("{:,.8f}".format(info))
        else:
            item = str("{:,.2f}".format(info))
        return item

    def format_date(info):
        dd = info.strftime("%d")
        mm = info.strftime("%m")
        yy = info.strftime("%Y")
        yyyy = int(yy)
        item = str(dd) + "/" + str(mm) + "/" + str(yyyy)
        return item

    def format_datetime(info):
        dd = info.strftime("%d")
        mm = info.strftime("%m")
        yy = info.strftime("%Y")
        h = info.strftime("%H")
        m = info.strftime("%M")
        s = info.strftime("%S")
        item = f'{yy}-{mm}-{dd} {h}:{m}:{s}'
        return item

    def convert_datetime(info):
        dd = info.strftime("%d")
        mm = info.strftime("%m")
        yy = info.strftime("%Y")
        h = info.strftime("%H")
        m = info.strftime("%M")
        s = info.strftime("%S")
        item = f'{yy}-{mm}-{dd} {h}:{m}:{s}'
        return item
