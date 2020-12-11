docker build -t ml_bert .
docker run --rm -d -v "${PWD}"/mnt:/mnt -it --entrypoint /bin/bash --name ml_bert_container ml_bert -s