# Big Data Challenge


## Twitter Dumper

### config.json template

```json
{
    "twitter": {
        "customer_key": "<customer_key>",
        "customer_secret": "<customer_secret>",
        "access_token": "<access_token>",
        "token_secret": "<token_secret>",
        "bearer_token": "<bearer_token>"
    },
    "mongo_db": {
        "username": "<username>",
        "password": "<password>",
        "host": "<host>"
    },
    "dumper": {
        "username": "elonmusk",
        "user_tweets": {
            "start_time": "2021-01-01T00:00:00",
            "max_number": 15000
        },
        "search_tweets": {
            "start_time": "2022-01-01T00:00:00",
            "max_number": 15000
        }
    }
}
```

## Kafka

### Start Kafka containers

```bash
docker-compose -f kafka/docker-compose.yml up -d
```

### Stop Kafka containers

```bash
docker-compose -f kafka/docker-compose.yml down
```

### Create topic

```bash
docker exec broker \
kafka-topics \
--bootstrap-server broker:9092 \
--create \
--topic search_tweets
```

### Remove topic

```bash
docker exec broker \
kafka-topics \
--bootstrap-server broker:9092 \
--delete \
--topic search_tweets
```

### List of topics

```bash
docker exec broker \
kafka-topics \
--bootstrap-server broker:9092 \
--list
```

### Write topic

```bash
docker exec --interactive --tty broker \
kafka-console-producer \
--bootstrap-server broker:9092 \
--topic search_tweets
```

### Read topic

```bash
docker exec --interactive --tty broker \
kafka-console-consumer \
--bootstrap-server broker:9092 \
--topic search_tweets \
--from-beginning
```