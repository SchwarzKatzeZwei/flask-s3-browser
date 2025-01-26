import allure
import pytest
from playwright.sync_api import Page, expect
from share_connect import top_screen


@pytest.mark.usefixtures("server_up_down")
class TestExampleHTMLSelector:
    @allure.title("IT Case:00001")
    def test_directory_create(self, page: Page) -> None:
        """
        テスト内容：
        none

        期待結果：
        none
        """
        # TOP画面に遷移
        assert top_screen(page)

        # ディレクトリ作成
        page.get_by_placeholder("e.g.: YYYYMMDD").fill("IT-test")
        page.get_by_role("button", name="mkdir").click()
        expect(page.get_by_role("cell", name="IT-test/")).to_be_visible()

        # ディレクトリに入る/出る
        page.get_by_text("IT-test/").click()
        page.get_by_role("button", name="").click()

        # ディレクトリ削除
        page.get_by_role("row", name="IT-test/ - - - never").get_by_role("button").nth(1).click()

        # 削除確認
        expect(page.get_by_role("cell", name="IT-test/")).not_to_be_visible()
