docker build -t etl_biowords .
docker run -v "${PWD}"/mnt:/mnt -it --add-host host.docker.internal:172.17.42.1 --entrypoint /bin/bash --name etl_biowords_container etl_biowords -s