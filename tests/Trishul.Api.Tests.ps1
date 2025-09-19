Describe "Trishul API" {

  BeforeAll {
    . "$PSScriptRoot\_helpers.ps1"
  }

  It "/health returns ok:true" {
    $res = Invoke-TrishulTest -Path '/health' -NoAuth
    $res.ok | Should -BeTrue
  }

  It "rudra mock-usage returns usage array" {
    $res = Invoke-TrishulTest -Path '/rudra/cloud/mock-usage' -Method POST -BodyJson '{}'
    $res.usage.Count | Should -BeGreaterThan 0
  }

  It "forecast returns total > 0" {
    $res = Invoke-TrishulTest -Path '/rudra/cloud/forecast'
    $res.total | Should -BeGreaterThan 0
  }
}
