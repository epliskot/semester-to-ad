#!/bin/bash

for command in down down up; do docker-compose.exe -f docker-compose.development.yml $command; done
