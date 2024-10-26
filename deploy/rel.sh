./build-all.sh
./push_to_docker_repo.sh $1
./go-remote.sh ssd rel $1

