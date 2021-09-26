from tinydb import TinyDB, Query


class TinyDBAC:

    def __init__(self) -> None:
        self.db = TinyDB("db.json")

    def __del__(self):
        self.db.close()

    def search(self, key) -> list:
        query = Query()
        return self.db.search(query.key == key)

    def update(self, key, value) -> None:
        query = Query()
        self.db.update({"value": value}, query.key == key)

    def insert(self, key, value) -> None:
        if self.search(key) == []:
            self.db.insert({"key": key, "value": value})
        else:
            self.update(key, value)

    def remove(self, key) -> None:
        query = Query()
        self.db.remove(query.key == key)

    def select_all(self) -> list:
        return self.db.all()
