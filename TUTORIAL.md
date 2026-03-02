# Mairex Tutorial

Learn Mairex step-by-step, from basic concepts to advanced orchestration patterns.

## Prerequisites

- Basic understanding of JSON
- Familiarity with terminal/shell commands
- Python 3.8+ installed
- Mairex installed (`pip install mairex`)

---

## Chapter 1: Your First JSOM File

### Lesson 1.1: Hello World

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

**Output:** `Hello, Mairex!`

**What happened:**
1. Mairex parsed the JSON structure
2. Found instruction `~| ... |~`
3. Found shell command `|>echo 'Hello, Mairex!'<|`
4. Executed `echo 'Hello, Mairex!'` in shell
5. Printed the result

**Key concepts:**
- `~| |~` marks an instruction
- `|> <|` marks a shell command
- All values must be in arrays

---

### Lesson 1.2: Multiple Commands

Create `multi.jsom`:

```json
{
  "commands": {
    "list_and_date": [
      "~| |>pwd<| |~",
      "~| |>date<| |~",
      "~| |>echo 'Done'<| |~"
    ]
  }
}
```

Run it:
```bash
mairex multi.jsom
```

**What happened:**
- Three commands executed in **three separate shell sessions**
- Array index 0: `pwd` (Shell 0)
- Array index 1: `date` (Shell 1)
- Array index 2: `echo 'Done'` (Shell 2)

**Important:** Each array element = separate shell!

---

### Lesson 1.3: Sequential Commands in Same Shell

Create `sequence.jsom`:

```json
{
  "workflow": {
    "navigate": [
      "~| (|>cd /tmp<|, |>pwd<|, |>ls<|) |~"
    ]
  }
}
```

**What happened:**
- All commands run in **Shell 0**
- `cd /tmp` changes directory
- `pwd` shows `/tmp` (because same shell)
- `ls` lists files in `/tmp`

**Key concept:** Parentheses with commas = same shell, sequential execution

---

## Chapter 2: Variables

### Lesson 2.1: Creating Variables

Create `variables.jsom`:

```json
{
  "test": {
    "create_var": [
      "~| MESSAGE&V <&¤S- 'Hello from variable' |~"
    ],
    "use_var": [
      "~| MESSAGE&V -$S> |>echo '<$>'<| |~"
    ]
  }
}
```

**Breakdown:**
1. `MESSAGE&V <&¤S- 'Hello from variable'`
   - `MESSAGE&V` = variable named MESSAGE, entry V (value)
   - `<&¤S-` = assign raw string from right
   - `'Hello from variable'` = the value
2. `MESSAGE&V -$S> |>echo '<$>'<|`
   - `MESSAGE&V -$S>` = pass MESSAGE value as string to right
   - `<$>` = placeholder where value goes
   - Result: `echo 'Hello from variable'`

**Output:** `Hello from variable`

---

### Lesson 2.2: Variable Scope (Shared Across Shells)

Create `shared_vars.jsom`:

```json
{
  "sharing": {
    "set_and_use": [
      "~| SHARED&V <&¤S- 'I am shared!' |~",
      "~| SHARED&V -$S> |>echo 'Shell 1 sees: <$>'<| |~",
      "~| SHARED&V -$S> |>echo 'Shell 2 sees: <$>'<| |~"
    ]
  }
}
```

**Output:**
```
Shell 1 sees: I am shared!
Shell 2 sees: I am shared!
```

**Key concept:** Custom variables are shared across all shells in same function

---

### Lesson 2.3: Different Variable Types

Create `types.jsom`:

```json
{
  "types": {
    "create": [
      "~| STR&V <&¤S- 'text' |~",
      "~| NUM&V <&¤I- 42 |~",
      "~| LST&V <&¤L- ['a', 'b', 'c'] |~"
    ],
    "use": [
      "~| STR&V -$S> |>echo 'String: <$>'<| |~",
      "~| NUM&V -$I> |>echo 'Number: <$>'<| |~",
      "~| LST&V -$L> |>echo 'List: <$>'<| |~"
    ]
  }
}
```

