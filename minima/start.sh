#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$SCRIPT_DIR/data"
JAR_PATH="$SCRIPT_DIR/minima.jar"
RPC_PORT=9005
P2P_PORT=9001

mkdir -p "$DATA_DIR"

echo "Starting Minima Node (Headless Mode)"
echo "======================================"
echo "Data Directory: $DATA_DIR"
echo "RPC Port: $RPC_PORT"
echo "P2P Port: $P2P_PORT"
echo ""

exec java -Xmx1G -jar "$JAR_PATH" \
    -data "$DATA_DIR" \
    -basefolder "$DATA_DIR" \
    -rpcenable \
    -rpc $RPC_PORT \
    -port $P2P_PORT \
    -p2pnodes megammr.minima.global:9001
