# FastAPI, Kafka and AsyncIO threads

Blank template for FastAPI, Kafka and AsincIO features.


## How to start the project

`docker-compose up --build`

The app always fail to start, even though it depends on kafka and zookeeper and those services already have healthchecks.
So, after starting docker-compose you'll see the app failing. In this case, start the app as a service alone


`docker-compose up --build -d app`


### Check Kafka status

This service uses [Kafka-UI](https://github.com/provectus/kafka-ui) as a web browser interactive status manager for Kafka. 
You can check the status for your local Broker acessing to http://localhost:9000/ once the docker compose is running


### cURL to the app

http://localhost:8000/send_message is a mapped REST endpoint for sending messages to the broker



### References

https://www.confluent.io/blog/kafka-client-cannot-connect-to-broker-on-aws-on-docker-etc/


https://github.com/provectus/kafka-ui


https://enmilocalfunciona.io/aprendiendo-apache-kafka-parte-2-2/
