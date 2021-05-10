docker build -t api_xara . --no-cache
docker run --rm -d -p 80:80 -it --add-host host.docker.internal:172.17.42.1 --entrypoint /bin/bash --name api_xara_container api_xara -s
