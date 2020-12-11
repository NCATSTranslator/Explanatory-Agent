docker build -t etl_cordreplace .
docker run -v "${PWD}"/mnt:/mnt --add-host host.docker.internal:172.17.42.1 --name etl_cordreplace_container etl_cordreplace