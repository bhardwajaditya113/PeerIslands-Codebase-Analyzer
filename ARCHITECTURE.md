# Architecture Diagrams

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION                          │
│                                                                   │
│  Command Line Interface                                          │
│  $ python main.py [--skip-clone] [--output-file FILE]           │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MAIN CONTROLLER                             │
│                         (main.py)                                │
│                                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Step 1  │  │  Step 2  │  │  Step 3  │  │  Step 4  │        │
│  │  Clone   │→ │   Read   │→ │ Analyze  │→ │  Format  │        │
│  │   Repo   │  │  Files   │  │   Code   │  │  Output  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└────────────────────────────┬─────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Repository  │      │    Code     │      │   Output    │
│  Manager    │      │  Analyzer   │      │  Formatter  │
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │                    │                    │
       │                    │                    │
       ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Chunker   │      │     LLM     │      │    JSON     │
│             │      │  Provider   │      │    File     │
└─────────────┘      └──────┬──────┘      └─────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │  LangChain  │
                     └──────┬──────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
         ┌─────────────┐        ┌─────────────┐
         │   OpenAI    │        │  Anthropic  │
         │   GPT-4     │        │   Claude    │
         └─────────────┘        └─────────────┘
```

## Data Flow

```
INPUT STAGE
───────────
GitHub URL
    │
    ▼
┌─────────────────┐
│ Git Clone/Pull  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Local Directory │
│  data/repo/     │
└────────┬────────┘

PROCESSING STAGE
────────────────
         │
         ▼
┌─────────────────────────┐
│ File Filtering          │
│ • Extension check       │
│ • Directory exclusion   │
│ • Encoding detection    │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Code Files              │
│ [File1, File2, ...]     │
└────────┬────────────────┘
         │
         ├─────────────────────────┐
         │                         │
         ▼                         ▼
┌──────────────────┐      ┌─────────────────┐
│ Overview Chunk   │      │ Code Chunks     │
│ • Structure      │      │ • By directory  │
│ • README         │      │ • Token-limited │
└────────┬─────────┘      └────────┬────────┘
         │                         │
         ▼                         ▼
┌──────────────────┐      ┌─────────────────┐
│ LLM Analysis     │      │ LLM Analysis    │
│ • Purpose        │      │ • Classes       │
│ • Architecture   │      │ • Methods       │
│ • Technologies   │      │ • Patterns      │
└────────┬─────────┘      └────────┬────────┘
         │                         │
         └────────────┬────────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Merge Results   │
             └────────┬────────┘
                      │
                      ├─────────────────┐
                      │                 │
                      ▼                 ▼
            ┌──────────────┐   ┌──────────────┐
            │ Complexity   │   │   Method     │
            │  Analysis    │   │ Signatures   │
            │   (Radon)    │   │   (Regex)    │
            └──────┬───────┘   └──────┬───────┘
                   │                  │
                   └────────┬─────────┘

OUTPUT STAGE
────────────
                   │
                   ▼
          ┌──────────────────┐
          │ Format Results   │
          │ • Structure JSON │
          │ • Generate text  │
          └────────┬─────────┘
                   │
                   ├──────────────────┐
                   │                  │
                   ▼                  ▼
         ┌──────────────────┐  ┌──────────────────┐
         │   JSON Output    │  │  Text Summary    │
         │ analysis_*.json  │  │  summary_*.txt   │
         └──────────────────┘  └──────────────────┘
```

## Component Interactions

```
┌──────────────────────────────────────────────────────────────┐
│                         CONFIG MODULE                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ • Load .env file                                       │  │
│  │ • Validate settings with Pydantic                      │  │
│  │ • Provide global config object                         │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────┬──────────────────────────────────┘
                            │ (imported by all modules)
                            │
    ┌───────────────────────┼───────────────────────┐
    │                       │                       │
    ▼                       ▼                       ▼

┌────────────┐      ┌────────────┐      ┌────────────┐
│ Repository │      │   Chunker  │      │    LLM     │
│  Manager   │      │            │      │  Provider  │
└─────┬──────┘      └─────┬──────┘      └─────┬──────┘
      │                   │                   │
      │ provides          │ uses              │ uses
      │ CodeFile[]        │ CodeFile[]        │ text chunks
      │                   │                   │
      └──────────►┌───────▼─────┐◄───────────┘
                  │   Analyzer   │
                  └───────┬──────┘
                          │ produces
                          │ analysis results
                          ▼
                  ┌────────────────┐
                  │ Output         │
                  │ Formatter      │
                  └───────┬────────┘
                          │ writes
                          ▼
                  ┌────────────────┐
                  │  Files         │
                  └────────────────┘
```

## Token Management Flow

```
                    START
                      │
                      ▼
            ┌─────────────────────┐
            │ Get all code files  │
            │ [F1, F2, F3, ...]   │
            └──────────┬──────────┘
                       │
                       ▼
            ┌─────────────────────┐
            │ Sort by directory   │
            │ for better context  │
            └──────────┬──────────┘
                       │
                       ▼
            ┌─────────────────────┐
            │ Initialize:         │
            │ • current_chunk=[]  │
            │ • tokens=0          │
            └──────────┬──────────┘
                       │
                       ▼
            ┌─────────────────────┐
            │ For each file       │
            └──────────┬──────────┘
                       │
                       ▼
            ┌─────────────────────────────┐
            │ Count tokens if file added  │
            │ to current chunk            │
            └──────────┬──────────────────┘
                       │
                  ┌────┴────┐
                  │         │
        ┌─────────▼─────┐   │
        │ Exceeds       │   │
        │ MAX_TOKENS?   │   │
        └────┬────┬─────┘   │
             │    │         │
          YES│    │NO       │
             │    └─────────┤
             │              │
             ▼              ▼
    ┌────────────────┐  ┌─────────────────┐
    │ Finalize       │  │ Add file to     │
    │ current chunk  │  │ current chunk   │
    └────┬───────────┘  └────┬────────────┘
         │                   │
         ▼                   │
    ┌────────────────┐       │
    │ Start new      │       │
    │ chunk with     │       │
    │ current file   │       │
    └────┬───────────┘       │
         │                   │
         └───────────────────┤
                             │
                             ▼
                    ┌────────────────┐
                    │ More files?    │
                    └────┬─────┬─────┘
                         │     │
                      YES│     │NO
                         │     │
                         └─┐   └──┐
                           │      │
                           ▼      ▼
                    ┌──────────────────┐
                    │ Finalize last    │
                    │ chunk            │
                    └────┬─────────────┘
                         │
                         ▼
                    ┌──────────────────┐
                    │ Return chunks    │
                    │ [C1, C2, C3,...] │
                    └──────────────────┘
