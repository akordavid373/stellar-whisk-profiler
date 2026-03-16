# Contributing to Stellar Whisk Parallelism Profiler

Thank you for your interest in contributing to Stellar Whisk Parallelism Profiler! This document provides guidelines and information for contributors.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Git
- GitHub account

### Setup Development Environment

1. **Fork and Clone**
   ```bash
   # Fork the repository on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/stellar-whisk-profiler.git
   cd stellar-whisk-profiler
   ```

2. **Install Dependencies**
   ```bash
   # Install in development mode with all dependencies
   make install-all
   # or
   pip install -e ".[dev]"
   ```

3. **Run Tests**
   ```bash
   make test
   ```

4. **Start Development Server**
   ```bash
   make dev-server
   ```

## 📋 How to Contribute

### Reporting Issues

We use GitHub Issues to track bugs, feature requests, and other tasks. Before creating a new issue:

1. **Search existing issues** to avoid duplicates
2. **Use appropriate templates** (Bug Report, Feature Request, etc.)
3. **Provide detailed information** including:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Relevant logs or screenshots

### Issue Templates

#### Bug Report
- **Title**: Brief description of the bug
- **Description**: Detailed explanation
- **Steps to Reproduce**: Clear, numbered steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, dependencies
- **Additional Context**: Any other relevant information

#### Feature Request
- **Title**: Brief description of the feature
- **Problem**: What problem does this solve?
- **Proposed Solution**: How should it work?
- **Alternatives Considered**: Other approaches you've thought about
- **Additional Context**: Any other relevant information

### Pull Requests

#### Before Submitting
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run all tests**: `make test`
6. **Check code quality**: `make check`
7. **Commit your changes** with clear messages
8. **Push to your fork**: `git push origin feature/your-feature-name`
9. **Create a Pull Request**

#### Pull Request Guidelines
- **Title**: Clear, descriptive title
- **Description**: Explain what you changed and why
- **Testing**: Describe how you tested your changes
- **Screenshots**: For UI changes, include before/after screenshots
- **Breaking Changes**: Clearly document any breaking changes

#### Code Style
- Follow PEP 8 style guidelines
- Use `make format` to auto-format code
- Add type hints for new functions
- Write docstrings for public functions
- Keep changes focused and minimal

## 🏗️ Development Workflow

### Component Areas

We welcome contributions in these areas:

#### Frontend (🌐)
- **Location**: `frontend/`
- **Technologies**: FastAPI, HTML, CSS, JavaScript, Plotly
- **Areas**: Dashboard UI, charts, user experience
- **Issues**: Look for labels `frontend`, `ui`, `dashboard`

#### Backend (⚙️)
- **Location**: `backend/`
- **Technologies**: Python, psutil, threading, data processing
- **Areas**: Profiling engine, metrics collection, sampling algorithms
- **Issues**: Look for labels `backend`, `profiling`, `metrics`

#### Contracts (🔗)
- **Location**: `contracts/`
- **Technologies**: Stellar SDK, Horizon API, Soroban
- **Areas**: Transaction profiling, contract analysis, network monitoring
- **Issues**: Look for labels `stellar`, `contracts`, `blockchain`

#### Documentation (📖)
- **Location**: `docs/`
- **Areas**: User guides, API documentation, tutorials
- **Issues**: Look for labels `documentation`, `docs`

### Development Commands

```bash
# Development helpers
make dev-backend      # Focus on backend development
make dev-frontend     # Focus on frontend development
make dev-contracts    # Focus on contracts development

# Testing
make test             # Run all tests
make test-backend     # Test backend only
make test-frontend    # Test frontend only
make test-contracts   # Test contracts only
make test-integration # Integration tests

# Code quality
make check            # Run all quality checks
make format           # Format code
make lint             # Lint code
make type-check       # Type checking
```

## 🐛 Bug Triage Process

### Issue Labels
- `bug`: Confirmed bugs
- `enhancement`: Feature requests
- `documentation`: Documentation issues
- `good first issue`: Good for newcomers
- `help wanted`: Community help needed
- `priority/high`, `priority/medium`, `priority/low`: Issue priority

### Triage Workflow
1. **New Issue**: Reviewed within 48 hours
2. **Classification**: Labeled with appropriate tags
3. **Assignment**: Assigned to maintainer or contributor
4. **Planning**: Added to milestone or backlog
5. **Resolution**: Fixed, documented, or closed

## 🎯 Contribution Areas

### Good First Issues
Look for issues labeled `good first issue` - these are great for getting started:
- Small bug fixes
- Documentation improvements
- Simple feature additions
- Test improvements

### Help Wanted
Issues labeled `help wanted` need community assistance:
- Complex features
- Research tasks
- Performance improvements
- Integration testing

### Expert Contributions
Areas requiring specific expertise:
- **Stellar Blockchain**: Deep knowledge of Stellar protocol
- **Performance Engineering**: Optimization and profiling expertise
- **Frontend Development**: Modern web technologies
- **DevOps**: CI/CD, deployment, infrastructure

## 📝 Development Guidelines

### Code Standards
- **Python**: Follow PEP 8, use type hints
- **JavaScript**: Modern ES6+, consistent formatting
- **CSS**: Use TailwindCSS classes, avoid inline styles
- **Documentation**: Clear, concise, up-to-date

### Testing Requirements
- **Unit Tests**: Cover new functionality
- **Integration Tests**: Test component interactions
- **Performance Tests**: For profiling features
- **Documentation Tests**: Verify examples work

### Security Considerations
- **Input Validation**: Validate all user inputs
- **Data Privacy**: Don't log sensitive information
- **Dependencies**: Keep dependencies updated
- **API Security**: Secure all endpoints

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Assume good intentions

### Communication
- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For general questions and ideas
- **Pull Requests**: For code contributions
- **Email**: For security issues or private matters

### Recognition
- Contributors are acknowledged in releases
- Significant contributions get special recognition
- Community members can become maintainers

## 🏆 Recognition Program

### Contributor Levels
- **Contributor**: At least one merged PR
- **Active Contributor**: Multiple meaningful contributions
- **Core Contributor**: Regular, high-quality contributions
- **Maintainer**: Trusted community member with merge rights

### Benefits
- GitHub organization membership
- Access to development resources
- Recognition in project documentation
- Voting on project decisions

## 📚 Resources

### Documentation
- [Architecture Guide](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [User Manual](docs/user-guide.md)
- [Developer Guide](docs/developer-guide.md)

### Tools and Resources
- [Stellar Documentation](https://developers.stellar.org/)
- [Python Style Guide](https://pep8.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Plotly Documentation](https://plotly.com/python/)

### Getting Help
- **GitHub Discussions**: General questions
- **Issues**: Bug reports and feature requests
- **Email**: team@stellar-whisk.org (private matters)

## 🔄 Release Process

### Version Management
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Release Cadence**: As needed, typically monthly
- **Changelog**: Maintained in CHANGELOG.md

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version bumped
- [ ] Tag created
- [ ] Release published

## 📞 Contact

### Project Maintainers
- **Lead Maintainer**: @akordavid373
- **Backend Maintainer**: [To be assigned]
- **Frontend Maintainer**: [To be assigned]
- **Contracts Maintainer**: [To be assigned]

### Getting in Touch
- **GitHub Issues**: For project-related discussions
- **Email**: team@stellar-whisk.org
- **Discord**: [Community server link]

---

Thank you for contributing to Stellar Whisk Parallelism Profiler! Your contributions help make Stellar blockchain development better for everyone. 🚀
