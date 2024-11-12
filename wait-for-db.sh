#!/bin/sh
# wait-for-db.sh

host="$1"
shift
until nc -z "$host" 3306; do
  echo "Waiting for MySQL..."
  sleep 2
done
exec "$@"
