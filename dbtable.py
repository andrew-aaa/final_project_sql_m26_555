# Базовые действия с таблицами

class DbTable:
    dbconn = None

    def __init__(self):
        pass

    def table_name(self):
        return self.dbconn.prefix + "table"

    def columns(self):
        return {"test": ["integer", "PRIMARY KEY"]}

    def column_names(self):
        return list(self.columns().keys())

    def primary_key(self):
        return ["id"]

    def column_names_without_id(self):
        names = self.column_names()
        pk = set(self.primary_key())
        return [name for name in names if name not in pk]

    def table_constraints(self):
        return []

    def create(self):
        sql = "CREATE TABLE " + self.table_name() + "("
        arr = [k + " " + " ".join(v) for k, v in self.columns().items()]
        sql += ", ".join(arr + self.table_constraints()) + ")"
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql)
        self.dbconn.conn.commit()

    def drop(self):
        sql = "DROP TABLE IF EXISTS " + self.table_name()
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql)
        self.dbconn.conn.commit()

    def insert_one(self, vals):
        names = self.column_names_without_id()
        if len(vals) != len(names):
            raise ValueError(
                f"Ожидалось значений: {len(names)}, получено: {len(vals)}"
            )
        columns_sql = ", ".join(names)
        placeholders = ", ".join(["%s"] * len(vals))
        sql = f"INSERT INTO {self.table_name()} ({columns_sql}) VALUES ({placeholders})"
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql, tuple(vals))
        self.dbconn.conn.commit()

    def first(self):
        sql = "SELECT * FROM " + self.table_name() + " ORDER BY " + ", ".join(self.primary_key())
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchone()

    def last(self):
        sql = "SELECT * FROM " + self.table_name() + " ORDER BY " + ", ".join(
            [x + " DESC" for x in self.primary_key()]
        )
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchone()

    def all(self):
        sql = "SELECT * FROM " + self.table_name() + " ORDER BY " + ", ".join(self.primary_key())
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
