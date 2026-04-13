#!/bin/bash

# Function to check PostgreSQL availability
# Helper to get the first non-empty environment variable
get_env() {
  for var in "$@"; do
    value="${!var}"
    if [ -n "$value" ]; then
      echo "$value"
      return
    fi
  done
}

check_postgres() {
  local db_host
  local db_user
  local db_name
  local db_pass

  db_host=$(get_env PGHOST)
  db_user=$(get_env PGUSER POSTGRES_USER)
  db_name=$(get_env PGDATABASE POSTGRES_DB)
  db_pass=$(get_env PGPASSWORD POSTGRES_PASSWORD)

  PGPASSWORD="$db_pass" psql -h "$db_host" -U "$db_user" -d "$db_name" -c '\q' >/dev/null 2>&1
}


# Wait for PostgreSQL to become available
until check_postgres; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - continuing..."

# run sql commands
# psql -h "$PGHOST" -U "$PGUSER" -d "$PGDATABASE" -f /app/backend/init-postgis.sql

# Apply Django migrations
python manage.py migrate

# Create superuser if environment variables are set and there are no users present at all.
if [ -n "$DJANGO_ADMIN_USERNAME" ] && [ -n "$DJANGO_ADMIN_PASSWORD" ] && [ -n "$DJANGO_ADMIN_EMAIL" ]; then
  echo "Creating superuser..."
  python manage.py shell << EOF
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

User = get_user_model()

# Check if the user already exists
if not User.objects.filter(username='$DJANGO_ADMIN_USERNAME').exists():
    # Create the superuser
    superuser = User.objects.create_superuser(
        username='$DJANGO_ADMIN_USERNAME',
        email='$DJANGO_ADMIN_EMAIL',
        password='$DJANGO_ADMIN_PASSWORD'
    )
    print("Superuser created successfully.")

    # Create the EmailAddress object for AllAuth
    EmailAddress.objects.create(
        user=superuser,
        email='$DJANGO_ADMIN_EMAIL',
        verified=True,
        primary=True
    )
    print("EmailAddress object created successfully for AllAuth.")
else:
    print("Superuser already exists.")
EOF
fi


# Sync the countries and world travel regions
# Retry logic for download-countries (can fail with exit code 137 due to OOM)
max_retries=3
retry_count=0
while [ $retry_count -lt $max_retries ]; do
  >&2 echo "Downloading countries data (attempt $((retry_count + 1))/$max_retries)..."
  python manage.py download-countries
  exit_code=$?

  if [ $exit_code -eq 0 ]; then
    >&2 echo "Countries data downloaded successfully."
    break
  elif [ $exit_code -eq 137 ]; then
    >&2 echo "WARNING: download-countries was interrupted (exit code 137). This is likely due to insufficient memory."
    retry_count=$((retry_count + 1))
    if [ $retry_count -lt $max_retries ]; then
      >&2 echo "Retrying in 5 seconds... ($retry_count/$max_retries)"
      sleep 5
    else
      >&2 echo "ERROR: download-countries failed after $max_retries attempts. Please allocate more memory to the container."
      exit 1
    fi
  else
    >&2 echo "ERROR: download-countries failed with exit code $exit_code"
    exit 1
  fi
done

cat /code/adventurelog.txt

exec "$@"