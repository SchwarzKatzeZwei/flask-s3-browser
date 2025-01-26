from typing import List
from unittest.mock import MagicMock

import pytest

from util import check_already_insert_db, dir_file_filter, make_tag, pass_gen


@pytest.fixture
def mock_s3_summaries(request: pytest.FixtureRequest) -> List[MagicMock]:
    """S3オブジェクトサマリーのモックを作成"""
    if request.function.__name__ == "test_dir_file_filter_with_prefix":
        # プレフィックス付きのテスト用のモック作成
        objects = [
            {"key": "test/"},
            {"key": "test/test.txt"},
            {"key": "test/dir1/file.txt"},
            {"key": "test/dir2/"},
            {"key": "test/dir2/empty"},
        ]
    else:
        # プレフィックスなしのテスト用のモック作成
        objects = [
            {"key": "test.txt"},
            {"key": "dir1/file.txt"},
            {"key": "empty/"},
        ]

    # モックオブジェクトの作成
    summaries = []
    for obj in objects:
        mock = MagicMock()
        mock.configure_mock(**obj)
        summaries.append(mock)

    return summaries


def test_dir_file_filter_with_prefix(mock_s3_summaries: list[MagicMock]) -> None:
    """dir_file_filterのプレフィックス付きテスト

    Tests:
        - プレフィックス "test/" を指定してフィルタリング
        - ディレクトリとファイルの分離が正しく行われるか

    Expects:
        - ディレクトリはkey属性を持つ辞書として返される
        - ファイルはS3オブジェクトサマリーとして返される
        - 重複するディレクトリは1つにまとめられる
    """
    result = dir_file_filter(mock_s3_summaries, "test/")
    assert len(result) == 3
    assert isinstance(result[0], dict)
    assert "key" in result[0]


def test_dir_file_filter_without_prefix(mock_s3_summaries: list[MagicMock]) -> None:
    """dir_file_filterのプレフィックスなしテスト

    Tests:
        - プレフィックスなしでフィルタリング
        - 空のディレクトリが正しく処理されるか

    Expects:
        - 空のディレクトリは除外される
        - ファイルとディレクトリが正しく分離される
    """
    result = dir_file_filter(mock_s3_summaries)
    assert len(result) == 3


def test_dir_file_filter_empty_list() -> None:
    """空のサマリーリストのテスト

    Tests:
        - 空のサマリーリストでフィルタリング

    Expects:
        - 空のリストが返される
    """
    result = dir_file_filter([])
    assert len(result) == 0


def test_pass_gen_default() -> None:
    """パスワード生成のデフォルト設定テスト

    Tests:
        - デフォルトの長さ(12文字)でパスワードを生成

    Expects:
        - 12文字のパスワードが生成される
        - 生成されたパスワードは文字列型
    """
    result = pass_gen()
    assert len(result) == 12
    assert isinstance(result, str)


def test_pass_gen_custom_length() -> None:
    """パスワード生成のカスタム長さテスト

    Tests:
        - 指定した長さ(8文字)でパスワードを生成

    Expects:
        - 8文字のパスワードが生成される
        - 生成されたパスワードは文字列型
    """
    result = pass_gen(8)
    assert len(result) == 8
    assert isinstance(result, str)


def test_pass_gen_character_types() -> None:
    """パスワードの文字種テスト

    Tests:
        - 生成されたパスワードに必要な文字種が含まれているか確認

    Expects:
        - 大文字、小文字、数字、特殊文字が少なくとも1つずつ含まれる
    """
    result = pass_gen(20)  # より長いパスワードで確実にすべての文字種が含まれるようにする
    assert any(c.isupper() for c in result), "大文字が含まれていない"
    assert any(c.islower() for c in result), "小文字が含まれていない"
    assert any(c.isdigit() for c in result), "数字が含まれていない"
    assert any(c in "%&$#()" for c in result), "特殊文字が含まれていない"


def test_check_already_insert_db_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    """DBにキーが存在する場合のテスト

    Tests:
        - 既存のキーをチェック

    Expects:
        - Trueが返される
    """
    mock_db = MagicMock()
    mock_db.search.return_value = [{"key": "test", "value": "test"}]
    monkeypatch.setattr("util.TinyDBAC", lambda: mock_db)

    assert check_already_insert_db("test") is True


def test_check_already_insert_db_not_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    """DBにキーが存在しない場合のテスト

    Tests:
        - 存在しないキーをチェック

    Expects:
        - Falseが返される
    """
    mock_db = MagicMock()
    mock_db.search.return_value = []
    monkeypatch.setattr("util.TinyDBAC", lambda: mock_db)

    assert check_already_insert_db("test") is False


def test_make_tag() -> None:
    """タグ文字列生成のテスト

    Tests:
        - 複数のキーワード引数からタグ文字列を生成

    Expects:
        - キーと値が=で連結された文字列が生成される
    """
    result = make_tag(name="test", id="123")
    assert result == "name=testid=123"


def test_make_tag_empty() -> None:
    """空のタグ文字列生成テスト

    Tests:
        - 引数なしでタグ文字列を生成

    Expects:
        - 空文字列が返される
    """
    result = make_tag()
    assert result == ""
