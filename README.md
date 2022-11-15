
## Run Application with docker:
#### Change all the dev.*.env files to *.env
### Development
    docker-compose -f docker-compose.dev.yml  up --build -d

### Production
    docker-compose -f docker-compose.prod.yml  up --build -d
