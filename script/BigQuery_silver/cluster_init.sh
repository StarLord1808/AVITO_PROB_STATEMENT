#!/bin/bash

# Update package list
apt-get update -y

# Install Python dependencies
pip install --upgrade pip
pip install faker geopy pandas numpy pyarrow google-cloud-bigquery google-cloud-storage requests

# Verify installation
pip list
