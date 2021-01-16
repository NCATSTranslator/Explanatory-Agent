docker build -t api_xara .
docker run --rm -d -p 80:80 --name api_xara_container api_xara