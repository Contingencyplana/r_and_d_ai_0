# Publish reports and acknowledgements to High Command
$ErrorActionPreference = 'Stop'

function Resolve-UpstreamRoot {
    param(
        [string]$RootValue
    )

    if ($RootValue -match '^\$\{(?<var>.+)\}$') {
        $resolved = [Environment]::GetEnvironmentVariable($Matches.var)
        if (-not $resolved) {
            throw "Environment variable '$($Matches.var)' for upstream_root is not set."
        }
        return $resolved
    }

    return $RootValue
}

$repoRoot = (Get-Location).Path
$configPath = Join-Path $repoRoot 'exchange\config.json'

if (-not (Test-Path $configPath)) {
    throw "Configuration file not found at $configPath"
}

$config = Get-Content -Path $configPath | ConvertFrom-Json
$upstreamRoot = Resolve-UpstreamRoot -RootValue $config.upstream_root

$logRoot = Join-Path $repoRoot 'exchange\logs'
if (-not (Test-Path $logRoot)) {
    New-Item -Path $logRoot -ItemType Directory | Out-Null
}
$logPath = Join-Path $logRoot 'publish_outbox.log'

function Write-Log {
    param(
        [string]$Message
    )

    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "$timestamp - $Message" | Tee-Object -FilePath $logPath -Append | Out-Null
}

Write-Log 'Starting publish_outbox sweep'

$localReports = Join-Path $repoRoot $config.mapping.local.reports_inbox
$archivedReports = Join-Path $repoRoot $config.mapping.local.reports_archived
$upstreamReports = Join-Path $upstreamRoot $config.mapping.upstream.reports_inbox

$localAcks = Join-Path $repoRoot $config.mapping.local.acks_pending
$loggedAcks = Join-Path $repoRoot $config.mapping.local.acks_logged
$upstreamAcks = Join-Path $upstreamRoot $config.mapping.upstream.acks_pending

$ledgerRoot = Join-Path $repoRoot 'exchange\ledger'
$journalPath = Join-Path $ledgerRoot 'journal.md'
$indexPath = Join-Path $ledgerRoot 'index.json'

foreach ($path in @($archivedReports, $loggedAcks)) {
    if (-not (Test-Path $path)) {
        New-Item -Path $path -ItemType Directory | Out-Null
    }
}

if (Test-Path $localReports) {
    Get-ChildItem $localReports -Filter *.json | ForEach-Object {
        $reportName = $_.Name
        $reportId = $_.BaseName
        $targetPath = Join-Path $upstreamReports $reportName

        if (Test-Path $targetPath) {
            return
        }

        Write-Log "Publishing report $reportId"
        Copy-Item $_.FullName -Destination $targetPath
        Move-Item $_.FullName -Destination (Join-Path $archivedReports $reportName)

        $timestamp = Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ'
        $journalEntry = "- $timestamp - Dispatched report $reportId to upstream"
        Add-Content -Path $journalPath -Value $journalEntry

        if (Test-Path $indexPath) {
            $index = Get-Content $indexPath | ConvertFrom-Json -AsHashtable

            if (-not $index.ContainsKey('reports')) {
                $index['reports'] = @{}
            }

            $index['reports'][$reportId] = "reports/archived/$reportName"
            $index['last_updated'] = $timestamp
            $index | ConvertTo-Json -Depth 6 | Set-Content $indexPath
        }
    }
}

if (Test-Path $localAcks) {
    Get-ChildItem $localAcks -Filter *.json | ForEach-Object {
        $ackName = $_.Name
        $ackId = $_.BaseName
        $targetPath = Join-Path $upstreamAcks $ackName

        if (Test-Path $targetPath) {
            return
        }

        Write-Log "Publishing acknowledgement $ackId"
        Copy-Item $_.FullName -Destination $targetPath
        Move-Item $_.FullName -Destination (Join-Path $loggedAcks $ackName)

        $timestamp = Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ'
        $journalEntry = "- $timestamp - Dispatched acknowledgement $ackId to upstream"
        Add-Content -Path $journalPath -Value $journalEntry

        if (Test-Path $indexPath) {
            $index = Get-Content $indexPath | ConvertFrom-Json -AsHashtable

            if (-not $index.ContainsKey('acks')) {
                $index['acks'] = @{}
            }

            $index['acks'][$ackId] = "acknowledgements/logged/$ackName"
            $index['last_updated'] = $timestamp
            $index | ConvertTo-Json -Depth 6 | Set-Content $indexPath
        }
    }
}

Write-Log 'Publish_outbox sweep complete'