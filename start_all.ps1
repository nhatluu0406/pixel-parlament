# start_all.ps1
# This script stops existing processes and starts the Backend and Frontend.

.\stop_all.ps1

Write-Host "`nStarting PixelParlament Backend (Port 8080)..." -ForegroundColor Green
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", "cd backend; uv run uvicorn app.main:app --reload --port 8080"

Write-Host "Starting PixelParlament Frontend (Port 3000)..." -ForegroundColor Cyan
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "`nWaiting for servers to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

$backendReady = Test-NetConnection -ComputerName localhost -Port 8080 -InformationLevel Quiet
$frontendReady = Test-NetConnection -ComputerName localhost -Port 3000 -InformationLevel Quiet

if ($backendReady) {
    Write-Host "[OK] Backend is UP at http://localhost:8080" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Backend failed to start on port 8080." -ForegroundColor Red
}

if ($frontendReady) {
    Write-Host "[OK] Frontend is UP at http://localhost:3000" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Frontend failed to start on port 3000." -ForegroundColor Red
}

if ($backendReady -and $frontendReady) {
    Write-Host "`nPixelParlament is ready!" -ForegroundColor Yellow
    Write-Host "Main Office: http://localhost:3000"
    Write-Host "Admin Dash:  http://localhost:3000/admin"
} else {
    Write-Host "`nSome services failed to start. Please check the two new terminal windows for error messages." -ForegroundColor Red
}
