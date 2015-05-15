# run bash within datacats/web with bind mounted ssh keys&config files
# so that you can ssh to the remote server within the docker

docker run \
    -it \
    -v  ~/.datacats/user-profile/id_rsa:/root/.ssh/id_rsa \
    -v  ~/datacats/datacats/scripts/known_hosts:/root/.ssh/known_hosts \
    -v  ~/datacats/datacats/scripts/ssh_config:/etc/ssh/ssh_config \
        datacats/web \
            bash
