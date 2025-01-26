import re

_section_rgx = re.compile(r"^\s*[a-zA-Z]+:\s*$")
_lspace_rgx = re.compile(r"^\s*")


def _parse_section(lines: list[str]) -> list[tuple[int, str]]:
    """docstringの各行を解析し、セクションタイトル（例："Tests:"）が存在する行のインデックスとタイトルを取得します。

    Args:
        lines (list[str]): docstringの各行を要素とするリスト。

    Returns:
        list[tuple[int, str]]: セクションタイトルが存在する行のインデックスとタイトルをタプルとして格納したリスト。
    """
    return [(i, line.strip()[:-1]) for i, line in enumerate(lines) if _section_rgx.match(line)]


def _count_lspace(s: str) -> int:
    """文字列の先頭にある空白の数をカウントします。

    Args:
        s (str): 空白の数をカウントする文字列。

    Returns:
        int: 文字列の先頭にある空白の数。
    """
    rgx = _lspace_rgx.match(s)
    if rgx is not None:
        return rgx.end()
    return 0


def _parse_content(index: int, lines: list[str]) -> list[str]:
    """指定されたインデックスから開始して、同じインデントレベルを持つ連続する行を取得します。

    Args:
        index (int): 開始行のインデックス。
        lines (list[str]): 解析する行のリスト。

    Returns:
        list[str]: 同じインデントレベルを持つ連続する行のリスト。
    """
    lspace = _count_lspace(lines[index])
    i = index + 1
    contents = []
    for line in lines[i:]:
        if _count_lspace(line) <= lspace:
            break
        contents.append(line.strip())
    return contents


def parse(docstring: str) -> dict[str, list[str]]:
    """docstringを解析し、各セクションのタイトルと内容を辞書として返します。

    Args:
        docstring (str): 解析するdocstring。

    Returns:
        dict[str, list[str]]: 各セクションのタイトルをキーとし、その内容をリストとして格納した辞書。
    """
    lines = docstring.splitlines()
    return {title: _parse_content(index, lines) for index, title in _parse_section(lines)}
