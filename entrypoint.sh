#!/bin/bash

set -e

echo "Starting Attendee FastAPI entrypoint..."

# Wait for database to be ready
echo "Waiting for database..."
while ! pg_isready -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER; do
  echo "Database is unavailable - sleeping"
  sleep 1
done
echo "Database is up - continuing..."

# Set environment variables
export PYTHONPATH=/attendee_fastapi
export DISPLAY=:99

# Start Xvfb for headless Chrome
echo "Starting Xvfb..."
Xvfb :99 -screen 0 1920x1080x24 &

# Start PulseAudio for audio capture
echo "Starting PulseAudio..."
pulseaudio --start --exit-idle-time=-1 &

# Run database migrations if needed
echo "Running database setup..."
python -c "
import asyncio
from app.core.database import create_tables

async def setup_db():
    await create_tables()
    print('Database tables created successfully')

asyncio.run(setup_db())
"

# Execute the command passed to the container
echo "Executing command: $@"
exec "$@" 