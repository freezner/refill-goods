#!/bin/bash

echo "🍎 MacOS .app 번들 생성 스크립트"
echo "=================================="

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

# .app 번들 생성
echo "🔨 .app 번들을 생성합니다..."
pyinstaller build_config.spec

# 결과 확인
if [ -d "dist/StockMonitor.app" ]; then
    echo "✅ .app 번들 생성 완료!"
    echo "📁 생성된 파일: dist/StockMonitor.app"
    echo "📱 Finder에서 더블클릭하여 실행할 수 있습니다."
    
    # 파일 크기 표시
    app_size=$(du -sh "dist/StockMonitor.app" | cut -f1)
    echo "📊 .app 번들 크기: $app_size"
    
    # .app 번들 정보 표시
    echo "ℹ️  .app 번들 정보:"
    plutil -p "dist/StockMonitor.app/Contents/Info.plist" | grep -E "(CFBundleName|CFBundleVersion|CFBundleIdentifier)"
    
else
    echo "❌ .app 번들 생성에 실패했습니다."
    exit 1
fi

echo ""
echo "🎉 MacOS .app 번들 생성이 완료되었습니다!"
echo "📂 dist/ 폴더에서 StockMonitor.app을 확인할 수 있습니다."
