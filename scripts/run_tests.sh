#!/bin/bash
set -e
echo "==> Running ClimateSmartTriage test suite"
pytest backend/tests/ -v --tb=short
echo "All tests passed."
