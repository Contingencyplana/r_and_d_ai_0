# Safety Status Report Templates

## Hourly Status Report

```yaml
report_type: hourly_status
timestamp: YYYY-MM-DD HH:MM:SS
report_id: HSR-YYYYMMDD-HH

system_status:
  overall_health: [GREEN|YELLOW|RED]
  active_labscapes: <number>
  active_units: <number>
  incident_count: <number>

metrics:
  performance_index: <value>
  resource_utilization: <percentage>
  error_rate: <value>
  safety_compliance: <percentage>

alerts:
  critical: <number>
  warning: <number>
  info: <number>

incidents:
  - id: <incident_id>
    type: <incident_type>
    severity: [LOW|MEDIUM|HIGH|CRITICAL]
    status: [ACTIVE|RESOLVED|INVESTIGATING]
    details: <description>

actions_required:
  - action: <description>
    priority: [LOW|MEDIUM|HIGH|CRITICAL]
    deadline: YYYY-MM-DD HH:MM:SS
```

## Daily Summary Report

```yaml
report_type: daily_summary
date: YYYY-MM-DD
report_id: DSR-YYYYMMDD

system_overview:
  operational_status: [NORMAL|DEGRADED|CRITICAL]
  labscapes_summary:
    total: <number>
    operational: <number>
    degraded: <number>
    offline: <number>
  
  units_summary:
    total: <number>
    active: <number>
    inactive: <number>
    quarantined: <number>

performance_metrics:
  system_stability: <percentage>
  resource_efficiency: <percentage>
  error_rate_24h: <value>
  safety_index: <value>

incidents_summary:
  total_incidents: <number>
  critical_incidents: <number>
  resolved_incidents: <number>
  ongoing_incidents: <number>

safety_compliance:
  protocol_adherence: <percentage>
  audit_findings:
    passed: <number>
    failed: <number>
    pending: <number>
  
maintenance_activities:
  completed:
    - activity: <description>
      timestamp: YYYY-MM-DD HH:MM:SS
      outcome: <description>
  
  scheduled:
    - activity: <description>
      scheduled_time: YYYY-MM-DD HH:MM:SS
      priority: [LOW|MEDIUM|HIGH|CRITICAL]

recommendations:
  - category: <category>
    description: <description>
    priority: [LOW|MEDIUM|HIGH|CRITICAL]
    deadline: YYYY-MM-DD HH:MM:SS
```

## Incident Report Template

```yaml
report_type: incident_report
timestamp: YYYY-MM-DD HH:MM:SS
incident_id: IR-YYYYMMDDHHMMSS

incident_details:
  type: <incident_type>
  severity: [LOW|MEDIUM|HIGH|CRITICAL]
  status: [ACTIVE|RESOLVED|INVESTIGATING]
  location:
    block: <block_id>
    labscape: <labscape_id>
    unit: <unit_id>

timeline:
  detection:
    timestamp: YYYY-MM-DD HH:MM:SS
    method: <detection_method>
    
  response:
    timestamp: YYYY-MM-DD HH:MM:SS
    actions_taken:
      - action: <description>
        outcome: <description>
        
  resolution:
    timestamp: YYYY-MM-DD HH:MM:SS
    final_status: <description>

impact_assessment:
  affected_systems:
    - system: <system_name>
      impact_level: [LOW|MEDIUM|HIGH|CRITICAL]
      status: <description>
      
  containment_status:
    method: <containment_method>
    effectiveness: <percentage>
    
  damage_assessment:
    scope: <description>
    severity: [LOW|MEDIUM|HIGH|CRITICAL]
    recovery_status: <description>

root_cause_analysis:
  primary_cause: <description>
  contributing_factors:
    - factor: <description>
      weight: [LOW|MEDIUM|HIGH]

corrective_actions:
  immediate:
    - action: <description>
      status: [PLANNED|IN_PROGRESS|COMPLETED]
      deadline: YYYY-MM-DD HH:MM:SS
      
  long_term:
    - action: <description>
      status: [PLANNED|IN_PROGRESS|COMPLETED]
      deadline: YYYY-MM-DD HH:MM:SS

lessons_learned:
  findings:
    - finding: <description>
      recommendation: <description>
      priority: [LOW|MEDIUM|HIGH|CRITICAL]
      
  preventive_measures:
    - measure: <description>
      implementation_status: [PLANNED|IN_PROGRESS|COMPLETED]
      deadline: YYYY-MM-DD HH:MM:SS
```

## Audit Report Template

```yaml
report_type: audit_report
date: YYYY-MM-DD
audit_id: AR-YYYYMMDD

audit_scope:
  systems_reviewed:
    - system: <system_name>
      components: [<component_list>]
      depth: [FULL|PARTIAL]
      
  timeframe:
    start_date: YYYY-MM-DD
    end_date: YYYY-MM-DD

compliance_summary:
  overall_status: [COMPLIANT|PARTIAL|NON_COMPLIANT]
  compliance_rate: <percentage>
  critical_findings: <number>
  major_findings: <number>
  minor_findings: <number>

findings:
  critical:
    - finding_id: <id>
      description: <description>
      impact: <description>
      recommendation: <description>
      deadline: YYYY-MM-DD
      
  major:
    - finding_id: <id>
      description: <description>
      impact: <description>
      recommendation: <description>
      deadline: YYYY-MM-DD
      
  minor:
    - finding_id: <id>
      description: <description>
      impact: <description>
      recommendation: <description>
      deadline: YYYY-MM-DD

corrective_actions:
  required_actions:
    - action_id: <id>
      finding_id: <id>
      description: <description>
      priority: [HIGH|MEDIUM|LOW]
      deadline: YYYY-MM-DD
      status: [PLANNED|IN_PROGRESS|COMPLETED]
      
  follow_up:
    next_audit_date: YYYY-MM-DD
    focus_areas: [<area_list>]
    special_requirements: <description>

certification:
  auditor: <name>
  position: <title>
  signature: <signature>
  date: YYYY-MM-DD
```