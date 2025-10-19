# Pull new orders from High Command inbox
$config = Get-Content -Path ".\exchange\config.json" | ConvertFrom-Json

$localPath = $config.workspace.local
$remotePath = $config.workspace.remote

# Pull pending orders
$pendingPath = Join-Path $remotePath $config.paths.orders.pending
$localPendingPath = Join-Path $localPath $config.paths.orders.pending

if (Test-Path $pendingPath) {
    Get-ChildItem $pendingPath -Filter *.json | ForEach-Object {
        $targetPath = Join-Path $localPendingPath $_.Name
        if (-not (Test-Path $targetPath)) {
            Copy-Item $_.FullName -Destination $targetPath
            Write-Host "Pulled order: $($_.Name)"
            
            # Update ledger
            $ledgerPath = Join-Path $localPath $config.paths.ledger
            $journalPath = Join-Path $ledgerPath "journal.md"
            $indexPath = Join-Path $ledgerPath "index.json"
            
            # Add journal entry
            $date = Get-Date -Format "yyyy-MM-dd"
            $entry = @"

## [$date] $($_.BaseName)
- Type: ORDER
- Status: RECEIVED
- Reference: N/A
- Details: New order received
"@
            Add-Content $journalPath $entry
            
            # Update index
            $index = Get-Content $indexPath | ConvertFrom-Json
            $index.orders | Add-Member -NotePropertyName $_.BaseName -NotePropertyValue @{
                received = $date
                status = "RECEIVED"
            }
            $index | ConvertTo-Json -Depth 10 | Set-Content $indexPath
        }
    }
}