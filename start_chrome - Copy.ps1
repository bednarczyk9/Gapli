# Skrypt do uruchamiania Chrome w trybie debugowania dla Playwright
Write-Host "Zamykam wszystkie instancje Chrome..." -ForegroundColor Yellow
Stop-Process -Name "chrome" -Force -ErrorAction SilentlyContinue

Write-Host "Uruchamiam Chrome na porcie 9222 z izolowanym profilem..." -ForegroundColor Green
# Używamy profilu w folderze TEMP, aby uniknąć konfliktów z Twoim głównym Chrome
$chromeProfile = "$env:TEMP\chrome-debug"

Start-Process "chrome.exe" -ArgumentList "--remote-debugging-port=9222", "--user-data-dir=$chromeProfile", "--no-first-run", "--no-default-browser-check"

Write-Host "Czekam na aktywację portu..."
Start-Sleep -s 3

$portCheck = netstat -ano | findstr :9222
if ($portCheck) {
    Write-Host "SUKCES: Chrome słucha na porcie 9222." -ForegroundColor Green
    Write-Host "Teraz wejdź na https://gapli.com/login i zaloguj się." -ForegroundColor Cyan
} else {
    Write-Host "BŁĄD: Nie udało się otworzyć portu 9222." -ForegroundColor Red
}
