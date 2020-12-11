"""
WHAT: Defining application miscellaneous utilities
WHY: Need to define miscellaneous utilities
ASSUMES: Running on Google Cloud
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-09-26
"""

from google.cloud import storage
from apiclient import discovery
import json
import logging


def printAndLog(msg):
    """
    Helper function to print and logging.info
    :param msg: Any message
    :return: None
    """
    print(msg)
    logging.info(msg)


def bucketFileExists(bucketFilePath):
    """
    Checks whether a file exists or not in a Google bucket
    :param bucketFilePath: The full file path in the bucket, like 'gs://mybucket/myfolder/myfile.txt"
    :return: Boolean, true if the file exists, false if it does not exist
    """
    bucketName = bucketFilePath.split("/")[2]
    bucketFileName = "/".join(bucketFilePath.split('/')[3:])
    client = storage.Client()
    bucket = client.bucket(bucket_name=bucketName)
    blob = storage.Blob(bucket=bucket, name=bucketFileName)
    return blob.exists(client=client)


def getBucketFolderFileList(bucketFolderPath):
    if bucketFolderPath.endswith("/"):
        bucketFolderPath = bucketFolderPath[:-1]
    bucketName = bucketFolderPath.split("/")[2]
    bucketFolderName = "/".join(bucketFolderPath.split('/')[3:])

    client = discovery.build('storage', 'v1')
    request = client.objects().list(bucket=bucketName, prefix=bucketFolderName)
    while request is not None:
        response = request.execute()
        printAndLog(json.dumps(response, indent=2))
        request = request.list_next(request, response)

# def getBucketFolderFileList(bucketFolderPath):
#     """
#     Returns the list of files in a bucket folder path
#     :param bucketFolderPath: The full folder path in the bucket, like 'gs://mybucket/myfolder'
#     :return: A list of file names
#     """
#     if bucketFolderPath.endswith("/"):
#         bucketFolderPath = bucketFolderPath[:-1]
#     bucketName = bucketFolderPath.split("/")[2]
#     bucketFolderName = "/".join(bucketFolderPath.split('/')[3:])
#     client = storage.Client()
#     for blob in client.list_blobs(bucketName, prefix=bucketFolderName):
#         print(str(blob))



# def uploadFileToBucket(localFilePath, bucketFilePath):
#     """
#     Copy a local file to a Google cloud bucket
#     :param localFilePath: Full path of the file on the local OS
#     :param bucketFilePath: Full path of the file on the Google bucket, like 'gs://mybucket/myfolder/myfile.txt'
#     :return: string, Blob url of new file in bucket
#     """
#     bucketName = bucketFilePath.split("/")[2]
#     bucketFileName = "/".join(bucketFilePath.split('/')[3:])
#     client = storage.Client()
#     bucket = client.bucket(bucket_name=bucketName)
#     blob = storage.Blob(bucket=bucket, name=bucketFileName)
#     blob.upload_from_filename(filename=localFilePath)
#     return blob.public_url
