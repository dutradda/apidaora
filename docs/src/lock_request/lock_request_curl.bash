python -c 'import json; open("/tmp/large.json", "w+").write(json.dumps(list(range(1000000))))'

curl -i localhost:8000/lock-request -X POST -T /tmp/large.json &
curl -i localhost:8000/lock-request -X POST -T /tmp/large.json &
curl -i localhost:8000/lock-request -X POST -T /tmp/large.json &
sleep 1
curl -i localhost:8000/lock-request -X POST -T /tmp/large.json
