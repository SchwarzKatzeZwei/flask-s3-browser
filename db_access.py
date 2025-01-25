from typing import Any

from tinydb import Query, TinyDB


class TinyDBAC:
    """TinyDBを使用したシンプルなデータアクセスクラス

    このクラスはキーと値のペアを保存、検索、更新、削除する機能を提供します。
    データは'db.json'ファイルに保存されます。

    Attributes:
        db (TinyDB): TinyDBインスタンス
    """

    def __init__(self) -> None:
        """データベース接続を初期化します"""
        self.db = TinyDB("db.json")

    def __del__(self) -> None:
        """データベース接続を終了します"""
        self.db.close()

    def search(self, key: str) -> list[dict[str, Any]]:
        """指定されたキーに関連する全てのレコードを検索します

        Args:
            key (str): 検索するキー

        Returns:
            list[dict[str, Any]]: 検索結果のリスト。レコードが見つからない場合は空リストを返します。
        """
        query = Query()
        return self.db.search(query.key == key)  # type: ignore

    def update(self, key: str, value: Any) -> None:
        """指定されたキーに関連する値を更新します

        Args:
            key (str): 更新するレコードのキー
            value (Any): 新しい値
        """
        query = Query()
        self.db.update({"value": value}, query.key == key)

    def insert(self, key: str, value: Any) -> None:
        """キーと値のペアを挿入または更新します

        既存のキーが存在する場合は更新を、存在しない場合は新規挿入を行います。

        Args:
            key (str): キー
            value (Any): 値
        """
        if self.search(key) == []:
            self.db.insert({"key": key, "value": value})
        else:
            self.update(key, value)

    def remove(self, key: str) -> None:
        """指定されたキーのレコードを削除します

        Args:
            key (str): 削除するレコードのキー
        """
        query = Query()
        self.db.remove(query.key == key)

    def select_all(self) -> list[dict[Any, Any]]:
        """全てのレコードを取得します

        Returns:
            list[dict[Any, Any]]: データベース内の全レコードのリスト
        """
        return self.db.all()  # type: ignore
