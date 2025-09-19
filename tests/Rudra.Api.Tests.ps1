Describe "Rudra API" {

  BeforeAll {
    . "$PSScriptRoot\_helpers.ps1"
  }

  It "/rudra/cloud/forecast/save returns ok + avg >= 0" {
    $res = Invoke-TrishulTest -Path '/rudra/cloud/forecast/save' -Method POST -BodyJson '{}'
    $res.ok  | Should -BeTrue
    $res.avg | Should -BeGreaterOrEqual 0
  }

  It "recent events include a forecast entry" {
    $events = Invoke-TrishulTest -Path '/nandi/events'
    ($events.results | Where-Object { $_.type -eq 'forecast' }).Count | Should -BeGreaterThan 0
  }
}
