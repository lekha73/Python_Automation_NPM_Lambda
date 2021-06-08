import boto3
import logging

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket='9514-loaaccelerator-prod'
    response = s3.list_objects(
        Bucket=bucket,
        Prefix='PTOAccrued_to_Process'
    )
    try:
      subfolder_filename=(response['Contents'][1]['Key'])
      split_ff=subfolder_filename.split("/")
      filename=split_ff[1]
      print(filename)
      #logging.info(filename)
      destination = "PTOAccrued/"+filename
      if filename is not None or (filename == 0):
        #subprocess.run('aws s3 mv s3://$filename s3://9514-loaaccelerator-prod/PTOAccrued/')
        copy_S3 = s3.copy_object(
            Bucket=bucket,
            CopySource={'Bucket': bucket, 'Key': subfolder_filename},
            Key=destination
        )
        print(copy_S3)
        #logging.info(copy_S3)
        delete_S3 = s3.delete_object(
            Bucket=bucket,
            Key=subfolder_filename
        )
        print(delete_S3)
        #logging.info(delete_S3)
    except IndexError:
      print("no objects found")
      #logging.info("no objects found")