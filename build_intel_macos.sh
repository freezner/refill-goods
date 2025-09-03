#!/bin/bash

echo "🖥️  Intel Mac용 StockMonitor 빌드 스크립트"
echo "=========================================="
echo ""
echo "⚠️  주의사항:"
echo "이 스크립트는 Intel Mac에서 실행해야 합니다."
echo "Apple Silicon Mac에서는 실행하지 마세요."
echo ""

# Intel Mac 확인
if [[ $(uname -m) == "x86_64" ]]; then
    echo "✅ Intel Mac이 확인되었습니다."
else
    echo "❌ 이 스크립트는 Intel Mac에서만 실행할 수 있습니다."
    echo "현재 시스템: $(uname -m)"
    exit 1
fi

# 가상환경 활성화
if [ -d "venv" ]; then
    echo "가상환경을 활성화합니다..."
    source venv/bin/activate
else
    echo "❌ 가상환경을 찾을 수 없습니다. 먼저 가상환경을 생성해주세요."
    exit 1
fi

# PyInstaller 설치 확인
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "❌ PyInstaller가 설치되지 않았습니다. 설치합니다..."
    pip install pyinstaller
fi

# 기존 빌드 파일 정리
echo "🧹 기존 빌드 파일을 정리합니다..."
rm -rf build dist

# Intel Mac용 .app 번들 생성
echo "🔨 Intel Mac용 .app 번들을 생성합니다..."
pyinstaller --onedir --windowed --icon=./app-icon.png --name=StockMonitor main.py

# .app 번들 생성
echo "📱 .app 번들을 생성합니다..."
mkdir -p "dist/StockMonitor.app/Contents/MacOS"
mkdir -p "dist/StockMonitor.app/Contents/Resources"
mkdir -p "dist/StockMonitor.app/Contents/Info.plist"

# 실행 파일 복사
cp "dist/StockMonitor/StockMonitor" "dist/StockMonitor.app/Contents/MacOS/"
cp -r "dist/StockMonitor/"* "dist/StockMonitor.app/Contents/Resources/"

# Info.plist 생성
cat > "dist/StockMonitor.app/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>StockMonitor</string>
    <key>CFBundleIdentifier</key>
    <string>com.stockmonitor.app</string>
    <key>CFBundleName</key>
    <string>StockMonitor</string>
    <key>CFBundleDisplayName</key>
    <string>Stock Monitor</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>13.7.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSUIElement</key>
    <false/>
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
    </dict>
</dict>
</plist>
EOF

# 결과 확인
if [ -d "dist/StockMonitor.app" ]; then
    echo "✅ Intel Mac용 .app 번들 생성 완료!"
    echo "📁 생성된 파일: dist/StockMonitor.app"
    echo "📱 Finder에서 더블클릭하여 실행할 수 있습니다."
    
    # 파일 크기 표시
    app_size=$(du -sh "dist/StockMonitor.app" | cut -f1)
    echo "📊 .app 번들 크기: $app_size"
    
    # 아키텍처 확인
    echo "🖥️  아키텍처 정보:"
    file "dist/StockMonitor.app/Contents/MacOS/StockMonitor"
    
else
    echo "❌ .app 번들 생성에 실패했습니다."
    exit 1
fi

echo ""
echo "🎉 Intel Mac용 StockMonitor .app 번들 생성이 완료되었습니다!"
echo "📂 dist/ 폴더에서 StockMonitor.app을 확인할 수 있습니다."
echo ""
echo "💡 사용법:"
echo "1. Finder에서 StockMonitor.app 더블클릭"
echo "2. Applications 폴더에 드래그하여 설치"
echo "3. Dock에 아이콘 추가 가능"
