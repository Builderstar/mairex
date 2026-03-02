# Mairex Syntax Reference

Complete specification of the Mairex orchestration language.

## Table of Contents

- [File Structure](#file-structure)
- [Data Types](#data-types)
- [Instruction Syntax](#instruction-syntax)
- [Assignment Operators](#assignment-operators)
- [Variables](#variables)
- [Shell Commands](#shell-commands)
- [AI Model Integration](#ai-model-integration)
- [JSON Operations](#json-operations)
- [File Operations](#file-operations)
- [Built-in Functions](#built-in-functions)
- [Execution Model](#execution-model)
- [Advanced Patterns](#advanced-patterns)

---

## File Structure

### JSOM Format

Mairex scripts use `.jsom` files (JSON with Mairex extensions).

**Critical Rule:** All leaf nodes MUST be arrays.

```json
{
  "step_name": {
    "action_name": ["value"]
  }
}
```

**Invalid:**
```json
{
  "step_name": {
    "action_name": "value"  // ❌ Not an array
  }
}
```

### Reserved Symbols

The following symbols have special meaning and cannot appear in plain JSON values:

- `<$>` - Reserved for data type placeholders
- Variable references (`&I`, `&O`, `&V`, etc.) without `;` separator
- `~| |~` - Instruction specifiers
- `|> <|` - Shell command specifiers

---

## Data Types

### Type Specifiers

Mairex distinguishes between three data types:

| Type | Symbol | Description | Example |
|------|--------|-------------|---------|
| String | `S` | Text data | `"hello"` |
| Integer | `I` | Numeric data | `42` |
| List | `L` | Array data | `["a", "b", 3]` |

### Data Type Placeholders

Use in JSON to mark locations where values can be saved:

```json
{
  "data": {
    "string_value": ["<$S>"],
    "number_value": ["<$I>"],
    "list_value": ["<$L>"]
  }
}
```

These placeholders allow the runtime to save values back into the JSON structure.

---

## Instruction Syntax

### Basic Instruction

Instructions are wrapped in `~| |~`:

```json
["~| <instruction> |~"]
```

### Shell Command Syntax

Shell commands are wrapped in `|> <|`:

```json
["~| |>echo 'Hello World'<| |~"]
```

### Multiple Shell Commands (Sequential in Same Shell)

Use parentheses with comma separation:

```json
["~| |>cd /tmp && ls -la<| |~"]
```

This executes: `cd /tmp` then `ls -la` in the same shell session.

### Multiple Shell Commands (Building Single Command)

Use `(> <)` to concatenate into one command:

```json
["~| (> |>echo<|, |>'Hello'<| <) |~"]
```

This executes: `echo 'Hello'` as a single command.

### Parallel Execution

Array elements execute in separate, independent shell sessions:

```json
{
  "parallel": [
    "~| |>echo 'Shell 0'<| |~",
    "~| |>echo 'Shell 1'<| |~",
    "~| |>echo 'Shell 2'<| |~"
  ]
}
```

Each instruction runs in its own shell (Shell 0, Shell 1, Shell 2).

### Parenthesized Parallel Instructions

Execute multiple instructions in same array position sequentially:

```json
["(~| |>command1<| |~, ~| |>command2<| |~)"]
```

---

## Assignment Operators

### Direction Operators

- `->` - Assign from **left to right**
- `<-` - Assign from **right to left**

### Data Source Operators

Combine with direction to specify data source:

| Operator | Meaning | Use Case |
|----------|---------|----------|
| `&#` | Command **output** | Capture stdout/stderr from shell |
| `&€` | File **content** | Read/write file contents |
| `&=` | JSON **value** | Access JSON data in the JSOM file |
| `&¤` | **Raw** value | Literal string/number/list from JSOM |

### Data Type Operators

Specify how to interpret/convert data:

| Operator | Meaning | Use Case |
|----------|---------|----------|
| `$S` | String variable | Pass as text |
| `$I` | Integer variable | Pass as number |
| `$L` | List variable | Pass as array |

### Assignment Combinations

#### Left to Right (`->`)

Format: `<source>-<data_source><data_type>> <destination>`

**Examples:**

```json
// Capture command output and assign to variable
["~| |>date<| -&#> TIME&V |~"]

// Read file content and assign to variable
["~| script.py -&€> CODE&V |~"]

// Pass raw string to variable
["~| 'hello world' -&¤S> MSG&V |~"]

// Assign command output to file
["~| |>ls -la<| -&#€> output.txt |~"]
```

#### Right to Left (`<-`)

Format: `<destination> <&<data_source><data_type>- <source>`

**Examples:**

```json
// Assign raw string to AI input
["~| A&I <&¤S- 'Analyze this text' |~"]

// Assign file content to variable
["~| SCRIPT&V <&€- main.py |~"]

// Assign JSON value to variable (Buggy and not working at the moment)
["~| VAL&V <&=- data.values[0].&= |~"]
```

### Complete Assignment Reference

| Assignment | Direction | Source | Type | Destination |
|------------|-----------|--------|------|-------------|
| `-&#>` | Left→Right | Command output | (any) | Next operation |
| `-&€>` | Left→Right | File content | (any) | Next operation |
| `-&¤>` | Left→Right | Raw value | (any) | Next operation |
| `-&#$S>` | Left→Right | Command output | String | Next operation |
| `-&#$I>` | Left→Right | Command output | Integer | Next operation |
| `-&#$L>` | Left→Right | Command output | List | Next operation |
| `-&€$S>` | Left→Right | File content | String | Next operation |
| `-&¤$S>` | Left→Right | Raw value | String | Next operation |
| `-&¤$I>` | Left→Right | Raw value | Integer | Next operation |
| `-&¤$L>` | Left→Right | Raw value | List | Next operation |
| `<&#-` | Right→Left | Command output | (any) | Previous operation |
| `<&€-` | Right→Left | File content | (any) | Previous operation |
| `<&¤-` | Right→Left | Raw value | (any) | Previous operation |
| `<&#$S-` | Right→Left | Command output | String | Previous operation |
| `<&€$S-` | Right→Left | File content | String | Previous operation |
| `<&¤$S-` | Right→Left | Raw value | String | Previous operation |
| `<&¤$I-` | Right→Left | Raw value | Integer | Previous operation |
| `<&¤$L-` | Right→Left | Raw value | List | Previous operation |

---

## Variables

### Custom Variables

**Naming:** Any combination of uppercase letters + `&`

**Scope:** Shared across all parallel shells within the same function level

**Entries:**
- `&V` - **Value**: The actual data stored
- `&S` - **Script**: Source code content
- `&F` - **Function**: Extracted function from script
- `&J` - **JSON**: JSON data (not yet implemented)
- `&P` - **Picture**: Raw image data (not yet implemented)

**Examples:**

```json
// Declare and set a variable
["~| DATA&V <&¤S- 'my data' |~"]

// Store script in variable
["~| MYSCRIPT&S <&€- script.py |~"]

// Access variable value
["~| DATA&V -$S> |>echo '<$>'<| |~"]

// Variable shared across parallel shells
{
  "shared": [
    "~| SHARED&V <&¤S- 'data' |~",
    "~| SHARED&V -$S> |>echo '<$>'<| |~",
    "~| SHARED&V -$S> |>echo '<$>'<| |~"
  ]
}
// All three shells see the same SHARED&V value
```

### AI Variables

**Naming:** `A&` (fixed)

**Scope:** Independent per parallel shell, persistent across JSON tree levels within that shell

**Entries:**
- `&I` - **Input**: Data to pass to AI model
- `&O` - **Output**: AI model response
- `&D` - **Decision**: AI decision from output (not yet implemented)
- `&M` - **Model**: Model name (e.g., `gpt-4o`, `llama3`)
- `&P` - **Prompt**: User prompt
- `&S` - **Service**: Provider (e.g., `ollama`, `openai`, `anthropic`)

**Examples:**

```json
// Set AI parameters
["~| A&M <&¤S- 'llama3:latest' |~"]
["~| A&S <&¤S- 'ollama' |~"]
["~| A&P <&¤S- 'You are a helpful assistant' |~"]
["~| A&I <&¤S- 'What is 2+2?' |~"]

// Trigger AI call and get output
["~| A&O -$S> |>echo '<$>'<| |~"]
```

**AI Variable Independence:**

```json
{
  "parallel_ai": [
    "(~| A&M <&¤S- 'llama3' |~, ~| A&I <&¤S- 'Task 1' |~)",
    "(~| A&M <&¤S- 'gpt-4o' |~, ~| A&I <&¤S- 'Task 2' |~)"
  ]
}
// Shell 0 uses llama3, Shell 1 uses gpt-4o independently
```

---

## Shell Commands

### Basic Execution

```json
["~| |>ls -la<| |~"]
```

### Persistent Shell Sessions

Each array index maintains its own shell session:

```json
{
  "workflow": [
    "~| |>cd /tmp<| |~",
    "~| |>pwd<| |~"
  ]
}
```

Shell 0: `cd /tmp`
Shell 1: `pwd` (in a different shell, not in /tmp)

### Sequential Commands in Same Shell

```json
{
  "workflow": [
    "~| |>cd /tmp && pwd<| |~"
  ]
}
```

This runs both commands in Shell 0, so `pwd` shows `/tmp`.

### Command Output Capture

```json
["~| |>date<| -&#> TIME&V |~"]
```

Captures the output of `date` command into `TIME&V` variable.

### Using Variables in Commands

```json
["~| VAR&V <&¤S- 'hello' |~"]
["~| VAR&V -$S> |>echo '<$>'<| |~"]
```

The `<$>` placeholder is replaced with the variable value.

---

## AI Model Integration

### AI Call Flow

1. Set service provider
2. Set model name
3. Set prompt (optional)
4. Set input data
5. Access output (`A&O` triggers the actual API call)

### Complete AI Example

```json
{
  "ai_task": {
    "configure": [
      "(~| A&S <&¤S- 'openai' |~, ~| A&M <&¤S- 'gpt-4o' |~, ~| A&P <&¤S- 'Summarize this text' |~)"
    ],
    "run": [
      "~| A&I <&€- document.txt |~"
    ],
    "output": [
      "~| A&O -€S> summary.txt |~"
    ]
  }
}
```

### Multiple AI Models in Parallel

```json
{
  "multi_ai": {
    "setup": [
      "(~| A&M <&¤S- 'llama3' |~, ~| A&P <&¤S- 'Extract names' |~)",
      "(~| A&S <&¤S- 'openai' |~, ~| A&M <&¤S- 'gpt-4o' |~, ~| A&P <&¤S- 'Extract dates' |~)",
      "(~| A&S <&¤S- 'anthropic' |~, ~| A&M <&¤S- 'claude-3-5-sonnet-20241022' |~, ~| A&P <&¤S- 'Extract locations' |~)"
    ],
    "input": [
      "~| A&I <&€- article.txt |~",
      "~| A&I <&€- article.txt |~",
      "~| A&I <&€- article.txt |~"
    ],
    "output": [
      "~| A&O -€S> names.txt |~",
      "~| A&O -€S> dates.txt |~",
      "~| A&O -€S> locations.txt |~"
    ]
  }
}
```

### Default AI Configuration

If not specified, defaults to:
- Model: `llama3:latest`
- Service: `ollama`
- Prompt: `AI_prompt`
- Input: `AI_input`

---

## JSON Operations

### Accessing JSON Values

Use `.&=` to access values in the JSOM file:

```json
{
  "data": {
    "commands": ["ls", "pwd", "date"]
  },
  "commands": {
    "download": [
      "~| data.commands[0].|>&=<| |~"
    ]
  }
}
```

Accesses `data.commands[0]` → `ls` → runs `ls`

### JSON Path Syntax

Format: `path.to.value.&=` (Buggy and not working at the moment)

```json
{
  "config": {
    "server": {
      "port": ["8080"]
    }
  },
  "start": [
    "~| config.server.port[0].&= -$I> |>python server.py <$>| |~"
  ]
}
```

### Variable JSON Array Access

```json
{
  "data": {
  "commands": ["ls", "pwd", "date"]
  },
  "test": [
    "~| 2 -&¤I$> data.commands[<$>].|>&=<| -&#$S> |>echo '<$>'<| |~"
  ]
}
```

The `<$>` in `[<$>]` is replaced with `2`, accessing `items[2]` → `date`

### Saving Back to JSON

Use placeholders with array reference:

```json
{
  "data": {
  "results": ["<$S>"]
  },
  "process": [
    "~| |>echo 'date'<| -&#$S> data.results[0<$>].|>&=<| |~"
  ]
}
```

The `[0<$>]` saves the command output to `results[0]` in the JSON structure.

**General pattern:**
- `[N<$>]` - Save to array index N
- `[<$>]` - Use variable value as array index (no save)

---

## File Operations

### Reading Files

```json
["~| CONTENT&V <&€- myfile.txt |~"]
```

Reads `myfile.txt` content into `CONTENT&V`.

### Writing Files

```json
["~| |>echo 'data'<| -&#€S> output.txt |~"]
```

Writes command output to `output.txt`.

### File Paths

Files are resolved relative to the directory where the JSOM script is executed.

```json
// Absolute path
["~| CONTENT&V <&€- /home/user/data.txt |~"]

// Relative path (from execution directory)
["~| CONTENT&V <&€- ./config.json |~"]
```

### Chaining File Operations

```json
["~| input.txt <&€- CODE&V <&#- |>cat source.py<| |~"]
```

Right to left: `cat source.py` → output to `CODE&V` → write to `input.txt`

---

## Built-in Functions

### Function Extraction (`;`)

Extract functions from source code stored in variables.

**Syntax:** `VARIABLE&F ; function_name()`

**Example:**

```json
{
  "scripts": {
    "load": [
      "~| MYSCRIPT&S <&€- script.py |~"
    ],
    "functions": [
      "ID_PLACEHOLDER",
      "MYSCRIPT&F ; main()",
      "ID_PLACEHOLDER"
    ],
    "use": [
      "~| (> |>echo<|, scripts.functions[1].|>&=<| <)"
    ]
  }
}
```

**How it works:**
1. `MYSCRIPT&S` stores the script content
2. `MYSCRIPT&F ; main()` extracts the `main()` function
3. The extracted function code replaces the string in the JSON
4. Access it later via JSON path

**Supported Languages:**
- Python, JavaScript, TypeScript, C, C++, Java, Go, Rust, Ruby, PHP, Kotlin, Swift, Bash, C#

---

## Execution Model

### Execution Hierarchy

```
Step (JSON object)
└── Function (nested object)
    └── Command (array element)
        └── Instruction (~| |~)
            └── Shell Command (|> <|)
```

### Execution Order

1. Parse JSON top to bottom
2. Process each array element sequentially
3. Each array element = separate shell session
4. Instructions within `(~| |~, ~| |~)` execute sequentially in same shell

### Variable Scope

**Custom Variables:**
- Scoped to function level
- Shared across all parallel shells in that function

**AI Variables:**
- Scoped to shell (array index)
- Persistent across JSON tree levels within that shell

### Example Execution Flow

```json
{
  "step1": {
    "function1": [
      "~| VAR&V <&¤S- 'shared' |~",    // Shell 0
      "~| VAR&V -$S> |>echo '<$>'<| |~" // Shell 1 (sees VAR&V from Shell 0)
    ]
  },
  "step2": {
    "function2": [
      "~| VAR&V -$S> |>echo '<$>'<| |~" // Shell 0 (VAR&V not available from step1)
    ]
  }
}
```

### Shell Persistence

Shell sessions persist within their array index:

```json
{
  "workflow": {
    "task1": [
      "~| |>cd /tmp<| |~",              // Shell 0: cd /tmp
      "~| |>mkdir test<| |~"            // Shell 1: mkdir test (not in /tmp)
    ],
    "task2": [
      "~| |>pwd<| |~",                  // Shell 0: shows /tmp (persistent)
      "~| |>pwd<| |~"                   // Shell 1: shows original dir
    ]
  }
}
```

---

## Advanced Patterns

### Chained Assignments

**Left to right:**
```json
["~| |>cat file.txt<| -&#> VAR&V -$S> |>echo '<$>'<| |~"]
```

Flow: Command output → VAR&V → Echo command

**Right to left:**
```json
["~| |>echo '<$>'<| <$S- VAR&V <&#- |>cat file.txt<| |~"]
```

Flow: Command output → VAR&V → Echo command (same result, different syntax)

### Multiple Assignments

```json
["~| 'value' -&¤S> VAR1&V -S> VAR2&V -S> VAR3&V |~"]
```

Assigns `'value'` to VAR1, then VAR1 to VAR2, then VAR2 to VAR3.

### Complex AI + Shell Pipeline

```json
{
  "pipeline": {
    "download": [
      "~| |>wget https://example.com -O page.html<| |~"
    ],
    "analyze": [
      "~| A&I <&€- page.html |~"
    ],
    "extract": [
      "(~| A&P <&¤S- 'Extract all URLs as JSON list' |~, ~| A&O -€S> urls.json |~)"
    ],
    "download_urls": [
      "~| urls.json -&€> DATA&V -$L> |>wget '<$>'<| |~"
    ]
  }
}

### Dynamic Command Building

```json
{
  "config": {
    "cmd": ["echo"],
    "args": ["'Hello World'"]
  },
  "run": [
    "~| (> config.cmd[0].|>&=<|, config.args[0].|>&=<| <) |~"
  ]
}
```

Builds and executes: `echo 'Hello World'`

---

## Error Handling

**Current Behavior:**
- Shell command failures return error output as string
- Execution continues after errors
- No built-in error catching mechanism (alpha limitation)

**Best Practices:**
- Validate inputs before shell execution
- Check command outputs in subsequent steps
- Use AI models to validate/parse outputs

---

## Notation Summary

| Symbol | Meaning |
|--------|---------|
| `~\| \|~` | Instruction specifier |
| `\|> <\|` | Shell command specifier |
| `(> <)` | Multiple commands → single command |
| `(\|> <\|, \|> <\|)` | Sequential commands in same shell |
| `[..., ...]` | Parallel execution (separate shells) |
| `->` | Assign left to right |
| `<-` | Assign right to left |
| `&#` | Command output |
| `&€` | File content |
| `&=` | JSON value |
| `&¤` | Raw value |
| `$S` | String type |
| `$I` | Integer type |
| `$L` | List type |
| `<$>` | Variable placeholder |
| `<$S>` | String placeholder (in JSON) |
| `<$I>` | Integer placeholder (in JSON) |
| `<$L>` | List placeholder (in JSON) |
| `[N<$>]` | Save to array index N |
| `[<$>]` | Variable array index access |
| `VAR&` | Custom variable |
| `&V` | Value entry |
| `&S` | Script entry |
| `&F` | Function entry |
| `A&` | AI variable |
| `&I` | AI Input |
| `&O` | AI Output |
| `&M` | AI Model |
| `;` | Built-in function separator |

---

**For tutorials and real-world examples, see [TUTORIAL.md](TUTORIAL.md) and [EXAMPLES.md](EXAMPLES.md).**
