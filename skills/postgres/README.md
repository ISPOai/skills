# postgres

Read-only PostgreSQL query skill. Query multiple databases safely with write protection.

## Setup

1. Create an external config directory and file (never inside the skill):
```bash
mkdir -p "${XDG_CONFIG_HOME:-$HOME/.config}/ispo"
chmod 700 "${XDG_CONFIG_HOME:-$HOME/.config}/ispo"
touch "${XDG_CONFIG_HOME:-$HOME/.config}/ispo/postgres-connections.json"
```

2. Add your database credentials:
```json
{
  "databases": [
    {
      "name": "prod",
      "description": "Production - users, orders, transactions",
      "host": "db.example.com",
      "port": 5432,
      "database": "app_prod",
      "user": "readonly",
      "password": "secret",
      "sslmode": "require"
    }
  ]
}
```

3. Secure the config:
```bash
chmod 600 "${XDG_CONFIG_HOME:-$HOME/.config}/ispo/postgres-connections.json"
```

## Usage

```bash
# List configured databases
python3 scripts/query.py --list

# List tables
python3 scripts/query.py --db prod --tables

# Show schema
python3 scripts/query.py --db prod --schema

# Run query
python3 scripts/query.py --db prod --query "SELECT * FROM users" --limit 100
```

## Config Fields

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| name | Yes | - | Database identifier |
| description | Yes | - | What data it contains (for auto-selection) |
| host | Yes | - | Hostname |
| port | No | 5432 | Port |
| database | Yes | - | Database name |
| user | Yes | - | Username |
| password | Yes | - | Password |
| sslmode | No | prefer | disable, allow, prefer, require, verify-ca, verify-full |

## Safety Features

- **Read-only sessions**: PostgreSQL `readonly=True` mode blocks writes at database level
- **Query validation**: Only SELECT, SHOW, EXPLAIN, WITH allowed
- **Single statement**: No multi-statement queries (prevents `SELECT 1; DROP TABLE`)
- **Timeouts**: 30s query timeout, 10s connection timeout
- **Memory cap**: Max 10,000 rows per query
- **Credential protection**: Passwords sanitized from error messages

## Requirements

Install `psycopg2-binary` in a user-managed isolated Python environment.
