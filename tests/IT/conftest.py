import signal
import subprocess
import time
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture(scope="session")
def server_up_down() -> Generator:
    # プロジェクトルートパスを取得
    root_dir = Path(__file__).parent.parent.parent

    # Gunicornプロセスを起動
    process = subprocess.Popen(["gunicorn", "-c", "config.py", "--workers=1", "app:app"], cwd=str(root_dir))

    # サーバー起動待機
    time.sleep(1)

    yield

    # テスト終了時にプロセスを終了
    process.send_signal(signal.SIGTERM)
    process.wait()
