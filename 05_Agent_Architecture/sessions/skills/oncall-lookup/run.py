import json, sys
ONCALL = {"atlas": {"team": "Tracking Platform", "channel": "#team-tracking", "pager": "tracking-oncall"}, "ledger": {"team": "Revenue Systems", "channel": "#team-revenue", "pager": "revenue-oncall"}, "warehouse gateway": {"team": "Depot Systems", "channel": "#team-depot", "pager": "depot-oncall"}, "postgres": {"team": "Data Platform", "channel": "#team-data", "pager": "data-oncall-24x7"}}
key = ' '.join(sys.argv[1:]).strip().lower()
hit = next((dict(service=name, **info) for name, info in ONCALL.items() if key in name or name in key), {'error': 'unknown'})
print(json.dumps(hit))
