
# This is an implementation of microservice architecture for FastAPI which is implementing the clean architecture and Repository Pattern.
## Tools and Tech
    * Docker and Docker-compose
    * MondoDB
    * RabbitMQ
    * Redis
    * Celery and Flower
    * FastAPI
    * MyPy Support
    * Nginx
## Run Application with docker:
#### Change all the dev.*.env files to *.env
### Development
    docker-compose -f docker-compose.dev.yml  up --build -d

### Production
    docker-compose -f docker-compose.prod.yml  up --build -d
