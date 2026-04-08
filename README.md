# Mairex

> An experimental orchestration language for AI models and system commands

Mairex is an orchestration language that allows you to coordinate AI models, shell commands, and data flows using a JSON-based syntax with specialized operators. It's designed for developers who want to prototype AI workflows and automation scripts.

**⚠️ Alpha Status:** Mairex is in early development (v0.9.2). Expect bugs, missing features, and potential breaking changes in future versions.

## Current Limitations

- Sequential execution only (parallel execution syntax exists but runs sequentially)
- Basic error handling
- Limited debugging capabilities
- Many planned features not yet implemented
- Documentation may be ahead of implementation in some areas

## What It Does

Mairex lets you write scripts that combine shell commands and AI model calls in a declarative way. For example, you can download websites, process them with AI models, and save outputs to files - all coordinated through a single `.jsom` file.

## ✨ Features

- 🤖 **Native AI Integration** - Call Ollama, OpenAI, Anthropic, Gemini, and XAI models directly
- 🔄 **Parallel Execution** - Run multiple shells and AI models concurrently
- 🔗 **Chainable Operations** - Flow data between commands, files, and AI models
- 📦 **Variable Scoping** - Custom and AI-specific variable management
- 🎯 **JSON-Based Syntax** - Familiar structure with powerful extensions
- 🛠️ **Shell Integration** - Execute any terminal command with persistent shell sessions
- 🧩 **Script-Level Arguments** - Pass runtime parameters to scripts from the command line

## 🚀 Quick Start

### Installation

```bash
pip install mairex
```

### Your First Mairex Script

Create a file `hello.jsom`:

```json
{
  "greeting": {
    "set_input": [
      "~| A&I <&¤S- 'World' |~"
    ],
    "set_prompt": [
      "~| A&P <&¤S- 'Say hello to the input' |~"
    ],
    "call_ai": [
      "~| A&O -$S> |>echo '<$>'<| |~"
    ]
  }
}
```

Run it:

```bash
mairex hello.jsom
```

**What this does:**
1. Sets AI input to "World"
2. Sets AI prompt to "Say hello to the input"
3. Calls the AI model and echoes the response

## 📚 Core Concepts

### JSOM Files

Mairex scripts use `.jsom` files (JSON + Mairex). They follow standard JSON syntax with one rule:

**All leaf nodes must be arrays:**

```json
{
  "step": {
    "action": ["value"]
  }
}
```

NOT:

```json
{
  "step": {
    "action": "value"
  }
}
```

### Instructions

Instructions are declared between `~| |~` specifiers:

```json
["~| |>echo 'Hello'<| |~"]
```

Shell commands go between `|> <|`:

```json
["~| |>ls -la<| |~"]
```

### Variables

**Custom Variables** (shared across shells, scoped to function):
```json
["~| VAR&V <&¤S- 'my value' |~"]
```

**AI Variables** (shell-specific, persistent across tree levels):
```json
["~| A&I <&¤S- 'AI input' |~"]
```

### Data Flow

**Left to right:**
```json
["~| |>echo 'output'<| -&#> FILE&V -€S> result.txt |~"]
```

**Right to left:**
```json
["~| FILE&V <&€- result.txt <&#- |>cat file.txt<| |~"]
```

### Parallel Execution

**Separate shells (parallel):**
```json
{
  "parallel_tasks": [
    "~| |>echo 'Shell 1'<| |~",
    "~| |>echo 'Shell 2'<| |~",
    "~| |>echo 'Shell 3'<| |~"
  ]
}
```

Each array element runs in its own independent shell session.

### Script-Level Arguments

Pass values from the command line into your script using `<ł[N]T>` placeholders:

```bash
mairex analyze.jsom report.txt llama3
```

```json
{
  "inputs": {
    "file": ["<ł[0]S>"],
    "model": ["<ł[1]S>"]
  },
  "analyze": {
    "setup": [
      "~| MODEL_NAME&V <&=- inputs.model[0].&= |~",
      "~| A&M <S- MODEL_NAME&V |~"
    ],
    "load": [
      "~| FILE_NAME&V <&=- inputs.file[0].&= |~",
      "~| FILE_NAME&V -$S> |>cat '<$>'<| -&#> A&I |~"
    ],
    "save": [
      "~| A&O -€S> summary.txt |~"
    ]
  }
}
```

Place placeholders as normal strings inside the JSON block, then access them inside instructions using standard JSON value access (`.&=`). Supports `S` (String), `I` (Integer), and `L` (List) types.

## 🎓 Learn More

- **[Syntax Reference](SYNTAX_REFERENCE.md)** - Complete language specification
- **[Tutorial](TUTORIAL.md)** - Step-by-step guide
- **[Examples](EXAMPLES.md)** - Real-world use cases

## 🔧 Requirements

- Python 3.8+
- Dependencies (auto-installed):
  - `ollama` - Local AI model support
  - `litellm` - Multi-provider AI API support
  - `lizard` - Code analysis for function extraction
  - `whats_that_code` - Programming language detection

## 🌐 AI Provider Setup

### Using Ollama (Local Models)

1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama3`
3. No API keys needed - works out of the box!

### Using Cloud AI Providers

Create `API_keys.json` in your working directory:

```json
{
  "openai": "sk-your-key-here",
  "anthropic": "sk-ant-your-key-here",
  "gemini": "your-gemini-key",
  "xai": "your-xai-key"
}
```

Set the provider in your JSOM file:

```json
["~| A&S <&¤S- 'openai' |~"]
["~| A&M <&¤S- 'gpt-4o' |~"]
```

## 📄 License

MIT License

## Development Status

This is an early alpha release. The project is not currently accepting outside contributions. Bug reports and feedback are welcome via GitHub issues.

---

**An experimental tool for AI orchestration**
