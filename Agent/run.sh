docker build -t api_xara . --no-cache
docker rm --force api_xara_container || true
docker run --rm -d -p 80:80 --add-host host.docker.internal:172.17.42.1 --name api_xara_container api_xara
