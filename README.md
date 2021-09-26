# Flask S3 Browser

AWS S3をwebブラウザーから簡易操作

## Setup

Flask S3 Browser supports Python >= 3.9.x

- Install Dependencies

```shell
pip install -r requirements.txt  # pip
conda env create -f M1Mac_miniconda_env.yaml  # Apple M1 Mac miniconda
```

- Configuration

`.env-sample`の内容を使って、新しいファイル`.env`を作成します。  
AWS CLIを使用していない場合は、プレースホルダーを変更して、AWSの認証情報とバケット名を追加します。

## Usage

```shell
flask run
```


## Clone origin

<https://github.com/kishstats/flask-s3-browser>
