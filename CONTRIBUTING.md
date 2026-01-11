# Contributing to SDG RAG System

Thank you for your interest in contributing to our AI-powered RAG system for UN/UN Habitat SDG file management!

## 🤝 How to Contribute

### Reporting Issues
- Use the issue templates provided
- Include detailed reproduction steps
- Specify your environment (OS, Python version, etc.)
- Mention which API keys are configured

### Development Setup
1. Fork the repository
2. Clone your fork locally
3. Create a virtual environment: `python -m venv venv`
4. Activate it: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
5. Install dependencies: `pip install -r requirements.txt`
6. Copy `.env.example` to `.env` and configure your API keys
7. Create a new branch: `git checkout -b feature/your-feature-name`

### Code Guidelines
- Follow PEP 8 style guidelines
- Add type hints where appropriate
- Include docstrings for new functions
- Test your changes before submitting

### Submitting Changes
1. Commit your changes with clear messages
2. Push to your fork: `git push origin feature/your-feature-name`
3. Create a Pull Request with a detailed description

## 🎯 Contribution Areas

### High Priority
- **SDG Classification**: Improve AI prompts and classification accuracy
- **Document Processing**: Support for additional file formats
- **API Integration**: Add more transportation and UN APIs
- **Frontend Development**: React dashboard for system monitoring

### Medium Priority
- **Testing**: Unit tests and integration tests
- **Performance**: Optimize vector search and API calls
- **Documentation**: API docs and user guides
- **Security**: Enhanced authentication and authorization

### Low Priority
- **Localization**: Multi-language support
- **Mobile Apps**: React Native or Flutter applications
- **Advanced Analytics**: ML models for trend prediction

## 📋 Development Workflow

### Before Coding
1. Check existing issues for similar requests
2. Discuss your approach in an issue or discussion
3. Ensure you understand the system architecture

### During Development
1. Write clean, documented code
2. Test edge cases and error conditions
3. Update documentation as needed
4. Follow the existing code patterns

### After Development
1. Test your changes thoroughly
2. Update README if needed
3. Ensure all tests pass
4. Submit a descriptive Pull Request

## 🔧 Technical Guidelines

### API Integration
- Use the existing `TransportationAgent` pattern for new APIs
- Implement proper error handling and rate limiting
- Add API key validation in settings
- Include SDG relevance mapping

### SDG Classification
- Use the `SDGClassifier` for AI-powered categorization
- Include confidence scores and reasoning
- Map content to multiple SDG goals when relevant
- Provide fallback keyword-based classification

### Database Changes
- Use Alembic for database migrations
- Update both PostgreSQL and vector store schemas
- Include proper indexes for performance
- Document schema changes

## 🌍 SDG Impact Considerations

When contributing, consider how your changes support the Sustainable Development Goals:
- **SDG 4**: Quality education through better information access
- **SDG 9**: Industry innovation through improved infrastructure
- **SDG 11**: Sustainable cities through better data integration
- **SDG 13**: Climate action through environmental monitoring
- **SDG 16**: Peace and justice through transparent information

## 📞 Getting Help

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Report bugs or request features
- **Documentation**: Check the README and API docs
- **Code Review**: Request reviews from maintainers

## 📜 Code of Conduct

Be respectful, inclusive, and constructive in all interactions. Focus on what's best for the community and the UN's sustainable development mission.

## 🏆 Recognition

Contributors will be recognized in:
- README contributors section
- Release notes for significant contributions
- Special badges for long-term contributors

Thank you for helping improve SDG data management and search capabilities! 🌍