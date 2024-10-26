#!/bin/bash
IMAGE=chatbot_app
IMAGE_LLM=llm_app
echo "building express and py apps env $BUILD_ENV"

cd ../
echo "building back end docker image.."
docker build --no-cache -t $IMAGE .

cd python
echo "building back end docker image.."
docker build --no-cache -t $IMAGE_LLM .


cd ../deploy
echo "completed building and creating docker images"
echo "================================================================"
echo "execute ./push_to_docker_repo.sh after this build is verified"
