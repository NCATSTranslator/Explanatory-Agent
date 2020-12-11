docker build -t etl_corddocs .
docker run -v "${PWD}"/mnt:/mnt --add-host host.docker.internal:172.17.42.1 --name etl_corddocs_container etl_corddocs