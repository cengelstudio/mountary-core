#!/bin/bash

# Exit on error
set -e

# Cleanup function
cleanup() {
    echo "Cleaning up..."
    rm -rf build/ dist/ *.spec
    if [ -d "venv" ]; then
        deactivate 2>/dev/null || true
        rm -rf venv
    fi
}

# Trap cleanup on exit
trap cleanup EXIT

echo "Starting build process..."

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

# Build the executable
pyinstaller --onefile --name disk_monitor \
    --add-data "logs:logs" \
    --hidden-import=psutil \
    --hidden-import=colorama \
    --hidden-import=requests \
    --hidden-import=watchdog \
    main.py

# Create distribution directory
mkdir -p dist/logs

# Copy necessary files
cp -r logs/* dist/logs/ 2>/dev/null || true

# Create a simple launcher script
cat > dist/start_monitor.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
./disk_monitor
EOF

# Make launcher executable
chmod +x dist/start_monitor.sh

echo "Build completed successfully!"
echo "You can find the executable in the 'dist' directory."
echo "Run './start_monitor.sh' to start the application."
