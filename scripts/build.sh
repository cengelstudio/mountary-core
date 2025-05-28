
set -e

cleanup() {
    echo "Cleaning up..."
    rm -rf build/ dist/ *.spec
    if [ -d "venv" ]; then
        deactivate 2>/dev/null || true
        rm -rf venv
    fi
}

trap cleanup EXIT

echo "Starting build process..."

python3 -m venv venv

source venv/bin/activate

pip install --upgrade pip

pip install -r requirements.txt

pip install -e .

pyinstaller --onefile --name disk_monitor \
    --add-data "logs:logs" \
    --hidden-import=psutil \
    --hidden-import=colorama \
    --hidden-import=requests \
    --hidden-import=watchdog \
    main.py

mkdir -p dist/logs

cp -r logs/* dist/logs/ 2>/dev/null || true

cat > dist/start_monitor.sh << 'EOF'
cd "$(dirname "$0")"
./disk_monitor
EOF

chmod +x dist/start_monitor.sh

echo "Build completed successfully!"
echo "You can find the executable in the 'dist' directory."
echo "Run './start_monitor.sh' to start the application."
