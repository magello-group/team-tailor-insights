echo "\n🐳 Build Docker image team-tailor-insights\n"

docker build -t team-tailor-insights .

if [ -z "${API_TOKEN}" ]; then
    read -p "👉 API för lösning i TeamTailor: " API_TOKEN
fi

if [ -z "${WEB_USER}" ]; then
    read -p "👉 Användarnamn för webbinloggning: " WEB_USER
fi

if [ -z "${WEB_PASSWORD}" ]; then
    read -p "👉 Lösenord för webbinloggning: " WEB_PASSWORD
fi

if [ -z "${PORT}" ]; then
    echo "Using default port 3000"
    PORT=3000
fi

echo "\n🚀 Run TeamTailor Insights on port $PORT with Basic Auth (usr and pwd as envs).\n"

docker run -it \
    -e API_TOKEN=$API_TOKEN \
    -e USER=$WEB_USER \
    -e PASSWORD=$WEB_PASSWORD \
    -p 3000:$PORT \
    team-tailor-insights


#
# echo "\n💻 Loading applicants into database. This will take a couple of minutes.\n"
# curl http://localhost:3000/reload
#