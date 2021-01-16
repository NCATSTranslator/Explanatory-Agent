# Cord BioBert

Generates a trained BioBert model using the CORD-19 data set. There are several manual steps to start each process, so please follow carefully! The final step, which performs model training, is expected to run on Google Cloud servers. 

Please refer to https://github.com/dmis-lab/biobert for pretrained model checkpoints and https://github.com/google-research/bert for pretraining details.

## Step 1: Start DB_MySQL Container

```bash
cd DB_MySQL
sh run.sh
```

Wait at least 2 minutes before continuing.  Check the docker logs to see if it's ready for connections:

```bash
docker logs db_mysql_container
```

## Step 2: Run ETL_CordDocs Container

```bash
cd ETL_CordDocs
sh run.sh
```

## Step 3: Run ETL_BioWords Container

Add files "proteins.json" and "diseases.json" to "ETL_BioWords/mnt/input" folder
```bash
cd ETL_BioWords
sh run.sh
```

## Step 4: Run ETL_CordReplace Container

```bash
cd ETL_CordReplace
sh run.sh
```

## Step 5: Run ETL_BertPrep Container

```bash
cd ETL_BertPrep
sh run.sh
```

## Step 6: Stop DB_MySQL Container
This container isn't needed anymore to run the Bert model.  It's using resources.
The data will not be deleted by stopping or deleting the container.  The data is mounted on the host drive at "DB_MySQL/data" folder.

```bash
docker kill db_mysql_container
```

## Step 7: Run ML_Bert Container

Add sample_text.txt to ETL_BertPrep/mnt/output, link here:
https://raw.githubusercontent.com/google-research/bert/master/sample_text.txt

You must configure a Google Storage Bucket (https://cloud.google.com/storage/docs/creating-buckets), as this module uses Google TPUs for training. Once defined, please set the configuration in ML_BERT/src/modConfig.py.

```bash
cd ML_Bert
sh run.sh
```

The output files and the log for the run will be located in ML_Bert/mnt/output/%run_date%/.

Once the container functionality is confirmed, make changes to run the real data set:
* src/modConfig.py -> Change inputTextFileName to "documents.txt" (it is currently "sample_text.txt")
* src/tasks/clsCreatePretrainingDataTask.py -> Update self.parameters per the study requirements
* src/tasks/clsRunPretrainingTask.py -> Update self.parameters per the study requirements

## Extra Information

GitHub's Dependabot issues a security warning due to the workflow requiring TensorFlow v1.11, as it has issues of varied severity. Unfortunately, the code from Bert's create_pretraining.py will not run in a Google VM on any newer version. The security concerns are due to code execution or memory access via loaded model checkpoint files. As is the case of all external files, please make sure you are getting them from trusted, verified sources and, where possible, confirm the file's contents via checksum.