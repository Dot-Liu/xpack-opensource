#!/bin/sh

set -e

Version=$1
ImageName=$2
APP="xpack"

ARCH=amd64

Tar="${APP}.${Version}.${ARCH}.tar.gz"

echo "docker save -o ${Tar} ${ImageName}:${Version}"
docker save -o ${Tar} ${ImageName}:${Version}

echo "login qiniu..."
qshell account ${AccessKey} ${SecretKey} ${QINIU_NAME}

echo "qshell rput ${QINIU_BUCKET} \"${APP}/images/${Tar}\" ${Tar}"
qshell rput ${QINIU_BUCKET} "${APP}/images/${Tar}" ${Tar}

rm -f ${Tar}
docker rmi -f ${ImageName}:${Version}