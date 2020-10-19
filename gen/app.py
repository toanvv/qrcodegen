import json
import os
import pyqrcode
import png
import base64
import boto3
from pyqrcode import QRCode

def obj_exists(bucket, obj):
    s3 = boto3.resource('s3')
    try:
        s3.Object(bucket, obj).load()
    except:
        return False
    else:
        return True

def generate_qr_and_store_to_s3(data):
    client = boto3.client('s3')
    bucket = os.environ['QR_BUCKET_NAME']
    code = base64.b64decode(data.encode('ascii'))
    code = code.decode('ascii')
    file_name = f"/tmp/{data.replace('=', '')}.png"
    obj_name = os.path.basename(file_name)
    s3_obj_url = f'https://{bucket}.s3.amazonaws.com/{obj_name}'

    if obj_exists(bucket, obj_name):
        return s3_obj_url

    qr = pyqrcode.create(code)
    qr.png(file_name, scale = 6)
    with open(file_name, "rb") as f:
        client.put_object(
            ACL='public-read',
            Body=f,
            ContentType='image/png',
            Bucket=bucket,
            Key=os.path.basename(file_name)
        )

    return s3_obj_url

def lambda_handler(event, context):
    try:
        code = event["queryStringParameters"]['code']
    except:
        response = { 'body': json.dumps({'message': 'parameter code is missing!'}) }
        return response
    else:
        url = generate_qr_and_store_to_s3(code)
        response = {}
        data = { 'qr_url': url }
        response["body"]=json.dumps(data)
        return response
