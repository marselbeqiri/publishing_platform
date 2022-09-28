Ready-To-Deploy Django, gunicorn, NGINX, Docker Application

# publishing_platform

### Setup

> docker-compose up --build

By executing above command, project will be ready to be consumed.
If you want to use virtualenv, please follow instructions of Dockerfile and docker-compose.

#### Admin Account (use this to login on swagger. /swagger)

```
username='admin'
password='Demo@123!##'
```

#### Blogger Account

```
username='blogger'
password='Demo@123!##'
```

### Tests
```
docker exec -it publishing_platform_web_1 /bin/sh
```
```
python manage.py test
```


### Docs

Multiple options to check:

- see swagger.yaml on project files and open it on [here](https://editor.swagger.io/ )
- go to path **/swagger** -> make sure to do Django Login with admin account
- go to path **/redoc**  -> make sure to do Django Login with admin account
