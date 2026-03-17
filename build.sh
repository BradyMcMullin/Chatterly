#!/bin/bash

echo "🗑️ Deleting old database..."
rm -f network.db

echo "🏗️ Building fresh schema..."
sqlite3 network.db <schema.sql

echo "🌱 Seeding database with mock data..."
python3 seed_db.py

echo "✅ Database network.db is fully rebuilt and seeded! You are ready to run app.py."
