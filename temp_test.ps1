try {
  $c = Invoke-RestMethod -Uri 'http://127.0.0.1:5000/search_cities' -Method Post
  Write-Output '---CITIES---'
  $c | ConvertTo-Json -Depth 5
  $m = Invoke-RestMethod -Uri 'http://127.0.0.1:5000/get_min_prices' -Method Post -Body @{startPoint='Paris, France'; destination='Madrid, Spain'}
  Write-Output '---MIN_PRICES---'
  $m | ConvertTo-Json -Depth 5
  $f = Invoke-RestMethod -Uri 'http://127.0.0.1:5000/search_flights' -Method Post -Body @{startPoint='Paris, France'; destination='Madrid, Spain'; startDate='2025-08-24'}
  Write-Output '---FLIGHTS---'
  $f | ConvertTo-Json -Depth 5
  $h = Invoke-RestMethod -Uri 'http://127.0.0.1:5000/search_hotels' -Method Post -Body @{destination='Madrid, Spain'; startDate='2025-08-24'; endDate='2025-08-25'}
  Write-Output '---HOTELS---'
  $h | ConvertTo-Json -Depth 5
} catch {
  Write-Output 'ERROR:'
  Write-Output $_.Exception.ToString()
}
