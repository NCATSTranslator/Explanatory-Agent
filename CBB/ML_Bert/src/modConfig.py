"""
WHAT: Defining application specific configuration. NOTE: You must set up a Google Storage bucket and define googleBucketPath!
WHY: Need to define input/output paths whether running in Docker or running directly on a Windows/Mac/Linux OS, paths would be different
ASSUMES: Docker environment if running from the Dockerfile because IS_DOCKER is injected there
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-08-28
"""

import os
from datetime import datetime

now = datetime.now()
isDocker = True if os.getenv("IS_DOCKER") == "TRUE" else False
localMountPath = "/mnt" if isDocker else os.path.join(os.path.dirname(os.getcwd()), "mnt")
logsFolderPath = os.path.join(localMountPath, "logs")
logFilePath = os.path.join(logsFolderPath, now.strftime('%Y-%m-%d_%H-%M-%S') + ".log")

googleBucketPath = "gs://<yourbucket>"  # set the bucket here
mountPath = os.path.join(googleBucketPath, "mnt").replace(os.sep, '/')
etlMountPath = os.path.join(googleBucketPath, "etl_mnt").replace(os.sep, '/')
tensorflowRecordMountPath = os.path.join(googleBucketPath, "tfrecords").replace(os.sep, '/')
tensorflowRecordFolderPath = os.path.join(tensorflowRecordMountPath, "sample_text").replace(os.sep, '/')

bertBaseFolderPath = os.path.join(etlMountPath, "unpacked/biobert_v1.1_pubmed").replace(os.sep, '/')
bertVocabFilePath = os.path.join(bertBaseFolderPath, "vocab_replace.txt").replace(os.sep, '/')
bertConfigFilePath = os.path.join(bertBaseFolderPath, "bert_config.json").replace(os.sep, '/')
bertModelCheckpointFilePath = os.path.join(bertBaseFolderPath, "model.ckpt").replace(os.sep, '/')

etlOutputFolderPath = os.path.join(etlMountPath, "output").replace(os.sep, '/')
inputTextFileFolderPath = os.path.join(etlOutputFolderPath, "sample_text").replace(os.sep, '/')
inputTextFileCount = 100
inputTextFileNames = [str(i).zfill(len(str(inputTextFileCount))) + ".txt" for i in list(range(inputTextFileCount))]
inputTextFilePaths = [os.path.join(inputTextFileFolderPath, inputTextFileName).replace(os.sep, '/') for inputTextFileName in inputTextFileNames]
tensorflowRecordFilePaths = [os.path.join(tensorflowRecordFolderPath, inputTextFileName.replace(".txt", ".tfrecord")).replace(os.sep, '/') for inputTextFileName in inputTextFileNames]
tensorflowRecordFilePathPattern = tensorflowRecordFolderPath + "/*.tfrecord"

outputFolderPath = os.path.join(mountPath, "output").replace(os.sep, '/')
outputRunFolderPath = os.path.join(outputFolderPath, now.strftime('%Y-%m-%d_%H-%M-%S')).replace(os.sep, '/')

tpuName = "bert-compute"
tpuZone = "us-central1-b"
max_seq_length = 512
max_predictions_per_seq = 80