**Output:**
```
String: text
Number: 42
List: ['a', 'b', 'c']
```

**Type specifiers:**
- `S` = String
- `I` = Integer
- `L` = List

---

## Chapter 3: Data Flow and Assignments

### Lesson 3.1: Capturing Command Output

Create `capture.jsom`:

```json
{
  "capture": {
    "get_date": [
      "~| |>date<| -&#> CURRENT_TIME&V |~"
    ],
    "show_date": [
      "~| CURRENT_TIME&V -$S> |>echo 'The time was: <$>'<| |~"
    ]
  }
}
```

**Breakdown:**
- `|>date<| -&#> CURRENT_TIME&V`
  - `-&#>` = capture command output, assign right
  - Command output goes into `CURRENT_TIME&V`

**Output:** `The time was: [current date/time]`

---

### Lesson 3.2: Chained Assignments

Create `chain.jsom`:

```json
{
  "chain": {
    "left_to_right": [
      "~| |>echo 'original'<| -&#> VAR1&V -S> VAR2&V -$S> |>echo 'Final: <$>'<| |~"
    ]
  }
}
```

**Flow:**
1. `echo 'original'` outputs "original"
2. Output goes to `VAR1&V` (as string)
3. `VAR1&V` value goes to `VAR2&V` as string
4. `VAR2&V` value goes to echo command
5. Result: `echo 'Final: original'`

**Output:** `Final: original`

---

### Lesson 3.3: Right to Left Assignment

Create `reverse.jsom`:

```json
{
  "reverse": {
    "right_to_left": [
      "~| |>echo '<$>'<| <$S- RESULT&V <&#- |>date<| |~"
    ]
  }
}
```

**Flow (right to left):**
1. `|>date<|` executes
2. `<&#-` captures output
3. Output goes to `RESULT&V`
4. `<$S-` passes RESULT value as string left
5. Value fills `<$>` in echo command

**Same result, different syntax!**

---

## Chapter 4: File Operations

### Lesson 4.1: Reading Files

Create `input.txt`:
```
This is test content
```

Create `read_file.jsom`:
```json
{
  "read": {
    "load_content": [
      "~| CONTENT&V <&€- input.txt |~"
    ],
    "display": [
      "~| CONTENT&V -$S> |>echo '<$>'<| |~"
    ]
  }
}
```

**Breakdown:**
- `<&€-` = read file content from right
- `input.txt` → `CONTENT&V`

**Output:** `This is test content`

---

### Lesson 4.2: Writing Files

Create `write_file.jsom`:

```json
{
  "write": {
    "create": [
      "~| |>date<| -&#€> timestamp.txt |~"
    ],
    "verify": [
      "~| |>cat timestamp.txt<| |~"
    ]
  }
}
```

**Breakdown:**
- `-&#€>` = capture command output and write to file
- `date` output → `timestamp.txt`

**Result:** Creates `timestamp.txt` with current date

---

### Lesson 4.3: File Pipeline

Create `pipeline.jsom`:

```json
{
  "pipeline": {
    "process": [
      "~| source.txt <&€- TEMP&V <&#- |>echo 'Processed data'<| |~"
    ]
  }
}
```

**Flow (right to left):**
1. `echo 'Processed data'` runs
2. Output captured to `TEMP&V`
3. `TEMP&V` written to `source.txt`

**Result:** `source.txt` contains "Processed data"

---

## Chapter 5: JSON Data Access

### Lesson 5.1: Reading JSON Values

Create `json_read.jsom`:

```json
{
  "data": {
    "commands": [
      "ls",
      "pwd"
    ]
  },
  "commands": {
    "show_url": [
      "~| data.commands[0].|>&=<| |~"
    ]
  }
}
```

**Breakdown:**
- `data.commands[0].&=` = access JSON path
- `.&=` = extract value at this path
- Value: `ls`
- `|>&=<| = runs value at this path as a shell command`

**Output:** `<content of the directory>`

---

### Lesson 5.2: Dynamic Array Access

Create `dynamic_json.jsom`:

