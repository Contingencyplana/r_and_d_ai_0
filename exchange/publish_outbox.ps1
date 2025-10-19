# Publish reports and acknowledgements to High Command
$config = Get-Content -Path ".\exchange\config.json" | ConvertFrom-Json

$localPath = $config.workspace.local
$remotePath = $config.workspace.remote

# Push reports
$reportsPath = Join-Path $localPath $config.paths.reports.inbox
$remoteReportsPath = Join-Path $remotePath $config.paths.reports.inbox

if (Test-Path $reportsPath) {
    Get-ChildItem $reportsPath -Filter *.json | ForEach-Object {
        $targetPath = Join-Path $remoteReportsPath $_.Name
        if (-not (Test-Path $targetPath)) {
            Copy-Item $_.FullName -Destination $targetPath
            Write-Host "Published report: $($_.Name)"
            
            # Move to archived
            $archivedPath = Join-Path $localPath $config.paths.reports.archived
            Move-Item $_.FullName -Destination (Join-Path $archivedPath $_.Name)
            
            # Update ledger
            $ledgerPath = Join-Path $localPath $config.paths.ledger
            $journalPath = Join-Path $ledgerPath "journal.md"
            $indexPath = Join-Path $ledgerPath "index.json"
            
            # Add journal entry
            $date = Get-Date -Format "yyyy-MM-dd"
            $entry = @"

## [$date] $($_.BaseName)
- Type: REPORT
- Status: DISPATCHED
- Reference: $($_.BaseName -replace '-report$','')
- Details: Report submitted to High Command
"@
            Add-Content $journalPath $entry
            
            # Update index
            $index = Get-Content $indexPath | ConvertFrom-Json
            $index.reports | Add-Member -NotePropertyName $_.BaseName -NotePropertyValue @{
                submitted = $date
                status = "DISPATCHED"
            }
            $index | ConvertTo-Json -Depth 10 | Set-Content $indexPath
        }
    }
}

# Push acknowledgements
$acksPath = Join-Path $localPath $config.paths.acknowledgements.pending
$remoteAcksPath = Join-Path $remotePath $config.paths.acknowledgements.pending

if (Test-Path $acksPath) {
    Get-ChildItem $acksPath -Filter *.json | ForEach-Object {
        $targetPath = Join-Path $remoteAcksPath $_.Name
        if (-not (Test-Path $targetPath)) {
            Copy-Item $_.FullName -Destination $targetPath
            Write-Host "Published acknowledgement: $($_.Name)"
            
            # Move to logged
            $loggedPath = Join-Path $localPath $config.paths.acknowledgements.logged
            Move-Item $_.FullName -Destination (Join-Path $loggedPath $_.Name)
            
            # Update ledger
            $ledgerPath = Join-Path $localPath $config.paths.ledger
            $journalPath = Join-Path $ledgerPath "journal.md"
            $indexPath = Join-Path $ledgerPath "index.json"
            
            # Add journal entry
            $date = Get-Date -Format "yyyy-MM-dd"
            $entry = @"

## [$date] $($_.BaseName)
- Type: ACKNOWLEDGEMENT
- Status: DISPATCHED
- Reference: $($_.BaseName -replace '-ack$','')
- Details: Acknowledgement sent to High Command
"@
            Add-Content $journalPath $entry
            
            # Update index
            $index = Get-Content $indexPath | ConvertFrom-Json
            $index.acknowledgements | Add-Member -NotePropertyName $_.BaseName -NotePropertyValue @{
                sent = $date
                status = "DISPATCHED"
            }
            $index | ConvertTo-Json -Depth 10 | Set-Content $indexPath
        }
    }
}