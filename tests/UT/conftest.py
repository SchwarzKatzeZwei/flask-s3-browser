import inspect
import pathlib
import sys
from datetime import datetime

import docstring_parser
import pytest
import pytest_html
from py.xml import html  # type:ignore
from pytest import ExitCode
from pytest_metadata.plugin import metadata_key

sys.path.append(str(pathlib.Path(__file__).parent))


ASSERT_COUNT: int = 0
FUNCTION_ASSERT_COUNT: int = 0


def pytest_configure(config: pytest.Config) -> None:
    """テストを実行する前に[環境]セクションを変更"""
    config.stash[metadata_key]["Version"] = "1.0.0"
    config.option.self_contained_html = True  # 単一ファイルレポート


@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session: pytest.Session, exitstatus: ExitCode) -> None:
    """テストの実行後に[環境]セクションを変更する"""
    session.config.stash[metadata_key]["単体試験項目数"] = ASSERT_COUNT


def pytest_html_report_title(report: pytest_html.report_data.ReportData) -> None:
    """Called before adding the title to the report"""
    report.title = "Unit Test Report"


# @pytest.hookimpl(tryfirst=True)
# def pytest_html_results_table_header(cells: list) -> None:
#     """Called after building results table header."""
#     del cells[1:]
#     cells.append(html.th("Test Case"))  # 2
#     cells.append(html.th("Expects"))  # 3
#     cells.append(html.th("Duration"))  # 4
#     cells.append(html.th("Time", class_="sortable time", col="time"))  # 5
#     cells.append(html.th("Asserts"))  # 6


def pytest_html_results_table_row(report: pytest.TestReport, cells: list) -> None:
    """Called after building results table row."""
    duration = cells[2]
    try:
        cells[1] = html.td(_add_br(report.tests))  # 「テスト内容」をレポートに出力
        cells[2] = html.td(_add_br(report.expects))  # 「期待結果」をレポートに出力
        cells[3] = duration  # 「実行時間」をレポートに出力
        # cells.append(html.td(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), class_="col-time"))  # 「テスト時刻」をレポートに出力
        # cells.append(html.td(report.asserts))  # 「assert件数」をレポートに出力
    except AttributeError:
        print("テストケースが不正終了しているため、レポートに出力できません。")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Function, call: pytest.CallInfo) -> None:  # type:ignore
    outcome = yield
    report = outcome.get_result()
    docstring = docstring_parser.parse(str(item.function.__doc__))
    # 「テスト内容」を`report`に追加
    report.tests = docstring.get("Tests") if docstring.get("Tests") is not None else ["No Test Case"]
    # 「期待結果」を`report`に追加
    report.expects = docstring.get("Expects") if docstring.get("Expects") is not None else ["No Expects"]
    global ASSERT_COUNT, FUNCTION_ASSERT_COUNT
    try:
        try:
            if inspect.getsource(item.function.__wrapped__.__code__).count("Tests:"):
                FUNCTION_ASSERT_COUNT = 0
                FUNCTION_ASSERT_COUNT = inspect.getsource(item.function.__wrapped__.__code__).count("assert")
            report.asserts = FUNCTION_ASSERT_COUNT  # 「assert件数」を`report`に追加

            if report.when == "call":
                ASSERT_COUNT += FUNCTION_ASSERT_COUNT

        except AttributeError:
            if inspect.getsource(item.function.__code__).count("Tests:"):
                FUNCTION_ASSERT_COUNT = 0
                FUNCTION_ASSERT_COUNT = inspect.getsource(item.function.__code__).count("assert")
            report.asserts = FUNCTION_ASSERT_COUNT  # 「assert件数」を`report`に追加

            if report.when == "call":
                ASSERT_COUNT += FUNCTION_ASSERT_COUNT
    except OSError:
        report.asserts = 0
        ASSERT_COUNT = -1


def _add_br(lines: list) -> list:
    """複数行のリストをhtml.br()でjoinする（文字列の"<br>"だとエスケープされるので）"""
    new_lines = []
    for line in lines[:-1]:
        new_lines.append(line)
        new_lines.append(html.br())
    new_lines.append(lines[-1])
    return new_lines
