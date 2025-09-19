Describe "Trinetra API" {

  BeforeAll {
    . "$PSScriptRoot\_helpers.ps1"
  }

  It "seeds QC results with 2 docs" {
    $items = @(
      @{
        filename = "pester1.csv"
        size     = 1
        mime     = "text/plain"
        qc       = @{ ok = $true; reason = "dummy-pass" }
      },
      @{
        filename = "pester2.csv"
        size     = 1
        mime     = "text/plain"
        qc       = @{ ok = $true; reason = "dummy-pass" }
      }
    )
    $body = $items | ConvertTo-Json -Depth 5

    $res = Invoke-TrishulTest -Path '/trinetra/qc/seed' -Method POST -BodyJson $body
    $res.inserted | Should -Be 2
  }

  It "results endpoint returns a non-empty array with filename & qc fields" {
    $results = Invoke-TrishulTest -Path '/trinetra/qc/results'
    @($results).Count | Should -BeGreaterThan 0

    # every item should expose 'filename' and 'qc'
    $missing = $results | Where-Object {
      -not ( $_.PSObject.Properties.Name -contains 'filename' -and $_.PSObject.Properties.Name -contains 'qc' )
    }
    $missing | Should -BeNullOrEmpty
  }
}