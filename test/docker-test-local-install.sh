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
        -v ~/git/colorview2d/:/colorview2d/ \
        -v ~/git/colorview2d/Makefile:/home/cvuser/Makefile \
        -v ~/git/colorview2d/test:/home/cvuser/test \
	colorview2d /bin/bash \
	-c "cd colorview2d;python setup.py install --user;cd;make testlocal"