```

## LLM Analysis Flow

```
         START
           │
           ▼
┌──────────────────────┐
│ Phase 1: Overview    │
│                      │
│ Input: Structure +   │
│        README        │
│                      │
│ Prompt: "What is    │
│ this project?"       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ LLM Response:        │
│ • Project name       │
│ • Purpose            │
│ • Architecture       │
│ • Technologies       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Phase 2: Detailed    │
│                      │
│ For each chunk:      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Chunk N/Total        │
│                      │
│ Input: Code files    │
│                      │
│ Prompt: "Extract     │
│ classes, methods,    │
│ complexity"          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ LLM Response:        │
│ • Classes            │
│ • Methods            │
│ • Relationships      │
│ • Complexity notes   │
└──────────┬───────────┘
           │
           ▼
     [more chunks]
           │
           ▼
┌──────────────────────┐
│ Aggregate Results    │
│                      │
│ Combine all chunk    │
│ analyses             │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Add Metrics          │
│                      │
│ • Radon complexity   │
│ • Method signatures  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Format as JSON       │
└──────────────────────┘
```

## Error Handling Strategy

```
              Operation
                  │
                  ▼
         ┌────────────────┐
         │ Try operation  │
         └────────┬───────┘
                  │
        ┌─────────┴─────────┐
        │                   │
     Success              Error
        │                   │
        ▼                   ▼
┌──────────────┐    ┌──────────────────┐
│ Continue     │    │ Catch exception  │
│ normally     │    └────────┬─────────┘
└──────────────┘             │
                             ▼
                    ┌─────────────────┐
                    │ Log error with  │
                    │ context         │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
              Critical            Non-critical
                    │                 │
                    ▼                 ▼
         ┌───────────────────┐  ┌──────────────┐
         │ Abort with clear  │  │ Skip item    │
         │ error message     │  │ Continue     │
         └───────────────────┘  └──────┬───────┘
                                       │
                                       ▼
                             ┌──────────────────┐
                             │ Include error    │
                             │ info in output   │
                             └──────────────────┘
```

## Configuration Loading

```
    Application Start
            │
            ▼
    ┌────────────────┐
    │ Load .env file │
    └────────┬───────┘
             │
             ▼
    ┌────────────────────────┐
    │ Parse environment vars │
    └────────┬───────────────┘
             │
             ▼
    ┌────────────────────────┐
    │ Create Config object   │
    │ with Pydantic          │
    └────────┬───────────────┘
             │
    ┌────────┴────────┐
    │                 │
 Invalid           Valid
    │                 │
    ▼                 ▼
┌────────────┐  ┌──────────────┐
│ Validation │  │ Config ready │
│ error      │  │ for use      │
│ • Missing  │  └──────────────┘
│   API key  │
│ • Invalid  │
│   value    │
└────────────┘

Example validation:
┌──────────────────────────┐
│ llm_provider = "openai"  │
│          ↓               │
│ Check: must be "openai"  │
│        or "anthropic"    │
│          ↓               │
│ Check: API key present   │
│          ↓               │
│ ✓ Valid                  │
└──────────────────────────┘
```

## Output Generation

```
    Analysis Results
            │
            ▼
    ┌────────────────────┐
    │ Format as          │
    │ structured dict    │
    └────────┬───────────┘
             │
             ▼
    ┌────────────────────┐
    │ Add metadata       │
    │ • Timestamp        │
    │ • Version          │
    │ • Repository info  │
    └────────┬───────────┘
             │
             ▼
    ┌────────────────────┐
    │ Organize sections  │
    │ • Overview         │
    │ • Statistics       │
    │ • Code structure   │
    │ • Complexity       │
    │ • Details          │
    └────────┬───────────┘
             │
             ├──────────────────┐
             │                  │
             ▼                  ▼
    ┌─────────────────┐  ┌──────────────┐
    │ Serialize to    │  │ Generate     │
    │ JSON            │  │ text summary │
    └────────┬────────┘  └──────┬───────┘
             │                  │
             ▼                  ▼
    ┌─────────────────┐  ┌──────────────┐
    │ Pretty print    │  │ Format as    │
    │ with indent=2   │  │ readable     │
    └────────┬────────┘  └──────┬───────┘
             │                  │
             ▼                  ▼
    ┌─────────────────┐  ┌──────────────┐
    │ Save to file    │  │ Save to file │
    │ .json           │  │ .txt         │
    └─────────────────┘  └──────────────┘
```

---

**Legend:**
- `┌─┐ └─┘` : Process/Component boxes
- `│ ─ ┬ ┴ ├ ┤ ┼` : Connections
- `→ ▼ ▲ ◄` : Flow direction
- `[...]` : List/Array
- `...` : More items

---

*These diagrams use ASCII art for universal compatibility*
