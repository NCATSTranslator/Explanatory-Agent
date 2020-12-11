export PROJECT_NAME=festive-radar-268519

# normal
ctpu up \
 --tpu-size=v3-8 \
 --machine-type=n1-standard-16 \
 --zone=us-central1-b \
 --tf-version=1.11 \
 --name=bert-compute \
 --project $PROJECT_NAME

# vm only
ctpu up \
 --vm-only \
 --machine-type=n1-standard-16 \
 --zone=us-central1-b \
 --tf-version=1.11 \
 --name=bert-compute \
 --project $PROJECT_NAME

# test
ctpu up \
 --tpu-size=v2-8 \
 --preemptible \
 --machine-type=n1-standard-4 \
 --preemptible-vm \
 --zone=us-central1-b \
 --tf-version=1.11 \
 --name=bert-compute \
 --project $PROJECT_NAME

# vm monitoring agent
gcloud beta compute ssh bert-compute \
 --project=festive-radar-268519 \
 --zone=us-central1-b \
 --command="curl -sSO https://dl.google.com/cloudagents/add-monitoring-agent-repo.sh && sudo bash add-monitoring-agent-repo.sh && sudo apt-get update && sudo apt-get install stackdriver-agent && sudo service stackdriver-agent start"

# tear down
ctpu delete \
 --name=bert-compute \
 --project $PROJECT_NAME

