# Backend Stop Script

Write-Host "`nStopping Backend Service" -ForegroundColor Yellow
Write-Host "="*60 -ForegroundColor Yellow

# Stop MySQL container
Write-Host "`n[STOP] MySQL container..." -ForegroundColor Yellow
docker-compose down

Write-Host "`n[DONE] Service stopped" -ForegroundColor Green
Write-Host ""
