Describe "Nandi API" {

  BeforeAll { . "$PSScriptRoot\_helpers.ps1" }

  It "queues (and possibly sends) an email" {
    $payload = '{ "to":"qa@example.com", "subject":"Pester test", "body":"Sent from Pester." }'
    $res = Invoke-TrishulTest -Path '/nandi/email/send' -Method POST -BodyJson $payload
    $res | Should -Not -BeNullOrEmpty
  }

  It "most recent outbox item has expected fields" {
    $items = Invoke-TrishulTest -Path '/nandi/email/outbox?limit=5'
    # Handle both shapes: bare array OR {results:[...]}
    if ($items -is [System.Array]) {
      $latest = $items | Select-Object -First 1
    } elseif ($items.PSObject.Properties.Name -contains 'results') {
      $latest = $items.results | Select-Object -First 1
    } else {
      $latest = $items
    }
    $latest | Should -Not -BeNullOrEmpty
    $latest.to | Should -Not -BeNullOrEmpty
    $latest.subject | Should -Not -BeNullOrEmpty
  }
}
