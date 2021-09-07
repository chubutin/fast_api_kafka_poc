# FastAPI, Kafka and AsyncIO threads

Blank template for FastAPI, Kafka and AsincIO features.


## How to start the project

`docker-compose up --build`

The app always fail to start, even though it depends on kafka and zookeeper and those services already have healthchecks.
So, after starting docker-compose you'll see the app failing. In this case, start the app as a service alone


`docker-compose up --build -d app consumer`

Note: consumer app has replica=2 on docker compose in order to test multi consumers per topic and groups

### Check Kafka status

This service uses [Kafka-UI](https://github.com/provectus/kafka-ui) as a web browser interactive status manager for Kafka. 
You can check the status for your local Broker acessing to http://localhost:9000/ once the docker compose is running


### cURL to the app

http://localhost:8000/send_message is a mapped REST endpoint for sending messages to the broker

### Considerations for MultiProcessing on message consumption

If the topic is created by aiokafka Producer it will only have one partition per topic, this means only one consumer
will be connected to the topic (per group-id). If you want multiple consumers per topic/group you need to create the topic
on Kafka-UI and assign at least two partitions to the topic `poc_topic`

### References

https://www.confluent.io/blog/kafka-client-cannot-connect-to-broker-on-aws-on-docker-etc/


https://github.com/provectus/kafka-ui


https://enmilocalfunciona.io/aprendiendo-apache-kafka-parte-2-2/
