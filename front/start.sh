#!/bin/bash

echo "🚀 WALKerHOLIC 개발 서버를 시작합니다..."
echo ""
echo "📱 모바일 접속 정보:"
echo "-------------------"

# Windows에서 IP 주소 가져오기 (여러 방법 시도)
# 방법 1: ipconfig를 통한 방법
IP=$(ipconfig | grep -A 8 'Wi-Fi' | grep 'IPv4' | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' | head -1)

# 방법 1이 실패하면 방법 2 시도
if [ -z "$IP" ]; then
    IP=$(ipconfig | grep -A 8 'Ethernet' | grep 'IPv4' | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' | head -1)
fi

# 방법 2도 실패하면 방법 3 시도 (PowerShell 사용)
if [ -z "$IP" ]; then
    IP=$(powershell -Command "(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias Wi-Fi).IPAddress" 2>/dev/null)
fi

# 그래도 실패하면 방법 4 시도
if [ -z "$IP" ]; then
    IP=$(powershell -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike '*Loopback*' -and $_.IPAddress -notlike '169.254.*'}).IPAddress | Select-Object -First 1" 2>/dev/null)
fi

# IP를 찾지 못한 경우 수동 확인 안내
if [ -z "$IP" ]; then
    echo "⚠️  IP 주소를 자동으로 찾을 수 없습니다."
    echo ""
    echo "수동으로 확인하는 방법:"
    echo "1. 새 명령 프롬프트(cmd) 창을 열어주세요"
    echo "2. ipconfig 명령어를 입력하세요"
    echo "3. Wi-Fi 또는 이더넷 어댑터의 IPv4 주소를 확인하세요"
    echo "   (보통 192.168.x.x 형태입니다)"
    echo ""
    echo "로컬: http://localhost:5173"
    echo "네트워크: http://[여기에 IP 주소 입력]:5173"
else
    echo "로컬: http://localhost:5173"
    echo "네트워크: http://$IP:5173"
    echo ""
    echo "📌 같은 Wi-Fi에 연결된 모바일 기기에서 위 네트워크 주소로 접속하세요!"
fi

echo "-------------------"
echo ""
echo "💡 팁: 모바일 접속이 안 되는 경우"
echo "   1. PC와 모바일이 같은 Wi-Fi에 연결되어 있는지 확인"
echo "   2. Windows 방화벽에서 Node.js 허용 확인"
echo "   3. 백신 프로그램의 방화벽 설정 확인"
echo "-------------------"
echo ""

# 개발 서버 실행
npm run dev