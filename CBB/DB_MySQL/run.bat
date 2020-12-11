docker run^
  --name db_mysql_container^
  -p 12345:3306^
  -v %cd%/data:/var/lib/mysql^
  -v %cd%/init:/docker-entrypoint-initdb.d^
  -e MYSQL_ROOT_PASSWORD=corddatabase^
  -e MYSQL_USER=corddatabase^
  -e MYSQL_PASSWORD=corddatabase^
  -e MYSQL_DATABASE=cord-bert^
  -d^
  mysql:8^
  --innodb-dedicated-server=TRUE^
  --local-infile=TRUE