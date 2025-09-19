# tests\_helpers.ps1
$Base = "http://127.0.0.1:8000"
$HostHeader = "tenant1.lvh.me"

# Mint short-lived OWNER from .env SECRET_KEY using python -c
$S = ((Get-Content .env -Raw) -split "`n" | ? {$_ -match '^SECRET_KEY='} | % { ($_ -split '=',2)[1].Trim() })
$script:OWNER = (python -c "import time,jwt; s='$S'; n=int(time.time()); print(jwt.encode({'sub':'emp@tenant1.com','tid':'tenant1','role':'owner','iat':n,'exp':n+600,'aud':'tenant1'}, s, algorithm='HS256'))").Trim()

function Invoke-TrishulTest {
  param(
    [Parameter(Mandatory)][string]$Path,
    [ValidateSet('GET','POST')][string]$Method='GET',
    [string]$BodyJson = $null,
    [switch]$NoAuth
  )
  $uri = "$Base$Path"
  $headers = @{ Host = $HostHeader }
  if (-not $NoAuth) { $headers.Authorization = "Bearer $script:OWNER" }
  if ($Method -eq 'POST' -and $BodyJson -eq $null) { $BodyJson = '{}' }

  $resp = Invoke-WebRequest -Uri $uri -Method $Method -Headers $headers -ContentType 'application/json' -Body $BodyJson
  if (-not $resp.Content) { throw "Empty response from $Path (HTTP $($resp.StatusCode))" }
  return ($resp.Content | ConvertFrom-Json)
}
