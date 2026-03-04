#!/bin/bash

echo "Deleting old database..."
rm -f network.db

echo "Building schema and seeding data..."
sqlite3 network.db <schema.sql

echo "Database network.db is ready!"
