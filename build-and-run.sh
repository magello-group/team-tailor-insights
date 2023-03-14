echo "\n🐳 Build Docker image team-tailor-insights\n"

docker build -t team-tailor-insights .

echo "\n🚀 Run on TeamTailor Insights on :3000 with Basic Auth (usr and pwd as envs).\n"
docker run -it \
    -e API_TOKEN=$API_TOKEN \
    -e USER=$USER \
    -e PASSWORD=$PASSWORD \
    -p 3000:3000 \
    team-tailor-insights

sleep 5s

echo "\n💻 Loading applicants into database. This will take a couple of minutes.\n"
#curl http://localhost:3000/reload
