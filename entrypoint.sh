#!/bin/sh

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until pg_isready -h db -p 5432; do
  sleep 1
done

echo "PostgreSQL is ready!"

# Apply database migrations
python manage.py migrate

# Run both the server and the task processor
echo "Starting Django runserver and background task processor..."
python manage.py runserver 0.0.0.0:8000 &  # Start the server in the background
python manage.py process_tasks             # Run the background task processor
