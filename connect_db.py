import logging
import os

import pymysql

HOST = os.getenv('DB_HOST', '127.0.0.1')
USER = os.getenv('DB_USER', '')
PASS = os.getenv('DB_PASS', '')
DATABASE = os.getenv('DB_NAME', 'tvhub')
PORT = int(os.getenv('DB_PORT', '3306'))


def _connect():
    return pymysql.connect(
        host=HOST,
        port=PORT,
        user=USER,
        passwd=PASS,
        db=DATABASE,
        charset='utf8mb4',
        connect_timeout=3,
        read_timeout=5,
        write_timeout=5,
        cursorclass=pymysql.cursors.DictCursor,
    )


class db:
    @staticmethod
    def sql_fetchall(sql):
        return db.sql_fetchall_params(sql, None)

    @staticmethod
    def sql_fetchone(sql):
        return db.sql_fetchone_params(sql, None)

    @staticmethod
    def sql_fetchone_params(sql, params):
        try:
            with _connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    return cur.fetchone()
        except Exception:
            logging.exception("Database fetchone failed")
            return None

    @staticmethod
    def sql_fetchall_params(sql, params):
        try:
            with _connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    return cur.fetchall()
        except Exception:
            logging.exception("Database fetchall failed")
            return []

    @staticmethod
    def sql_commit(sql, params=None):
        try:
            with _connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                conn.commit()
                return True
        except Exception:
            logging.exception("Database commit failed")
            return False

    @staticmethod
    def sql_run_commit(sql):
        return db.sql_commit(sql)


class share:
    @staticmethod
    def format_number(info, digit):
        return round(info, digit)

    @staticmethod
    def format_cunumber(info, digit):
        if 0 <= digit <= 8:
            return f"{info:,.{digit}f}"
        return f"{info:,.2f}"

    @staticmethod
    def format_date(info):
        return info.strftime("%d/%m/%Y")

    @staticmethod
    def format_datetime(info):
        return info.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def convert_datetime(info):
        return info.strftime("%Y-%m-%d %H:%M:%S")
