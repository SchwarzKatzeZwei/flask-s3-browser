import datetime
import mimetypes
import os
from pathlib import Path

import arrow

from db_access import TinyDBAC
from resources import get_bucket

additional_file_types = {".md": "text/markdown"}


def datetimeformat(date_str: str) -> str:
    """日付フォーマット変更

    Args:
        date_str (str): 時刻文字列(YYYY-MM-DD HH:mm:ss+hh:mmZ)

    Returns:
        str: 変換後時刻文字列
    """
    if not isinstance(date_str, datetime.datetime):
        return "-"

    dt = arrow.get(date_str)
    local = dt.to("Asia/Tokyo").format("YYYY/MM/DD HH:mm:ss")
    return local


def file_type(summary) -> str:
    """MIMEタイプ取得

    Args:
        summary (boto3.resources.factory.s3.ObjectSummary): S3 Bucket Object

    Returns:
        str: MIMEタイプ
    """
    if isinstance(summary, dict):
        return "directory"

    else:
        key = summary.key

    file_info = os.path.splitext(key)
    file_extension = file_info[1]

    try:
        return mimetypes.types_map[file_extension]
    except KeyError:
        filetype = "Unknown"
        if file_info[0].startswith(".") and file_extension == "":
            filetype = "text"

        if file_extension in additional_file_types.keys():
            filetype = additional_file_types[file_extension]

        return filetype


def path_parent(path: str) -> str:
    """親ディレクトリパス返却

    Args:
        path (str): カレントパス

    Returns:
        str: 親ディレクトリパス

    Note:
        ルートディレクトリの場合はゼロストリングスを返却
    """
    if path == "":
        return path

    p = str(Path(path).parent)
    if p == ".":
        return ""

    return p + "/"


def get_archive_pass(key: str) -> str:
    """圧縮ファイルパスワード返却

    Args:
        key (str): S3 Bucket Object Key

    Returns:
        str: password
    """
    dbac = TinyDBAC()
    if (record := dbac.search(key)) != []:
        password = record[0]["value"]
    else:
        password = "unknown"

    del dbac
    return password


def get_expire(key: str) -> str:
    """有効期限日取得

    Args:
        key (str): S3 Bucket Object Key

    Returns:
        str: 変換後時刻文字列
    """
    my_bucket = get_bucket()
    object = my_bucket.Object(key)
    try:
        expiration_date = object.expiration.split('"')[1]
    except AttributeError:
        return "never"
    dt = datetime.datetime.strptime(expiration_date, "%a, %d %b %Y %H:%M:%S %Z")
    ar = arrow.get(dt)
    local = ar.to("Asia/Tokyo").format("YYYY/MM/DD HH:mm:ss")
    return local
