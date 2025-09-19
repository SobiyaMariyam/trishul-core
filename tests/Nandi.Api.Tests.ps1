Describe "Nandi API" {

  BeforeAll {
    . "$PSScriptRoot\_helpers.ps1"
    $script:testTo = $env:TEST_TO
    if ([string]::IsNullOrWhiteSpace($script:testTo)) {
      $script:testTo = "trishul.ai825@gmail.com"
    }
  }

  It "queues (and possibly sends) an email" {
    $payload = @{
      to      = $script:testTo
      subject = "Nandi test ✔"
      body    = "Sent from Pester."
    } | ConvertTo-Json -Compress

    $res = Invoke-TrishulTest -Path '/nandi/email/send' -Method POST -BodyJson $payload
    $res.ok | Should -BeTrue
    # Either queued true OR sent true is acceptable
    (($res.queued -eq $true) -or ($res.sent -eq $true)) | Should -BeTrue
  }

  It "outbox returns an array of messages" {
    $res = Invoke-TrishulTest -Path '/nandi/email/outbox'
    ($res.results | Measure-Object).Count | Should -BeGreaterThan 0
  }

  It "most recent outbox item has expected fields" {
    $res = Invoke-TrishulTest -Path '/nandi/email/outbox'
    $last = $res.results[-1]
    $last.to      | Should -Not -BeNullOrEmpty
    $last.subject | Should -Not -BeNullOrEmpty
    $last.ts      | Should -Not -BeNullOrEmpty
  }
}
