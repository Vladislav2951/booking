#!/usr/bin/env bash

echo "Apply migrations..."
export PYTHONPATH=$PYTHONPATH:/app/src

alembic upgrade head

echo "Migrations applied successfully."

exec "$@"