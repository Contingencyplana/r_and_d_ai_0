# Pull new orders from High Command inbox
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
$logPath = Join-Path $logRoot 'pull_inbox.log'

function Write-Log {
    param(
        [string]$Message
    )

    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "$timestamp - $Message" | Tee-Object -FilePath $logPath -Append | Out-Null
}

Write-Log 'Starting pull_inbox sweep'

$localOrdersPending = Join-Path $repoRoot $config.mapping.local.orders_pending
$upstreamOrdersPending = Join-Path $upstreamRoot $config.mapping.upstream.orders_pending

if (-not (Test-Path $localOrdersPending)) {
    Write-Log "Local pending directory missing. Creating $localOrdersPending"
    New-Item -Path $localOrdersPending -ItemType Directory | Out-Null
}

if (-not (Test-Path $upstreamOrdersPending)) {
    Write-Log "Upstream pending directory not found: $upstreamOrdersPending"
    return
}

$ledgerRoot = Join-Path $repoRoot 'exchange\ledger'
$journalPath = Join-Path $ledgerRoot 'journal.md'
$indexPath = Join-Path $ledgerRoot 'index.json'

Get-ChildItem $upstreamOrdersPending -Filter *.json | ForEach-Object {
    $orderName = $_.Name
    $orderId = $_.BaseName
    $targetPath = Join-Path $localOrdersPending $orderName

    if (Test-Path $targetPath) {
        return
    }

    Write-Log "Pulling order $orderId"
    Copy-Item $_.FullName -Destination $targetPath

    $timestamp = Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ'
    $journalEntry = "- $timestamp - Pulled $orderId into exchange/orders/pending/"
    Add-Content -Path $journalPath -Value $journalEntry

    if (Test-Path $indexPath) {
        $index = Get-Content $indexPath | ConvertFrom-Json -AsHashtable

        if (-not $index.ContainsKey('orders')) {
            $index['orders'] = @{}
        }

        $index['orders'][$orderId] = @{
            status = 'pending'
            order_path = "orders/pending/$orderName"
            ack_path = $null
            report_path = $null
            received = $timestamp
        }

        $index['last_updated'] = $timestamp

        $index | ConvertTo-Json -Depth 6 | Set-Content $indexPath
    }
}

Write-Log 'Pull_inbox sweep complete'