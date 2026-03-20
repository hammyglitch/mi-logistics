#!/bin/bash
echo ""
echo "============================================"
echo "  MI LOGISTICS - Brand Review App"
echo "============================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found."
    echo "Install it from: https://www.python.org/downloads/"
    exit 1
fi

# Install Flask if needed
python3 -c "import flask" 2>/dev/null || {
    echo "Installing Flask..."
    pip3 install flask --quiet
}

echo "Flask ready."
echo ""
echo "Opening: http://localhost:5000"
echo "Press Ctrl+C to stop the app."
echo ""

# Open browser (works on Mac & most Linux)
sleep 2 && (open http://localhost:5000 2>/dev/null || xdg-open http://localhost:5000 2>/dev/null) &

python3 app.py
