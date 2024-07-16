#!/bin/bash

namespace="$(nuv -config -d | grep NUVDEV_USERNAME | cut -d'=' -f2)"

echo "setting namespace: $namespace"

# sed -i "s@#--annotation url https:\/\/walkiria.cloud\/api\/v1\/web\/{os.environ\[\x27__OW_NAMESPACE\x27\]}@#--annotation\ url\ https:\/\/walkiria.cloud\/api\/v1\/web\/$namespace@" packages/*/*.py packages/*/*/*.py
# sed -i "s@#--annotation url https:\/\/walkiria.cloud\/api\/v1\/namespaces\/{os.environ\[\x27__OW_NAMESPACE\x27\]}@#--annotation\ url\ https:\/\/walkiria.cloud\/api\/v1\/namespaces\/$namespace@" packages/*/*.py packages/*/*/*.py

sed -i "s@{os.environ\[\x27__OW_NAMESPACE\x27\]}@$namespace@g" packages/*/*.py packages/*/*/*.py
sed -i "s@\[os.environ\[\x27__OW_NAMESPACE\x27\]\]@\['$namespace'\]@g" packages/*/*.py packages/*/*/*.py

nuv action update root packages/base/root.py --annotation provide-api-key true --param $(cat .env | grep CONNECTION_STRING | tr '=' ' ')
nuv invoke root --result
# rm -rf packages/base/root.py
# echo JWT_SECRET=$(openssl rand -base64 48) >> .env