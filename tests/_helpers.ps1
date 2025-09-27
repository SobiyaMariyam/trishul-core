function Invoke-TrishulTest {
  param(
    [Parameter(Mandatory=$true)][string]$Path,
    [ValidateSet("GET","POST","PUT","PATCH","DELETE")][string]$Method = "GET",
    [string]$BodyJson
  )
  $u = $env:TRISHUL_URL; if (-not $u) { $u = "http://127.0.0.1:8000" }
  $vhost = $env:HOST; if (-not $vhost) { $vhost = "tenant1.lvh.me" }

  $headers = @{ Host = $vhost }
  if ($env:OWNER) { $headers["Authorization"] = "Bearer $env:OWNER" }

  $args = @{
    Uri            = ($u + $Path)
    Method         = $Method
    Headers        = $headers
    UseBasicParsing= $true
  }

  if ($BodyJson -and $Method -in @("POST","PUT","PATCH")) {
    $args["ContentType"] = "application/json"
    $args["Body"] = $BodyJson
  }

  $resp = Invoke-WebRequest @args
  if ($resp.Content) { return ($resp.Content | ConvertFrom-Json) }
}

