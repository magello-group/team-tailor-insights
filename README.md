# Insights into Team Tailor candidate communication

* Install dependencies via `poetry install`
* Run via `[Environment variables - see below] ./run.sh`
* To reload data go to `http://localhost:3000/reload`. For login/password see environment variables below.
* To view insights web app browse to `http://localhost:3000`

## Environment variables

* API_TOKEN - Team Tailor API token with admin rights
* USER - Basic auth user
* PASSWORD - Basic auth password

## Build & run as container

```bash
docker build -t insights . &&  \
docker run -it \
    -e API_TOKEN=[token] \
    -e USER=[user] \
    -e PASSWORD=[password] \
    -p 3000:3000 \
    insights
```
