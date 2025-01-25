import secrets
import string

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
    ret_list = []
    in_directory = []
    for summary in summaries:
        file_path = summary.key[prefix_len:]
        splist = file_path.split("/")
        if len(splist) > 1:
            # directory
            if key + splist[0] not in in_directory:
                ret_list.append({"key": key + splist[0] + "/"})
                in_directory.append(key + splist[0])
        else:
            if splist[0] == "":
                continue
            # file
            ret_list.append(summary)

    return ret_list


def pass_gen(size: int = 12) -> str:
    """ランダムなパスワードを生成する

    英大文字、英小文字、数字、一部の特殊文字（%&$#()）を含むパスワードを生成します。

    Args:
        size (int, optional): 生成するパスワードの長さ. Defaults to 12.

    Returns:
        str: 生成されたパスワード

    Example:
        >>> pass_gen(8)
        'Kj2$mP9n'
    """
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    # 記号を含める場合
    chars += "%&$#()"

    return "".join(secrets.choice(chars) for x in range(size))


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


def make_tag(**kwargs: dict) -> str:
    """キーワード引数からタグ文字列を生成する

    Args:
        **kwargs (dict): キーと値のペアを含む任意のキーワード引数

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
