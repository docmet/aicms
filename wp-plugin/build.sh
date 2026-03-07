#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
rm -f mystorey-connector.zip
zip -r mystorey-connector.zip mystorey-connector/
echo "Built: mystorey-connector.zip"
