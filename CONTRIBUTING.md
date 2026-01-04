# Contributing to Skoda MQTT Bridge

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Relevant log excerpts

**Security vulnerabilities**: Please report privately via email (see SECURITY.md)

### Suggesting Features

Feature requests are welcome! Please:
- Check if the feature has already been requested
- Clearly describe the use case
- Explain why it would be useful to most users
- Consider if it fits the project's scope

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**:
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed
4. **Test your changes**:
   - Test manually with a real vehicle (if possible)
   - Ensure no regressions
5. **Commit with clear messages**:
   - Use descriptive commit messages
   - Reference issues if applicable
6. **Push and create PR**:
   - Describe what your PR does
   - Link to related issues
   - Explain testing performed

## Development Setup

### Local Development

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/myskoda-mqtt.git
cd myskoda-mqtt

# Install dependencies (if using pip)
pip install -r requirements.txt

# Or on Debian/Ubuntu
sudo apt install python3-requests python3-paho-mqtt

# Create a config file
cp config.example.json config.json
# Edit config.json with your credentials

# Run locally
python3 -m myskoda_mqtt.main --config config.json
```

### Code Style

- Follow PEP 8 style guide
- Use type hints where appropriate
- Keep functions focused and small
- Add docstrings to classes and functions
- Use meaningful variable names

### Testing

Currently, this project doesn't have automated tests. Contributions to add testing infrastructure are welcome!

Manual testing checklist:
- [ ] Service starts without errors
- [ ] MQTT connection established
- [ ] Vehicle state published correctly
- [ ] Commands execute successfully
- [ ] Home Assistant discovery works
- [ ] Logs are clear and helpful

## Project Structure

```
myskoda-mqtt/
├── myskoda_mqtt/          # Main Python package
│   ├── __init__.py        # Package initialization
│   ├── main.py            # Application entry point
│   ├── config.py          # Configuration management
│   ├── skoda_api.py       # Skoda Connect API client
│   └── mqtt_client.py     # MQTT client wrapper
├── systemd/               # Systemd service files
│   └── myskoda-mqtt.service
├── scripts/               # Installation scripts
│   ├── install.sh
│   └── uninstall.sh
├── docs/                  # Documentation
│   ├── MQTT_TOPICS.md
│   └── SECURITY.md
├── README.md
├── LICENSE
└── requirements.txt
```

## Areas for Contribution

### High Priority

- **Actual Skoda API implementation**: The current API client is a placeholder
- **Error handling improvements**: Better handling of API errors and edge cases
- **Testing**: Unit tests, integration tests
- **Documentation**: More examples, troubleshooting guides

### Medium Priority

- **Additional vehicle data**: Climate, windows, location (if API supports)
- **MQTT TLS support**: Secure MQTT connections
- **Configuration validation**: Better config file validation
- **Metrics/monitoring**: Prometheus metrics, health checks

### Low Priority

- **Multiple vehicles**: Support for multiple vehicles in one instance
- **Web UI**: Simple web interface for monitoring
- **Docker support**: Optional Docker deployment (in addition to systemd)

## Skoda Connect API

The Skoda Connect API is not officially documented. Implementation is based on:
- Reverse engineering of official apps
- Community efforts
- Trial and error

If you have knowledge of the API, contributions are especially welcome!

### API Resources

- [WeConnect-python](https://github.com/tillsteinbach/WeConnect-python) - VW Group API library
- [Skoda Connect API discussion](https://github.com/skodaconnect/homeassistant-skodaconnect)

## Code of Conduct

- Be respectful and constructive
- Welcome newcomers
- Focus on what's best for the project
- Accept constructive criticism gracefully

## Questions?

Feel free to open an issue for questions or discussions!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

