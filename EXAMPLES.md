# Mairex Examples

Real-world use cases demonstrating the power of Mairex orchestration.

## Table of Contents

1. [Web Scraping & AI Analysis](#1-web-scraping--ai-analysis)
2. [Multi-Model AI Comparison](#2-multi-model-ai-comparison)
3. [Automated Report Generation](#3-automated-report-generation)
4. [Code Analysis Pipeline](#4-code-analysis-pipeline)
5. [Data Processing & Transformation](#5-data-processing--transformation)
6. [Automated Testing & Documentation](#6-automated-testing--documentation)
7. [System Monitoring & Alerts](#7-system-monitoring--alerts)
8. [Batch File Processing](#8-batch-file-processing)
9. [Parameterized Scripts with Script-Level Arguments](#9-parameterized-scripts-with-script-level-arguments)

---

## 1. Web Scraping & AI Analysis

**Use Case:** Download multiple websites, extract specific information with different AI models, and organize results.

```json
{
  "websites": {
    "wget": [
      "https://news.ycombinator.com",
      "https://techcrunch.com",
      "https://arstechnica.com"
    ],
    "-O": [
      "hn.html",
      "tc.html",
      "ars.html"
    ]
  },
  "download": {
    "fetch_pages": [
      "~| (> websites.|>wget<|[0].|>&=<|, websites.|>-O<|[0].|>&=<| <) |~",
      "~| (> websites.|>wget<|[1].|>&=<|, websites.|>-O<|[1].|>&=<| <) |~",
      "~| (> websites.|>wget<|[2].|>&=<|, websites.|>-O<|[2].|>&=<| <) |~"
    ]
  },
  "analyze": {
    "setup_models": [
      "(~| A&M <&¤S- 'llama3:latest' |~, ~| A&P <&¤S- 'Extract all article titles as a JSON list' |~)",
      "(~| A&M <&¤S- 'qwen3:4b' |~, ~| A&P <&¤S- 'Extract main topics discussed' |~)",
      "(~| A&M <&¤S- 'wizardlm2:7b' |~, ~| A&P <&¤S- 'Summarize top 3 stories' |~)"
    ],
    "process_pages": [
      "~| A&I <&€- hn.html |~",
      "~| A&I <&€- tc.html |~",
      "~| A&I <&€- ars.html |~"
    ],
    "save_results": [
      "~| A&O -€S> hn_titles.json |~",
      "~| A&O -€S> tc_topics.txt |~",
      "~| A&O -€S> ars_summary.txt |~"
    ]
  },
  "organize": {
    "create_dir": [
      "~| |>mkdir -p analysis_results<| |~"
    ],
    "move_files": [
      "~| |>mv *.json *.txt analysis_results/<| |~"
    ]
  }
}
```

**What this does:**
- Downloads 3 different news sites in parallel
- Processes each with a different AI model (also in parallel)
- Each AI has a different extraction task
- Organizes all results into a folder

**Time saved:** ~40 lines instead of 240+ in Python/JavaScript

---

## 2. Multi-Model AI Comparison

**Use Case:** Compare how different AI models respond to the same prompt.

```json
{
  "test": {
    "question": [
      "~| Q&V <&¤S- 'Explain quantum entanglement in simple terms' |~"
    ]
  },
  "models": {
    "configure": [
      "(~| A&S <&¤S- 'ollama' |~, ~| A&M <&¤S- 'llama3' |~)",
      "(~| A&S <&¤S- 'openai' |~, ~| A&M <&¤S- 'gpt-4o' |~)",
      "(~| A&S <&¤S- 'anthropic' |~, ~| A&M <&¤S- 'claude-3-5-sonnet-20241022' |~)",
      "(~| A&S <&¤S- 'gemini' |~, ~| A&M <&¤S- 'gemini-2.5-pro' |~)"
    ],
    "ask_all": [
      "~| A&I <S- Q&V |~",
      "~| A&I <S- Q&V |~",
      "~| A&I <S- Q&V |~",
      "~| A&I <S- Q&V |~"
    ],
    "save_responses": [
      "~| A&O -€S> llama3_response.txt |~",
      "~| A&O -€S> gpt4_response.txt |~",
      "~| A&O -€S> claude_response.txt |~",
      "~| A&O -€S> qwen_response.txt |~"
    ]
  },
  "compare": {
    "create_report": [
      "~| |>echo '=== Llama3 ===' > comparison.txt && cat llama3_response.txt >> comparison.txt<| |~"
    ],
    "append_others": [
      "(~| |>echo '=== GPT-4 ===' >> comparison.txt<| |~, ~| |>cat gpt4_response.txt >> comparison.txt<| |~)"
    ],
    "finalize": [
      "(~| |>echo '=== Claude ===' >> comparison.txt<| |~, ~| |>cat claude_response.txt >> comparison.txt<| |~, ~| |>echo '=== Qwen ===' >> comparison.txt<| |~, ~| |>cat qwen_response.txt >> comparison.txt<| |~)"
    ]
  }
}
```

**Result:** Single file comparing 4 different AI model responses side-by-side.

---

## 3. Code Analysis Pipeline

**Use Case:** Analyze source code files, extract functions, document them with AI.

```json
{
  "load_source_files": [
    "~| MAIN&S <&€- src/main.py |~",
    "~| UTILS&S <&€- src/utils.py |~",
    "~| CONFIG&S <&€- src/config.py |~"
  ],
  "extract": {
    "functions": {
      "main_funcs": [
        "MAIN&F ; main()",
        "MAIN&F ; init()"
      ],
      "util_funcs": [
        "UTILS&F ; parse_data()",
        "UTILS&F ; validate_input()"
      ],
      "setup_ai": [
      "(~| A&M <&¤S- 'gpt-4o' |~, ~| A&S <&¤S- 'openai' |~, ~| A&P <&¤S- 'Generate detailed documentation for this function including parameters, return values, and example usage' |~)",
      "(~| A&M <&¤S- 'gpt-4o' |~, ~| A&S <&¤S- 'openai' |~, ~| A&P <&¤S- 'Generate detailed documentation for this function including parameters, return values, and example usage' |~)"
      ],
      "process_funcs": [
      "~| A&I <&#- (> |>echo<|, extract.functions.main_funcs[0].|>&=<| <) |~",
      "~| A&I <&#- (> |>echo<|, extract.functions.util_funcs[0].|>&=<| <) |~"
      ],
      "save_docs": [
      "~| A&O -€S> docs/main_function.md |~",
      "~| A&O -€S> docs/parse_data_function.md |~"
      ]
  }
  }
}
```

**What this does:**
- Loads multiple Python source files
- Extracts specific functions
- AI generates documentation for each
- Saves as markdown files

**Use case:** Automated documentation generation

---

## 4. Data Processing & Transformation

**Use Case:** Download CSV data, transform it, analyze with AI, export results.

```json
{
  "data": {
    "download": [
      "~| |>wget https://example.com/sales_data.csv -O raw_data.csv<| |~"
    ],
    "transform": [
      "~| |>awk -F',' '{print $1,$3,$5}' raw_data.csv > filtered_data.csv<| |~"
    ],
    "analyze": {
      "setup": [
        "(~| A&M <&¤S- 'llama3' |~, ~| A&P <&¤S- 'Analyze this sales data and provide: 1) Total revenue, 2) Top product, 3) Growth trend, 4) Recommendations' |~)"
      ],
      "process": [
        "~| A&I <&€- filtered_data.csv |~"
      ],
      "results": [
        "~| A&O -€S> sales_analysis.txt |~"
      ]
    },
    "visualize": {
      "create_chart": [
        "~| |>gnuplot -e \"set term png; set output 'chart.png'; plot 'filtered_data.csv' with lines\"<| |~"
      ]
    },
    "report": {
      "combine": [
        "~| |>echo '# Sales Report' > final_report.md<| |~"
      ],
      "add_analysis": [
        "~| (|>echo '## Analysis' >> final_report.md<|, |>cat sales_analysis.txt >> final_report.md<|) |~"
      ],
      "add_chart": [
        "~| |>echo '![Chart](chart.png)' >> final_report.md<| |~"
      ]
    }
  }
}
```

**Result:** Complete data analysis pipeline with AI insights and visualization

---

## 5. Automated Testing & Documentation

**Use Case:** Run tests, analyze failures with AI, generate bug reports.

```json
{
  "testing": {
    "run_tests": [
      "~| |>pytest tests/ -v<| -&#> TEST_OUTPUT&V |~"
    ],
    "save_log": [
      "~| TEST_OUTPUT&V -€S> test_results.log |~"
    ]
  },
  "analysis": {
    "check_failures": [
      "~| |>grep -i 'FAILED' test_results.log<| -&#> FAILURES&V |~"
    ],
    "ai_analyze": {
      "setup": [
        "(~| A&M <&¤S- 'gpt-4o' |~, ~| A&S <&¤S- 'openai' |~, ~| A&P <&¤S- 'Analyze these test failures and provide: 1) Root cause, 2) Affected components, 3) Suggested fixes, 4) Priority level' |~)"
      ],
      "process": [
        "~| A&I <&€- test_results.log |~"
      ],
      "report": [
        "~| A&O -€S> bug_report.md |~"
      ]
    }
  },
  "notify": {
    "send_alert": [
      "~| |>curl -X POST https://slack.webhook.url -d @bug_report.md<| |~"
    ]
  }
}
```

**Perfect for:** CI/CD pipelines with intelligent failure analysis

---

## 6. System Monitoring & Alerts

**Use Case:** Monitor system resources, detect anomalies with AI, send alerts.

```json
{
  "monitor": {
    "collect_metrics": [
      "~| |>top -b -n 1 | head -20<| -&#€S> metrics_snapshot.txt |~",
      "~| |>ps aux --sort=-%mem | head -10<| -&#€S> memory_hogs.txt |~",
      "~| |>netstat -tuln | grep LISTEN<| -&#€S> open_ports.txt |~"
    ]
  },
  "analyze": {
    "ai_check": {
      "setup": [
        "(~| A&M <&¤S- 'llama3' |~, ~| A&P <&¤S- 'Analyze these system metrics. Report any anomalies: high CPU (>80%), high memory (>90%), unexpected processes, or unusual network activity. Format as: ALERT or OK, then details.' |~)"
      ],
      "combine_data": [
        "~| |>cat metrics_snapshot.txt memory_hogs.txt open_ports.txt<| -&#$S> ALL_METRICS&V |~"
      ],
      "process": [
        "~| A&I <$S- ALL_METRICS&V |~"
      ],
      "save": [
        "~| A&O -€S> health_status.txt |~"
      ]
    }
  },
  "alert": {
    "check_status": [
      "~| |>grep -q 'ALERT' health_status.txt && mail -s 'System Alert' admin@example.com < health_status.txt<| |~"
    ]
  }
}
```

**Use case:** Cron job running every 15 minutes for intelligent monitoring

---

## Advanced Example: Complete Blog Post Generator

**Use Case:** Research topic, gather sources, generate content with AI, format as blog post.

```json
{
  "config": {
    "topic": ["Quantum Computing Applications"],
    "sources": [
      "https://quantum-journal.org/article1",
      "https://science-blog.com/quantum",
      "https://tech-news.com/qc-latest"
    ]
  },
  "research": {
    "download_sources": [
      "~| config.sources[0].&= -$S> |>wget '<$>' -O source1.html<| |~",
      "~| config.sources[1].&= -$S> |>wget '<$>' -O source2.html<| |~",
      "~| config.sources[2].&= -$S> |>wget '<$>' -O source3.html<| |~"
    ],
    "extract_text": [
      "~| |>lynx -dump source1.html<| -&#€S> text1.txt |~",
      "~| |>lynx -dump source2.html<| -&#€S> text2.txt |~",
      "~| |>lynx -dump source3.html<| -&#€S> text3.txt |~"
    ]
  },
  "analyze": {
    "summarize": {
      "setup": [
        "(~| A&M <&¤S- 'gpt-4o' |~, ~| A&S <&¤S- 'openai' |~, ~| A&P <&¤S- 'Summarize key points about quantum computing applications from this source' |~)",
        "(~| A&M <&¤S- 'gpt-4o' |~, ~| A&S <&¤S- 'openai' |~, ~| A&P <&¤S- 'Summarize key points about quantum computing applications from this source' |~)",
        "(~| A&M <&¤S- 'gpt-4o' |~, ~| A&S <&¤S- 'openai' |~, ~| A&P <&¤S- 'Summarize key points about quantum computing applications from this source' |~)"
      ],
      "process": [
        "~| A&I <&€- text1.txt |~",
        "~| A&I <&€- text2.txt |~",
        "~| A&I <&€- text3.txt |~"
      ],
      "save": [
        "~| A&O -€S> summary1.txt |~",
        "~| A&O -€S> summary2.txt |~",
        "~| A&O -€S> summary3.txt |~"
      ]
    }
  },
  "generate": {
    "combine_summaries": [
      "~| |>cat summary1.txt summary2.txt summary3.txt<| -&#€S> all_summaries.txt |~"
    ],
    "write_post": {
      "setup": [
        "(~| A&M <&¤S- 'gpt-4o' |~, ~| A&S <&¤S- 'openai' |~, ~| A&P <&¤S- 'Write a comprehensive 1000-word blog post about Quantum Computing Applications. Use these summaries as sources. Include: introduction, 3 main sections, conclusion, and suggest 5 SEO keywords.' |~)"
      ],
      "process": [
        "~| A&I <&€- all_summaries.txt |~"
      ],
      "save": [
        "~| A&O -€S> blog_draft.md |~"
      ]
    }
  },
  "polish": {
    "proofread": {
      "setup": [
        "(~| A&M <&¤S- 'claude-3-5-sonnet-20241022' |~, ~| A&S <&¤S- 'anthropic' |~, ~| A&P <&¤S- 'Proofread this blog post. Fix grammar, improve clarity, ensure professional tone. Return the corrected version.' |~)"
      ],
      "process": [
        "~| A&I <&€- blog_draft.md |~"
      ],
      "final": [
        "~| A&O -€S> blog_final.md |~"
      ]
    }
  },
  "publish": {
    "preview": [
      "~| |>pandoc blog_final.md -o blog_final.html<| |~"
    ],
    "notify": [
      "~| |>echo 'Blog post ready for review: blog_final.html'<| |~"
    ]
  }
}
```

**Result:** Fully automated blog post generation from research to final draft!

---

## 9. Parameterized Scripts with Script-Level Arguments

**Use Case:** Build reusable scripts that accept runtime parameters from the command line instead of hardcoding values.

### Reusable AI Analyzer

Invoke with a file to analyze and the AI model to use:

```bash
mairex analyze.jsom report.txt llama3
```

```json
{
  "args": {
    "file": ["<ł[0]S>"],
    "model": ["<ł[1]S>"]
  },
  "analyze": {
    "setup": [
      "(~| A&M <S- args.model[0].&= |~, ~| A&P <&¤S- 'Summarize this document concisely' |~)"
    ],
    "load": [
      "~| (> |>echo<|, args.file[0].|>&=<| <) -&#S> A&I |~"
    ],
    "save": [
      "~| A&O -€S> summary.txt |~"
    ]
  }
}
```

- `args.file` → `report.txt` (file to analyze)
- `args.model` → `llama3` (model to use)

## Tips for Complex Workflows

### 1. Use JSON Structure for Configuration

Store reusable data at the top:

```json
{
  "config": {
    "api_endpoint": ["https://api.example.com"],
    "models": ["llama3", "gpt-4o", "claude-3-5-sonnet-20241022"]
  }
}
```

### 2. Leverage Parallel Execution

Each array index = independent shell = parallelism:

```json
{
  "parallel_tasks": [
    "~| |>heavy_task_1<| |~",
    "~| |>heavy_task_2<| |~",
    "~| |>heavy_task_3<| |~"
  ]
}
```

### 3. Chain Operations Efficiently

```json
["~| source -&€> VAR1&V -S> VAR2&V -€S> destination |~"]
```

### 4. Use AI for Complex Parsing

Instead of complex regex/awk scripts, let AI parse:

```json
{
  "parse": {
    "ai": [
      "(~| A&P <&¤S- 'Extract all email addresses as JSON array' |~, ~| A&I <&€- messy_data.txt |~, ~| A&O -€S> emails.json |~)"
    ]
  }
}
```

---

## Performance Considerations

**Parallel AI Calls:**
- Each array element runs independently
- 10 AI calls in 10 array elements = parallel execution
- Much faster than sequential

**Shell Session Persistence:**
- Shells stay alive throughout execution
- No overhead from spawning new shells each time

**Variable Sharing:**
- Custom variables shared = no data duplication
- AI variables isolated = no cross-contamination

---

**For syntax details, see [SYNTAX_REFERENCE.md](SYNTAX_REFERENCE.md)**

**For learning basics, see [TUTORIAL.md](TUTORIAL.md)**
