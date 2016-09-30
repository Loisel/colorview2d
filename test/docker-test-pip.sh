#!/bin/bash -i
XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth
touch $XAUTH
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -
docker run -ti \
        --volume=$XSOCK:$XSOCK:rw \
        --volume=$XAUTH:$XAUTH:rw \
        --env="XAUTHORITY=${XAUTH}" \
        --env="DISPLAY" \
        --user="cvuser" \
	-v /home/al/git/colorview2d/Makefile:/home/cvuser/Makefile \
	-v /home/al/git/colorview2d/test:/home/cvuser/test \
	-v /home/al/git/colorview2d/:/colorview2d/ \
	colorview2d /bin/bash \
	-c "pip install --upgrade pip;pip install --upgrade --user --index-url https://testpypi.python.org/pypi/ colorview2d;cd;make testpip"

