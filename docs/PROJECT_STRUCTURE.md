# Project Structure

This document describes the organization of the Skoda MQTT Bridge project.

## Directory Layout

```
myskoda-mqtt/
│
├── myskoda_mqtt/              # Main Python package
│   ├── __init__.py            # Package initialization and version info
│   ├── main.py                # Application entry point and main loop
│   ├── config.py              # Configuration management
│   ├── skoda_api.py           # Skoda Connect API client
│   └── mqtt_client.py         # MQTT client wrapper
│
├── systemd/                   # Systemd service files
│   └── myskoda-mqtt.service   # Service definition for systemd
│
├── scripts/                   # Installation and maintenance scripts
│   ├── install.sh             # Installation script
│   └── uninstall.sh           # Uninstallation script
│
├── docs/                      # Documentation
│   ├── QUICKSTART.md          # Quick start guide
│   ├── MQTT_TOPICS.md         # MQTT topics reference
│   ├── SECURITY.md            # Security considerations
│   ├── TROUBLESHOOTING.md     # Troubleshooting guide
│   └── PROJECT_STRUCTURE.md   # This file
│
├── .github/                   # GitHub-specific files
│   └── ISSUE_TEMPLATE/        # Issue templates
│       ├── bug_report.md      # Bug report template
│       └── feature_request.md # Feature request template
│
├── README.md                  # Main project documentation
├── LICENSE                    # MIT License
├── CONTRIBUTING.md            # Contribution guidelines
├── requirements.txt           # Python dependencies
├── config.example.json        # Example configuration file
└── .gitignore                 # Git ignore rules
```

## File Descriptions

### Core Application Files

#### `myskoda_mqtt/__init__.py`
- Package initialization
- Version information
- Package metadata

#### `myskoda_mqtt/main.py`
- Application entry point
- Main bridge class (`SkodaMQTTBridge`)
- Main polling loop
- Signal handlers for graceful shutdown
- Command-line argument parsing

#### `myskoda_mqtt/config.py`
- Configuration management class
- Loads settings from JSON file or environment variables
- Configuration validation
- Safe configuration export (redacts secrets)

#### `myskoda_mqtt/skoda_api.py`
- Skoda Connect API client
- Authentication and token management
- Vehicle status retrieval
- Command execution (charging, locking)
- Automatic token refresh

#### `myskoda_mqtt/mqtt_client.py`
- MQTT client wrapper
- Connection management
- State publishing
- Command subscription and handling
- Home Assistant MQTT Discovery

### Installation Files

#### `scripts/install.sh`
- Automated installation script
- Installs Python dependencies via apt
- Creates directories and sets permissions
- Installs systemd service
- Creates example configuration

#### `scripts/uninstall.sh`
- Automated uninstallation script
- Stops and disables service
- Removes installation files
- Optionally removes config and logs

#### `systemd/myskoda-mqtt.service`
- Systemd service definition
- Service configuration and dependencies
- Security hardening settings
- Restart policy

### Documentation Files

#### `README.md`
- Main project documentation
- Features and architecture overview
- Installation and configuration instructions
- Quick reference

#### `docs/QUICKSTART.md`
- Step-by-step quick start guide
- Minimal configuration examples
- Verification steps
- Next steps and examples

#### `docs/MQTT_TOPICS.md`
- Complete MQTT topics reference
- Topic descriptions and examples
- Home Assistant discovery details
- Example commands

#### `docs/SECURITY.md`
- Security considerations and best practices
- Credential management
- MQTT security
- API security
- Incident response

#### `docs/TROUBLESHOOTING.md`
- Common issues and solutions
- Diagnostic commands
- Advanced debugging
- Command reference

#### `CONTRIBUTING.md`
- Contribution guidelines
- Development setup
- Code style guidelines
- Areas for contribution

### Configuration Files

#### `config.example.json`
- Example configuration file
- Shows all available options
- Safe to commit (no secrets)

#### `requirements.txt`
- Python package dependencies
- Version specifications
- Installation notes for apt

#### `.gitignore`
- Git ignore rules
- Excludes secrets and generated files
- Python-specific ignores

#### `LICENSE`
- MIT License text
- Copyright information

## Runtime Directories

When installed, the following directories are created:

```
/opt/myskoda-mqtt/          # Installation directory
├── myskoda_mqtt/           # Python package (copied from repo)
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── skoda_api.py
│   └── mqtt_client.py

/etc/myskoda-mqtt/          # Configuration directory
└── config.json             # Active configuration (contains secrets)

/var/log/myskoda-mqtt/      # Log directory (if file logging enabled)

/etc/systemd/system/        # Systemd directory
└── myskoda-mqtt.service    # Installed service file
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     myskoda_mqtt/main.py                    │
│                    (SkodaMQTTBridge class)                  │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   config.py  │  │ skoda_api.py │  │mqtt_client.py│    │
│  │              │  │              │  │              │    │
│  │ Load config  │  │ Authenticate │  │ Connect to   │    │
│  │ Validate     │  │ Get status   │  │ MQTT broker  │    │
│  │              │  │ Send commands│  │ Pub/Sub      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                  │                  │            │
└─────────┼──────────────────┼──────────────────┼────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
    config.json      Skoda Connect API    MQTT Broker
                                                │
                                                ▼
                                         Home Assistant
```

## Module Dependencies

```
main.py
├── config.py
├── skoda_api.py
│   └── requests (external)
└── mqtt_client.py
    └── paho.mqtt (external)
```

## Development Workflow

1. **Clone repository**
   ```bash
   git clone https://github.com/mikitu/myskoda-mqtt.git
   ```

2. **Make changes**
   - Edit files in `myskoda_mqtt/`
   - Update documentation in `docs/`
   - Test locally

3. **Test installation**
   ```bash
   sudo ./scripts/install.sh
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "Description"
   git push
   ```

## Adding New Features

### Adding a new vehicle attribute

1. Update `skoda_api.py`:
   - Add retrieval in `get_vehicle_status()`

2. Update `mqtt_client.py`:
   - Add publishing in `publish_state()`
   - Add discovery config in `publish_ha_discovery()`

3. Update `docs/MQTT_TOPICS.md`:
   - Document new topic

### Adding a new command

1. Update `skoda_api.py`:
   - Add command method (e.g., `set_climate()`)

2. Update `main.py`:
   - Add handler in `_register_command_handlers()`

3. Update `mqtt_client.py`:
   - Register callback in `_register_command_handlers()`

4. Update `docs/MQTT_TOPICS.md`:
   - Document new command topic

## Code Style

- **Python**: PEP 8 style guide
- **Docstrings**: Google style
- **Type hints**: Used where appropriate
- **Logging**: Structured with appropriate levels
- **Error handling**: Specific exceptions with clear messages

## Testing

Currently manual testing only. Future additions:
- Unit tests for each module
- Integration tests
- CI/CD pipeline

