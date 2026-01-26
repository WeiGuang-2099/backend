# Backend Startup Script

Write-Host "`nFastAPI Backend + MySQL" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

# Check Docker
Write-Host "`n[CHECK] Docker..." -ForegroundColor Yellow
$dockerRunning = docker ps 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}
Write-Host "[OK] Docker is running" -ForegroundColor Green

# Start MySQL
Write-Host "`n[START] MySQL container..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "[WAIT] Starting MySQL (15 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check Python dependencies
Write-Host "`n[CHECK] Python dependencies..." -ForegroundColor Yellow
$pipList = pip freeze
if ($pipList -notmatch "fastapi") {
    Write-Host "[INSTALL] Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}
Write-Host "[OK] Python dependencies installed" -ForegroundColor Green

# Initialize sample users
Write-Host "`n[INIT] Sample users..." -ForegroundColor Yellow
python init_sample_users.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[OK] Database initialized successfully" -ForegroundColor Green
} else {
    Write-Host "`n[WARN] Database may already be initialized, continuing..." -ForegroundColor Yellow
}

Write-Host "`n"
Write-Host "="*60 -ForegroundColor Cyan
Write-Host "Starting Backend Service" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

Write-Host "`nService Information:" -ForegroundColor Yellow
Write-Host "   MySQL:    localhost:3306" -ForegroundColor White
Write-Host "   API:      http://localhost:8000" -ForegroundColor White
Write-Host "   Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "   ReDoc:    http://localhost:8000/redoc" -ForegroundColor White

Write-Host "`nTest Accounts:" -ForegroundColor Yellow
Write-Host "   Username: john   Password: password123" -ForegroundColor Cyan
Write-Host "   Username: jane   Password: password456" -ForegroundColor Cyan
Write-Host "   Username: alice  Password: password789" -ForegroundColor Cyan

Write-Host "`n[START] Starting FastAPI..." -ForegroundColor Yellow
Write-Host ""

# Start FastAPI
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
