#!/bin/bash

DOCKER_USER=siyothsoft
DOCKER_HOST=45.32.222.104
#PASSWORD=XXXX comes from source .env
IMAGE=chatbot_app
IMAGE_LLM=llm_app

echo "login to docker repo..."
echo "enter password for docker repository"$DOCKER_HOST
docker login --username=$DOCKER_USER $DOCKER_HOST --password=$PASSWORD


echo "pushing chatbot_app:latest to docker repo.."
docker tag $IMAGE:latest $DOCKER_HOST/$IMAGE:latest
if [ "$1" == "web" ]; then
  docker push $DOCKER_HOST/$IMAGE:latest
fi
echo "pushing llm_app:latest to docker repo.."
docker tag $IMAGE_LLM:latest $DOCKER_HOST/$IMAGE_LLM:latest
if [ "$2" == "llm" ]; then
  docker push $DOCKER_HOST/$IMAGE_LLM:latest
fi

echo "completed pushing to repo.."
echo "================================================================"
echo "login to hosting site"
echo "[cd $IMAGE/deploy]"
echo "[run ./build-remote.sh]"

