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
	-v /home/al/git/colorview2d/Makefile:/colorview2d/Makefile \
	-v /home/al/git/colorview2d/test:/colorview2d/test \
	-v /home/al/git/colorview2d/spam.log:/colorview2d/spam.log \
	colorview2d /bin/bash \
	-c "pip install --upgrade --index-url https://testpypi.python.org/pypi/ colorview2d;cd colorview2d;make testpip"
