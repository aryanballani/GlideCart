#!/bin/bash

# Manual deployment steps for Grocery Buddy
# Run each command one at a time and enter password when prompted

echo "=========================================="
echo "Manual Deployment to Raspberry Pi"
echo "Password: raspberrypi"
echo "=========================================="
echo ""

echo "Step 1: Creating directory on Pi..."
echo "Run: ssh ishman@10.19.129.238 'mkdir -p /home/ishman/grocery-buddy'"
ssh ishman@10.19.129.238 'mkdir -p /home/ishman/grocery-buddy'

echo ""
echo "Step 2: Copying files to Pi..."
echo "This will ask for password again..."
rsync -avz --progress raspberry-pi/ ishman@10.19.129.238:/home/ishman/grocery-buddy/

echo ""
echo "Step 3: Installing dependencies..."
ssh ishman@10.19.129.238 'cd /home/ishman/grocery-buddy && pip3 install --user websockets opencv-python numpy'

echo ""
echo "Step 4: Making script executable..."
ssh ishman@10.19.129.238 'chmod +x /home/ishman/grocery-buddy/main_server.py'

echo ""
echo "✅ Deployment complete!"
echo ""
echo "To start the server, run:"
echo "ssh ishman@10.19.129.238 'cd /home/ishman/grocery-buddy && python3 main_server.py'"
