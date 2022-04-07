#!/bin/sh

DOCKER_COMPOSE="${HOME}/docker-compose.yml"
DOCKER_COMPOSE_STACK="${HOME}/docker-compose-stack.yml"

docker compose -f "${DOCKER_COMPOSE}" pull
docker compose -f "${DOCKER_COMPOSE}" up -d --remove-orphans

deploy_stack () {
    ENV_FILE="${HOME}/${1}.env"
    if [ -f ${ENV_FILE} ]; then
        docker-compose -f "${DOCKER_COMPOSE_STACK}" --env-file "${ENV_FILE}" pull
        docker-compose -f "${DOCKER_COMPOSE_STACK}" --env-file "${ENV_FILE}" --project-name "${1}" up -d --remove-orphans
    fi
}

deploy_stack development
deploy_stack production
