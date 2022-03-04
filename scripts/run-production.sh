#!/usr/bin/env bash

# Unless otherwise specified, we'll deploy the latest version
version="latest"

if [ "$1" = "--version" ]; then
   version="$2"
fi

docker login -u `cat ~/docker.username` -p `cat ~/docker.password` docker.nmbu.no:5000

if grep -qi Microsoft /proc/sys/kernel/osrelease
then
  echo "Running on Windows. Using \"docker-compose.exe\" as executable"
  docker_compose=docker-compose.exe
else
  echo "Running on Linux. Using \"docker-compose\" as executable"
  docker_compose=docker-compose
fi

VERSION=${version} CURRENT_UID=$(id -u):$(id -g) $docker_compose -f docker-compose.production.yml down
VERSION=${version} CURRENT_UID=$(id -u):$(id -g) $docker_compose -f docker-compose.production.yml up -d
