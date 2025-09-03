# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# MacOS에서 터미널 창 숨김을 위한 추가 설정
import sys
if sys.platform == 'darwin':
    # MacOS 전용 설정
    console = False
    windowed = True
    # MacOS에서 터미널 창 완전 숨김
    argv_emulation = True
    # MacOS .app 번들 생성을 위한 설정
    bundle_identifier = 'com.stockmonitor.app'
    app_name = 'StockMonitor'
    # 앱 아이콘 설정
    app_icon = './app-icon.png'
    # MacOS Ventura 13.7.x+ 호환성을 위한 설정
    target_arch = 'universal2'  # Universal Binary (Intel + Apple Silicon)
    codesign_identity = None  # 개발자 ID가 없을 경우
else:
    # Windows/Linux 설정
    console = False
    windowed = False
    argv_emulation = False

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('env_example.txt', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'schedule',
        'requests',
        'bs4',
        'dotenv',
        'email',
        'smtplib',
        'json',
        'threading',
        'time',
        'datetime',
        'urllib',
        'logging',
        # MacOS Ventura+ 호환성을 위한 추가 모듈
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'certifi',
        'charset_normalizer',
        'idna',
        'urllib3',
        'ssl',
        'socket',
        'platform',
        'sys',
        'os',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='StockMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=console,  # 플랫폼별 설정 적용
    disable_windowed_traceback=False,
    argv_emulation=argv_emulation,  # 플랫폼별 설정 적용
    target_arch=None,  # Universal Binary로 빌드 (Intel + Apple Silicon)
    codesign_identity=codesign_identity if sys.platform == 'darwin' else None,  # MacOS에서만 코드 서명 설정
    entitlements_file=None,
    icon=app_icon if sys.platform == 'darwin' else None,  # MacOS에서만 아이콘 적용
    windowed=windowed,  # 플랫폼별 설정 적용
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='StockMonitor',
)

# MacOS에서 .app 번들 생성
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name=app_name + '.app',
        icon=app_icon,  # 앱 아이콘 설정
        bundle_identifier=bundle_identifier,
        info_plist={
            'CFBundleName': app_name,
            'CFBundleDisplayName': 'Stock Monitor',
            'CFBundleIdentifier': bundle_identifier,
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
            'LSBackgroundOnly': False,
            'LSUIElement': False,
            # MacOS Ventura 13.7.x+ 호환성을 위한 추가 설정
            'LSMinimumSystemVersion': '13.7.0',  # 최소 시스템 요구사항
            'NSAppTransportSecurity': {
                'NSAllowsArbitraryLoads': True,  # HTTP 요청 허용 (재고 확인용)
            },
            'CFBundleSupportedPlatforms': ['MacOSX'],
            'CFBundleInfoDictionaryVersion': '6.0',
            'CFBundlePackageType': 'APPL',
            'CFBundleSignature': '????',
            # Intel + Apple Silicon 호환성
            'CFBundleExecutable': 'StockMonitor',
            'CFBundleName': 'StockMonitor',
            'CFBundleDisplayName': 'Stock Monitor',
        },
    )
