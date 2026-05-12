#!/bin/bash
set -e
echo "==> ClimateSmartTriage dev setup"
pip install -r requirements.txt
if command -v ollama &>/dev/null; then
    echo "==> Pulling Gemma 2B quantised model (1.8 GB) …"
    ollama pull gemma:2b-instruct-q4_K_M
else
    echo "WARNING: Ollama not found. Install from https://ollama.ai"
fi
echo "==> Running data ingestion pipeline …"
python data_ingestion/pipeline.py --output ./data
echo ""
echo "Setup complete."
echo "Start server:  docker-compose -f deployment/docker-compose.yml up"
echo "Run tests:     bash scripts/run_tests.sh"
