#!/bin/bash

echo "Stopping EKP Development Environment..."

cd "$(dirname "$0")"

docker-compose down

echo ""
echo "Do you want to remove volumes as well? (y/N)"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Removing volumes..."
    docker-compose down -v
    echo "Volumes removed."
fi

echo ""
echo "EKP Development Environment stopped."
