# Changelog

All notable changes to Mairex will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- Decision-based execution (`A&D`)
- Advanced branching and looping constructs
- JSON path operations
- Multi-variable assignments
- Enhanced error handling and debugging
- Interactive REPL mode
- Plugin system for custom tools

---

## [0.9.2] - 2026-04-07

### Added
- Initial release of Mairex orchestration language
- Core JSOM parser and execution engine
- Shell command execution with persistent sessions
- Custom variable system with function-level scoping
- AI variable system with shell-level isolation
- Multi-provider AI integration:
  - Ollama (local models)
  - OpenAI (GPT-4, GPT-3.5, etc.)
  - Anthropic (Claude)
  - Google (Gemini)
  - XAI (Grok)
- Data flow operators:
  - Command output capture (`&#`)
  - File content operations (`&€`)
  - Raw value assignment (`&¤`)
  - JSON data access (`&=`)
- Type system (String, Integer, List)
- Parallel execution via array-based shell isolation
- Function extraction from source code (`&F`)
- Chainable assignments (left-to-right and right-to-left)
- Comprehensive documentation:
  - README with quick start
  - Complete syntax reference
  - Step-by-step tutorial
  - Real-world examples
  - Packaging guide

### Features

#### Shell Integration
- Persistent shell sessions per array index
- Multiple command execution in same shell
- Command concatenation
- Independent parallel shell execution

#### AI Capabilities
- Native integration with multiple AI providers
- Configurable model, prompt, and service per shell
- Input/output management
- Parallel AI model execution

#### Data Management
- Variable scoping (custom vs AI)
- File read/write operations
- JSON value access and modification
- Dynamic array indexing
- Type conversion and validation

#### Syntax
- JSON-based declarative format (.jsom files)
- Instruction specifiers (`~| |~`)
- Shell command markers (`|> <|`)
- Rich assignment operators
- Variable placeholders (`<$>`)

### Dependencies
- Python 3.8+
- ollama >= 0.1.0
- litellm >= 1.0.0
- lizard >= 1.17.0
- whats-that-code >= 0.1.0

### Documentation
- README.md - Project introduction and quick start
- SYNTAX_REFERENCE.md - Complete language specification
- TUTORIAL.md - Step-by-step learning guide
- EXAMPLES.md - Real-world use cases
- PACKAGING_GUIDE.md - Publishing and distribution guide

### Known Limitations (Alpha)
- Error handling is basic (errors logged but don't stop execution)
- Decision-based execution not yet implemented
- Branching and looping constructs not yet implemented
- JSON variable operations partially implemented
- Limited debugging capabilities
- No interactive mode

### Notes
This is an alpha release. APIs and syntax may change in future versions.

---

## Legend

- `Added` - New features
- `Changed` - Changes in existing functionality
- `Deprecated` - Soon-to-be removed features
- `Removed` - Removed features
- `Fixed` - Bug fixes
- `Security` - Security fixes

---

**For upgrade instructions and migration guides, see [UPGRADE.md](UPGRADE.md)**
