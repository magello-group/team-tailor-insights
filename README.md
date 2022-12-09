# Insights into Team Tailor candidate communication

* Run via `[Environment variables - see below] ./run.sh`
* To reload data run `curl -u "login:password" -XPOST localhost:5000/reload`. For login/password see environment variables below.
* To view insights web app browse to `http://localhost:5000`

## Environment variables

* API_TOKEN - Team Tailor API token with admin rights
* USER - Basic auth user
* PASSWORD - Basic auth password