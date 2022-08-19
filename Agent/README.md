# Explanatory Autonomous Relay Agent

An API which relays a node-edge graph.

How to run:

The Agent web service is composed of two Docker containers: A PostgreSQL container containing data to direct processing and a Python container which hosts the REST API. The PostgreSQL container must be populated with data from a dump file first, before the REST API will function.

The following steps will build a container, populate it, and build then run the REST API.

1. Start the Postgres Docker container (NOTE: a volume will be mounted in the current working directory to store the Postgres data):

```
docker run --rm \
-v /"${PWD}"/postgres_data:/var/lib/postgresql/data \
-p 5432:5432 \
--name xara-postgres \
-e POSTGRES_PASSWORD=postgres \
-e POSTGRES_DB=xARA \
-d postgres:11.12-buster
```

2. Load the database data (be sure to specify the path to the xARA_Backup.sql file):
```
docker exec -i xara-postgres /bin/bash \
-c "PGPASSWORD=postgres psql \
--username postgres xARA" < /path/to/xARA_Backup.sql
```

3. Build the web service Docker image:
```
docker build \
--add-host host.docker.internal:172.17.0.1 \
-t translator-explanatory-agent \
--no-cache ./Agent
```

4. Start the container:
```
docker run --rm -d -p 80:80 \
--add-host host.docker.internal:172.17.0.1 \
--name translator-explanatory-agent_container \
translator-explanatory-agent
```

5. Verify the webservice is working by navigating to `http://localhost/health`. You should see a message similar to
`{"message":"API and Database are up! Database host host.docker.internal with timestamp: <current date and time>"}`
