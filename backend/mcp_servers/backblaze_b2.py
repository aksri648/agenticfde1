import os
import json
import boto3
from claude_agent_sdk import tool, create_sdk_mcp_server

B2_APPLICATION_KEY_ID = os.getenv("B2_APPLICATION_KEY_ID", "")
B2_APPLICATION_KEY = os.getenv("B2_APPLICATION_KEY", "")
B2_BUCKET_NAME = os.getenv("B2_BUCKET_NAME", "")


def _get_b2_client():
    return boto3.client(
        "s3",
        endpoint_url="https://s3.us-west-004.backblazeb2.com",
        aws_access_key_id=B2_APPLICATION_KEY_ID,
        aws_secret_access_key=B2_APPLICATION_KEY,
        region_name="us-west-004",
    )


@tool(
    "b2_upload_file",
    "Upload a file to a Backblaze B2 bucket using S3-compatible API.",
    {"key": str, "file_path": str},
)
async def b2_upload_file(args):
    client = _get_b2_client()
    try:
        client.upload_file(args["file_path"], B2_BUCKET_NAME, args["key"])
        return {"content": [{"type": "text", "text": f"Uploaded {args['file_path']} to s3://{B2_BUCKET_NAME}/{args['key']}"}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Upload failed: {str(e)}"}]}


@tool(
    "b2_download_file",
    "Download a file from a Backblaze B2 bucket.",
    {"key": str, "file_path": str},
)
async def b2_download_file(args):
    client = _get_b2_client()
    try:
        client.download_file(B2_BUCKET_NAME, args["key"], args["file_path"])
        return {"content": [{"type": "text", "text": f"Downloaded s3://{B2_BUCKET_NAME}/{args['key']} to {args['file_path']}"}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Download failed: {str(e)}"}]}


@tool(
    "b2_list_files",
    "List files in a Backblaze B2 bucket.",
    {"prefix": str},
)
async def b2_list_files(args):
    client = _get_b2_client()
    try:
        resp = client.list_objects_v2(Bucket=B2_BUCKET_NAME, Prefix=args.get("prefix", ""))
        files = [{"key": obj["Key"], "size": obj["Size"]} for obj in resp.get("Contents", [])]
        return {"content": [{"type": "text", "text": json.dumps(files)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"List failed: {str(e)}"}]}


@tool(
    "b2_delete_file",
    "Delete a file from a Backblaze B2 bucket.",
    {"key": str},
)
async def b2_delete_file(args):
    client = _get_b2_client()
    try:
        client.delete_object(Bucket=B2_BUCKET_NAME, Key=args["key"])
        return {"content": [{"type": "text", "text": f"Deleted s3://{B2_BUCKET_NAME}/{args['key']}"}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Delete failed: {str(e)}"}]}


s3_server = create_sdk_mcp_server(
    name="s3",
    tools=[b2_upload_file, b2_download_file, b2_list_files, b2_delete_file],
)
