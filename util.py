import secrets
import string
from typing import Any

import boto3

from db_access import TinyDBAC


def dir_file_filter(summaries: boto3.resources.collection.ResourceCollection, key: str = "") -> list:
    """S3のオブジェクトリストからディレクトリとファイルを分離してフィルタリングする

    Args:
        summaries: S3のオブジェクトサマリーのリスト
        key (str, optional): フィルタリングの基準となるプレフィックスキー. Defaults to "".

    Returns:
        list: フィルタリングされたディレクトリとファイルのリスト
        各要素は以下の形式の辞書:
        - ディレクトリの場合: {"key": "directory_name/"}
        - ファイルの場合: S3オブジェクトサマリー
    """
    prefix_len = len(key)
    dir_list = []
    file_list = []
    in_directory = []
    for summary in summaries:
        file_path = summary.key[prefix_len:] if key and summary.key.startswith(key) else summary.key
        splist = file_path.split("/")

        if len(splist) > 1 and splist[0]:
            # ディレクトリエントリの場合
            dir_name = splist[0]
            dir_path = key + dir_name if key else dir_name
            if dir_path not in in_directory:
                dir_list.append({"key": dir_path + "/"})
                in_directory.append(dir_path)
        elif splist[0]:
            # else:
            # ファイルエントリの場合（空でない場合のみ）
            file_list.append(summary)

    # ディレクトリを先に、ファイルを後に配置
    return dir_list + file_list


def pass_gen(size: int = 12) -> str:
    """ランダムなパスワードを生成する

    英大文字、英小文字、数字、一部の特殊文字（%&$#()）を含むパスワードを生成します。
    各文字種が少なくとも1文字は含まれることが保証されています。

    Args:
        size (int, optional): 生成するパスワードの長さ. Defaults to 12.

    Returns:
        str: 生成されたパスワード

    Example:
        >>> pass_gen(8)
        'Kj2$mP9n'
    """
    # 各文字種から1文字ずつ選択
    upper = secrets.choice(string.ascii_uppercase)
    lower = secrets.choice(string.ascii_lowercase)
    digit = secrets.choice(string.digits)
    symbol = secrets.choice("%&$#()")

    # 残りの文字数をランダムに生成
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits + "%&$#()"
    remaining = "".join(secrets.choice(chars) for _ in range(size - 4))

    # すべての文字を結合してシャッフル
    password = list(upper + lower + digit + symbol + remaining)
    secrets.SystemRandom().shuffle(password)
    return "".join(password)


def check_already_insert_db(key: str) -> bool:
    """指定されたキーがデータベースに既に存在するかチェックする

    Args:
        key (str): チェックするキー

    Returns:
        bool: キーが存在する場合はTrue、存在しない場合はFalse

    Note:
        この関数は自動的にデータベース接続を開始し、チェック後に接続を閉じます。
    """
    dbac = TinyDBAC()
    if dbac.search(key) != []:
        del dbac
        return True

    del dbac
    return False


def make_tag(**kwargs: Any) -> str:
    """キーワード引数からタグ文字列を生成する

    Args:
        **kwargs (Any): キーと値のペアを含む任意のキーワード引数

    Returns:
        str: "key1=value1key2=value2..." 形式の文字列

    Example:
        >>> make_tag(name="test", id="123")
        'name=testid=123'
    """
    ret_text = ""
    for k, v in kwargs.items():
        ret_text += f"{k}={v}"
    return ret_text
