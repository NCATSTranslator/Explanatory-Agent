docker build -t etl_bertprep .
docker run -v "${PWD}"/mnt:/mnt --add-host host.docker.internal:172.17.42.1 --name etl_bertprep_container etl_bertprep