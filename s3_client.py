import boto3
import logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)


class S3Client:
    def __init__(self, bucket_name):
        self.s3 = boto3.client('s3')
        self.bucket_name = bucket_name
    
    def insert_item(self, key, data):
        """Upload data to S3"""
        logging.info(f"Inserting item: {key} to bucket: {self.bucket_name}")
        try:
            if isinstance(data, str):
                self.s3.put_object(Bucket=self.bucket_name, Key=key, Body=data.encode())
            else:
                self.s3.put_object(Bucket=self.bucket_name, Key=key, Body=data)
            logging.info(f"Successfully inserted item: {key}")
            return True
        except ClientError as e:
            logging.error(f"Failed to insert item {key}: {e}")
            return False
    
    def download_item(self, key):
        """Download item from S3"""
        logging.info(f"Downloading item: {key} from bucket: {self.bucket_name}")
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            data = response['Body'].read()
            logging.info(f"Successfully downloaded item: {key}, size: {len(data)} bytes")
            return data
        except ClientError as e:
            logging.error(f"Failed to download item {key}: {e}")
            return None
    
    def list_items(self, prefix=''):
        """List items in S3 bucket"""
        logging.info(f"Listing items in bucket: {self.bucket_name}, prefix: '{prefix}'")
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            items = [obj['Key'] for obj in response.get('Contents', [])]
            logging.info(f"Found {len(items)} items")
            return items
        except ClientError as e:
            logging.error(f"Failed to list items: {e}")
            return []
    
    def delete_items(self, keys):
        """Delete multiple items from S3"""
        if isinstance(keys, str):
            keys = [keys]
        logging.info(f"Deleting {len(keys)} items from bucket: {self.bucket_name}")
        try:
            delete_objects = [{'Key': key} for key in keys]
            self.s3.delete_objects(
                Bucket=self.bucket_name,
                Delete={'Objects': delete_objects}
            )
            logging.info(f"Successfully deleted items: {keys}")
            return True
        except ClientError as e:
            logging.error(f"Failed to delete items {keys}: {e}")
            return False
        
# Example usage:
s3 = S3Client('djp-s3')
s3.insert_item('file.txt', 'Hello World')
content = s3.download_item('file.txt')
if content:
    print(f"Downloaded content: {content.decode()}")
    with open('downloaded_file.txt', 'wb') as f:
        f.write(content)
    print("File saved as 'downloaded_file.txt'")
items = s3.list_items()
print(f"Items in bucket: {items}")

#s3.delete_items(['file.txt'])

