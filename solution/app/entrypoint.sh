#!/bin/bash

# Init data
python postgres_init.py
python redis_init.py

# Start app
python app.py