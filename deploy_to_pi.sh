#!/bin/bash

# Deployment script for Grocery Buddy to Raspberry Pi
# Usage: ./deploy_to_pi.sh

PI_USER="ishman"
PI_HOST="10.19.129.238"
PI_DIR="/home/ishman/grocery-buddy"

echo "======================================"
echo "Grocery Buddy - Raspberry Pi Deployment"
echo "======================================"
echo ""

# Check if sshpass is available
if ! command -v sshpass &> /dev/null; then
    echo "⚠️  Warning: sshpass not found. You'll need to enter password manually."
    USE_SSHPASS=false
else
    USE_SSHPASS=true
    PI_PASSWORD="raspberrypi"
fi

echo "📦 Creating deployment package..."

# Create a temporary directory for deployment
TEMP_DIR=$(mktemp -d)
cp -r raspberry-pi/* "$TEMP_DIR/"

echo "✅ Package created"
echo ""

echo "🚀 Deploying to Raspberry Pi ($PI_HOST)..."
echo "   This will:"
echo "   1. Create directory $PI_DIR on the Pi"
echo "   2. Copy all files"
echo "   3. Install dependencies"
echo ""

# Function to run SSH commands
run_ssh() {
    if [ "$USE_SSHPASS" = true ]; then
        sshpass -p "$PI_PASSWORD" ssh -o StrictHostKeyChecking=no "$PI_USER@$PI_HOST" "$1"
    else
        ssh "$PI_USER@$PI_HOST" "$1"
    fi
}

# Function to copy files
copy_files() {
    if [ "$USE_SSHPASS" = true ]; then
        sshpass -p "$PI_PASSWORD" rsync -avz --delete -e "ssh -o StrictHostKeyChecking=no" "$TEMP_DIR/" "$PI_USER@$PI_HOST:$PI_DIR/"
    else
        rsync -avz --delete "$TEMP_DIR/" "$PI_USER@$PI_HOST:$PI_DIR/"
    fi
}

# Create directory on Pi
echo "📁 Creating directory on Pi..."
run_ssh "mkdir -p $PI_DIR"

# Copy files
echo "📤 Copying files..."
copy_files

if [ $? -eq 0 ]; then
    echo "✅ Files copied successfully"
else
    echo "❌ Failed to copy files"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies on Pi..."
run_ssh "cd $PI_DIR && pip3 install --user websockets opencv-python numpy" || echo "⚠️  Some dependencies may have failed to install"

# Make main_server.py executable
run_ssh "chmod +x $PI_DIR/main_server.py"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "===================================="
echo "🤖 To start the robot server:"
echo "===================================="
echo ""
echo "Method 1 - Interactive (with SSH):"
echo "  ssh $PI_USER@$PI_HOST"
echo "  cd $PI_DIR"
echo "  python3 main_server.py"
echo ""
echo "Method 2 - Direct command:"
if [ "$USE_SSHPASS" = true ]; then
    echo "  sshpass -p '$PI_PASSWORD' ssh $PI_USER@$PI_HOST 'cd $PI_DIR && python3 main_server.py'"
else
    echo "  ssh $PI_USER@$PI_HOST 'cd $PI_DIR && python3 main_server.py'"
fi
echo ""
echo "Method 3 - Run in background:"
if [ "$USE_SSHPASS" = true ]; then
    echo "  sshpass -p '$PI_PASSWORD' ssh $PI_USER@$PI_HOST 'cd $PI_DIR && nohup python3 main_server.py > robot.log 2>&1 &'"
else
    echo "  ssh $PI_USER@$PI_HOST 'cd $PI_DIR && nohup python3 main_server.py > robot.log 2>&1 &'"
fi
echo ""
echo "📱 Then connect your Android app to: $PI_HOST:8765"
echo ""

# Cleanup
rm -rf "$TEMP_DIR"
