#!/bin/sh

DOCKER_COMPOSE_YML="${HOME}/docker-compose.yml"
docker compose -f ${DOCKER_COMPOSE_YML} pull
docker compose -f ${DOCKER_COMPOSE_YML} up -d --remove-orphans
