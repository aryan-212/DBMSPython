#!/usr/bin/env bash
# wait-for-it.sh

host=$1
shift
cmd="$@"

until nc -z "$host" 3306; do
  echo "Waiting for MySQL..."
  sleep 1
done

echo "MySQL is up - executing command"
exec $cmd
