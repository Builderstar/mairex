# Mairex Quick Start

Get started with Mairex in 5 minutes.

## Installation

```bash
pip install mairex
```

## Your First Script

Create `hello.jsom`:

```json
{
  "greeting": {
    "say_hello": [
      "~| |>echo 'Hello, Mairex!'<| |~"
    ]
  }
}
```

Run it:

```bash
mairex hello.jsom
```

## Basic Concepts

### 1. Instructions

Wrap commands in `~| |~`:

```json
["~| |>date<| |~"]
```

### 2. Variables

Store and reuse data:

```json
{
  "demo": {
    "create": [
      "~| VAR&V <&¤S- 'Hello' |~"
    ],
    "use": [
      "~| VAR&V -$S> |>echo '<$>'<| |~"
    ]
  }
}
```

### 3. Script-Level Arguments

Pass values from the command line at invocation:

```bash
mairex script.jsom "Alice" 42
```

```json
{
  "args": {
    "name": ["<ł[0]S>"],
    "age": ["<ł[1]I>"]
  },
  "demo": {
    "run": [
      "~| args.name[0].&= -$S> |>echo 'Hello, <$>!'<| |~",
      "~| args.age[0].&= -$I> |>echo 'Age: <$>'<| |~"
    ]
  }
}
```

- `<ł[0]S>` → first argument, parsed as string
- `<ł[1]I>` → second argument, parsed as integer
- Arguments act as static JSON values, read into instructions via `.&=`

### 4. AI Integration

Call AI models:

```json
{
  "ai": {
    "setup": [
      "~| A&P <&¤S- 'Explain quantum physics simply' |~"
    ],
    "input": [
      "~| A&I <&¤S- 'User wants to learn' |~"
    ],
    "output": [
      "~| A&O -€S> response.txt |~"
    ]
  }
}
```

## Common Patterns

### Download and Process

```json
{
  "workflow": {
    "download": [
      "~| |>wget https://example.com -O page.html<| |~"
    ],
    "analyze": [
      "(~| A&P <&¤S- 'Summarize this webpage' |~, ~| A&I <&€- page.html |~, ~| A&O -€S> summary.txt |~)"
    ]
  }
}
```

### Parallel Tasks

```json
{
  "parallel": [
    "~| |>task1<| |~",
    "~| |>task2<| |~",
    "~| |>task3<| |~"
  ]
}
```

Each array element runs in its own independent shell session.

**Note:** While the syntax supports specifying parallel execution (separate array elements), the current implementation executes these sequentially. True parallel execution is planned for a future release.

## Next Steps

- **Full Tutorial:** [TUTORIAL.md](TUTORIAL.md)
- **Syntax Guide:** [SYNTAX_REFERENCE.md](SYNTAX_REFERENCE.md)
- **Examples:** [EXAMPLES.md](EXAMPLES.md)

## Need Help?

```bash
mairex --help
```

**Happy orchestrating! 🚀**