```json
{
  "items": ["date", "pwd", "ls"],
  "access": {
    "dynamic": [
      "~| 1 -&¤I$> items[<$>].|>&=<| |~"
    ]
  }
}
```

**Flow:**
1. `1 -&¤I$>` = pass raw integer 1
2. `items[<$>]` = `<$>` becomes `1`
3. Access `items[1]` = "pwd"
4. |>&=<| runs "pwd" in the shell

**Output:** `/home/...`

---

### Lesson 5.3: Saving to JSON

Create `json_save.jsom`:

```json
{
  "process": {
    "results": ["<$S>"],
    "save": [
      "~| |>echo 'pwd'<| -&#$S> process.results[0<$>].|>&=<| |~"
    ]
  }
}
```

**Breakdown:**
- `results[0<$>].&=` = save to results[0]
- `<$S>` placeholder in JSON = can receive string
- Command output saved back to JSON structure

Output: `pwd`  `/home/...`
---

## Chapter 6: AI Integration

### Lesson 6.1: First AI Call (Using Ollama)

**Prerequisites:**
1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama3`

Create `ai_hello.jsom`:

```json
{
  "ai": {
    "setup": [
      "(~| A&M <&¤S- 'llama3:latest' |~, ~| A&S <&¤S- 'ollama' |~, ~| A&P <&¤S- 'Be concise' |~)"
    ],
    "input": [
      "~| A&I <&¤S- 'What is 2+2?' |~"
    ],
    "output": [
      "~| A&O -$S> |>echo '<$>'<| |~"
    ]
  }
}
```

**Breakdown:**
1. `A&M` = Model: llama3:latest
2. `A&S` = Service: ollama
3. `A&P` = Prompt: Be concise
4. `A&I` = Input: What is 2+2?
5. `A&O` = Triggers AI call, captures output

**Output:** AI response (e.g., "4" or "2+2 equals 4")

---

### Lesson 6.2: AI with File Input

Create `ai_file.jsom`:

```json
{
  "analyze": {
    "setup": [
      "(~| A&M <&¤S- 'llama3:latest' |~, ~| A&P <&¤S- 'Summarize this text in one sentence' |~)"
    ],
    "load": [
      "~| A&I <&€- document.txt |~"
    ],
    "result": [
      "~| A&O -€S> summary.txt |~"
    ]
  }
}
```

**Flow:**
(Without specifing the service mairex will default to ollama)
1. Setup AI with llama3 and summarization prompt
2. Load `document.txt` content into AI input
3. AI processes
4. Save AI output to `summary.txt`

---

### Lesson 6.3: Multiple AI Models in Parallel

Create `multi_ai.jsom`:

```json
{
  "parallel_ai": {
    "configure": [
      "(~| A&M <&¤S- 'llama3' |~, ~| A&P <&¤S- 'Extract names' |~)",
      "(~| A&M <&¤S- 'qwen3:4b' |~, ~| A&P <&¤S- 'Extract dates' |~)",
      "(~| A&M <&¤S- 'wizardlm2:7b' |~, ~| A&P <&¤S- 'Extract locations' |~)"
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

**What happened:**
- 3 separate shells (array indices 0, 1, 2)
- Each shell has independent AI configuration
- All run in parallel
- Each produces different output file

**Result:** Three files with different extracted data

---

### Lesson 6.4: Using Cloud AI (OpenAI/Anthropic/etc.)

Create `API_keys.json` in your working directory:

```json
{
  "openai": "sk-your-key-here",
  "anthropic": "",
  "gemini": "",
  "xai": ""
}
```

Create `cloud_ai.jsom`:

```json
{
  "gpt": {
    "setup": [
      "(~| A&S <&¤S- 'openai' |~, ~| A&M <&¤S- 'gpt-4o' |~, ~| A&P <&¤S- 'You are helpful' |~)"
    ],
    "input": [
      "~| A&I <&¤S- 'Explain quantum computing' |~"
    ],
    "output": [
      "~| A&O -€S> explanation.txt |~"
    ]
  }
}
```

**Note:** Mairex uses LiteLLM, supporting:
- OpenAI (gpt-4o, gpt-4, gpt-3.5-turbo, etc.)
- Anthropic (claude-3-5-sonnet-20241022, etc.)
- Google (gemini-pro, etc.)
- XAI (grok-beta, etc.)

---

## Chapter 7: Advanced Patterns

### Lesson 7.1: Building Commands Dynamically

Create `dynamic_cmd.jsom`:

```json
{
  "config": {
    "base_cmd": ["wget"],
    "url": ["https://example.com"],
    "output": ["-O page.html"]
  },
  "download": {
    "run": [
      "~| (> config.base_cmd[0].|>&=<|, config.url[0].|>&=<|, config.output[0].|>&=<| <) |~"
    ]
  }
}
```

**Result:** Executes `wget https://example.com -O page.html`

**Key concept:** `(> <)` concatenates into single command

---

### Lesson 7.2: Function Extraction

Create `script.py`:
```python
def greet(name):
    return f"Hello, {name}!"

def farewell(name):
    return f"Goodbye, {name}!"
```

Create `extract_func.jsom`:

```json
{
  "scripts": {
    "load": [
      "~| MYSCRIPT&S <&€- script.py |~"
    ],
    "functions": [
      "ID_0",
      "MYSCRIPT&F ; greet()",
      "MYSCRIPT&F ; farewell()"
    ],
    "show": [
      "~| (> |>echo '<|, scripts.functions[1].|>&=<|, |>'<| <) |~",
      "~| (> |>echo '<|, scripts.functions[2].|>&=<|, |>'<| <) |~"
    ]
  }
}
```

**What happened:**
1. Load `script.py` into `MYSCRIPT&S`
2. Extract `greet()` function → replaces `scripts.functions[1]`
3. Extract `farewell()` function → replaces `scripts.functions[2]`
4. Echo both functions (shows their code)

---

### Lesson 7.3: Complete AI + Shell Pipeline

Create `full_pipeline.jsom`:

```json
{
  "pipeline": {
    "download": [
      "~| |>wget https://example.com -O page.html<| |~"
    ],
    "analyze": {
      "setup": [
        "(~| A&M <&¤S- 'llama3' |~, ~| A&P <&¤S- 'Extract all email addresses without explanation' |~)"
      ],
      "process": [
        "~| A&I <&€- page.html |~"
      ],
      "save": [
        "~| A&O -€S> emails.txt |~"
      ]
    },
    "verify": [
      "~| |>cat emails.txt<| |~"
    ]
  }
}
```

**Flow:**
1. Download webpage
2. Configure AI to extract emails
3. Load webpage as AI input
4. Save AI output to emails.txt
5. Display emails.txt

**Real-world use case!**

---
## Next Steps

You've completed the tutorial! You now understand:
- ✅ JSOM file structure
- ✅ Instructions and shell commands
- ✅ Variables and scoping
- ✅ Data flow and assignments
- ✅ File operations
- ✅ JSON data access
- ✅ AI model integration
- ✅ Advanced patterns

### Continue Learning:
- **[SYNTAX_REFERENCE.md](SYNTAX_REFERENCE.md)** - Complete language specification
- **[EXAMPLES.md](EXAMPLES.md)** - Real-world use cases
- **Experiment** - Build your own orchestrations!

---

## Troubleshooting

### Command Not Found
```
Error: mairex: command not found
```

**Solution:** Reinstall with `pip install mairex` or use `python3 comp.py yourfile.jsom`

---

### Syntax Error
```
SyntaxError: Unfinished |> command specifier
```

**Solution:** Check that all `|>` have matching `<|`

---

### Shell Died
```
RuntimeError: Shell died! Exit code: 127
```

**Solution:** The shell command doesn't exist or has syntax error. Verify command works in terminal first.

---

### AI Model Not Found
```
AttributeError: The model to set llama3 could not be found
```

**Solution:**
- For Ollama: `ollama pull llama3`
- For cloud: Check model name spelling

---

### File Not Found
```
RuntimeError: The file specified in: data.txt can't be found
```

**Solution:** File paths are relative to execution directory. Use absolute paths or verify file location.

---

**Happy orchestrating! 🚀**
