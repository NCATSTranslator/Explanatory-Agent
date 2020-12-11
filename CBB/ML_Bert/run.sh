docker build -t ml_bert .
docker run --rm -d -v "${PWD}"/mnt:/mnt --name ml_bert_container ml_bert