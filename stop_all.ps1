# stop_all.ps1
Write-Host "Cleaning up existing processes on ports 8080 and 3000..." -ForegroundColor Yellow

$ports = @(8000, 8080, 3000)
foreach ($port in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($conns) {
        foreach ($c in $conns) {
            Write-Host "Killing process $($c.OwningProcess) on port $port..." -ForegroundColor Red
            taskkill /F /PID $c.OwningProcess /T 2>$null
        }
    }
}

# Also kill by process name for Next.js and Uvicorn
taskkill /F /IM uvicorn.exe /T 2>$null
taskkill /F /IM node.exe /T 2>$null

Write-Host "Cleanup complete." -ForegroundColor Green
