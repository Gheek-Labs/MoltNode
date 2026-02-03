#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$SCRIPT_DIR/data"
JAR_PATH="$SCRIPT_DIR/minima.jar"
RPC_PORT=9005
P2P_PORT=9001
MDS_PORT=9003

mkdir -p "$DATA_DIR"

# ============================================
# MDS Password Security
# ============================================

validate_password_entropy() {
    local password="$1"
    local errors=()
    
    # Minimum 16 characters
    if [[ ${#password} -lt 16 ]]; then
        errors+=("- Must be at least 16 characters (currently ${#password})")
    fi
    
    # Must contain lowercase
    if ! [[ "$password" =~ [a-z] ]]; then
        errors+=("- Must contain at least one lowercase letter")
    fi
    
    # Must contain uppercase
    if ! [[ "$password" =~ [A-Z] ]]; then
        errors+=("- Must contain at least one uppercase letter")
    fi
    
    # Must contain number
    if ! [[ "$password" =~ [0-9] ]]; then
        errors+=("- Must contain at least one number")
    fi
    
    # Must contain symbol
    if ! [[ "$password" =~ [^a-zA-Z0-9] ]]; then
        errors+=("- Must contain at least one symbol (!@#$%^&* etc.)")
    fi
    
    if [[ ${#errors[@]} -gt 0 ]]; then
        echo "ERROR: MDS_PASSWORD does not meet security requirements:"
        printf '%s\n' "${errors[@]}"
        return 1
    fi
    return 0
}

generate_secure_password() {
    # Generate 28-char password with guaranteed high entropy
    # 24 random chars + !Aa1 for guaranteed complexity
    printf '%s!Aa1' "$(openssl rand -base64 32 | tr -d '/+=' | head -c 24)"
}

# Check if MDS_PASSWORD is set
if [[ -z "$MDS_PASSWORD" ]]; then
    echo ""
    echo "WARNING: MDS_PASSWORD not set. Generating secure password..."
    MDS_PASSWORD="$(generate_secure_password)"
    echo ""
    echo "============================================"
    echo "GENERATED MDS PASSWORD (save this securely):"
    echo "$MDS_PASSWORD"
    echo "============================================"
    echo ""
    echo "To set permanently, add MDS_PASSWORD to your secrets."
    echo ""
fi

# Validate password entropy
if ! validate_password_entropy "$MDS_PASSWORD"; then
    echo ""
    echo "FATAL: MDS_PASSWORD failed security validation. Node will not start."
    echo "Please set a strong password with: 16+ chars, uppercase, lowercase, number, symbol"
    exit 1
fi

echo "Starting Minima Node (Headless Mode)"
echo "======================================"
echo "Data Directory: $DATA_DIR"
echo "RPC Port:       $RPC_PORT"
echo "P2P Port:       $P2P_PORT"
echo "MDS Port:       $MDS_PORT (SSL, password-protected)"
echo "MDS Password:   [SET - validated]"
echo ""

exec java -Xmx1G -jar "$JAR_PATH" \
    -data "$DATA_DIR" \
    -basefolder "$DATA_DIR" \
    -rpcenable \
    -rpc $RPC_PORT \
    -port $P2P_PORT \
    -mdsenable \
    -mdspassword "$MDS_PASSWORD" \
    -p2pnodes megammr.minima.global:9001
