import string
import secrets
from db_access import TinyDBAC


def dir_file_filter(summaries, key: str = "") -> list:
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

    # DBUG ####################
    # from pprint import pprint
    # [pprint(s) for s in summaries]
    # print("-" * 80)
    # pprint(ret_list)
    ###########################

    return ret_list


def pass_gen(size: int = 12) -> str:
    """パスワードジェネレータ

    Args:
        size (int, optional): パスワードレングス Defaults to 12.

    Returns:
        str: パスワード
    """
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    # 記号を含める場合
    chars += "%&$#()"

    return "".join(secrets.choice(chars) for x in range(size))


def check_already_insert_db(key: str) -> bool:
    """DBにkeyがあるかチェック

    Args:
        key (str): key

    Returns:
        bool: 正否
    """
    dbac = TinyDBAC()
    if dbac.search(key) != []:
        del dbac
        return True

    del dbac
    return False


def make_tag(**kwargs) -> str:
    """タグ文生成

    Returns:
        str: タグ文
    """
    ret_text = ""
    for k, v in kwargs.items():
        ret_text += f"{k}={v}"

    return ret_text
