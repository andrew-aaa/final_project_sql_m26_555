# Установка соединения с базой данных
# (параметры передаются через класс конфиг).
import re
import psycopg2


class DbConnection:
    def __init__(self, config):
        self.dbname = config.dbname
        self.user = config.user
        self.password = config.password
        self.host = config.host
        self.prefix = config.dbtableprefix

        schema = self.prefix[:-1]
        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            options=f"-c search_path={schema}"
        )

    def close(self):
        if getattr(self, "conn", None) and not self.conn.closed:
            self.conn.close()

    def __del__(self):
        self.close()

    def test(self):
        # Безопасная проверка соединения без создания/удаления таблиц.
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
        return result == (1,)
