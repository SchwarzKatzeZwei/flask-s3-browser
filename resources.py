import boto3
from boto3.resources.base import ServiceResource
from botocore.client import BaseClient

from config import S3_BUCKET, S3_KEY, S3_SECRET


def _get_s3_resource() -> ServiceResource:
    """S3リソースクライアントを取得します

    設定に応じて認証情報付きまたは認証情報なしのS3リソースクライアントを返します。

    Returns:
        ServiceResource: S3リソースクライアント

    Note:
        環境変数またはconfigからS3_KEYとS3_SECRETが設定されている場合は、
        それらの認証情報を使用してクライアントを作成します。
    """
    if S3_KEY and S3_SECRET:
        return boto3.resource("s3", aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
    else:
        return boto3.resource("s3")


def get_bucket() -> boto3.resources.base.ServiceResource:
    """S3バケットリソースを取得します

    セッションにバケット名が保存されている場合はそれを使用し、
    ない場合はデフォルトのS3_BUCKETを使用します。

    Returns:
        boto3.resources.base.ServiceResource: S3バケットリソース

    Note:
        バケット名の優先順位:
        1. セッションに保存されたバケット名
        2. 設定ファイルのS3_BUCKET
    """
    s3_resource = _get_s3_resource()
    bucket = S3_BUCKET

    return s3_resource.Bucket(bucket)


def get_s3_client() -> BaseClient:
    """S3クライアントを取得します

    設定に応じて認証情報付きまたは認証情報なしのS3クライアントを返します。

    Returns:
        BaseClient: S3クライアント

    Note:
        環境変数またはconfigからS3_KEYとS3_SECRETが設定されている場合は、
        それらの認証情報を使用してクライアントを作成します。
    """
    if S3_KEY and S3_SECRET:
        return boto3.client("s3", aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
    else:
        return boto3.client("s3")
