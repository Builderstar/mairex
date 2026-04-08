#!/usr/bin/env python3
"""
Mairex CLI - Command-line interface for Mairex orchestration language
"""

import sys
import os

# Add the parent directory to the path to import comp module
# This ensures the module can be run both as installed package and from source
try:
    from mairex.comp import (
        API_Key_load, Script_Load, Jsom_Parse,
        Instruction_Extract, Main
    )
except ImportError:
    # Fallback for development/source installation
    from comp import (
        API_Key_load, Script_Load, Jsom_Parse,
        Instruction_Extract, Main
    )


def main():
    """
    Main entry point for the Mairex CLI.

    Usage:
        mairex <script.jsom>

    Arguments:
        script.jsom: Path to the Mairex JSOM file to execute

    Returns:
        Exit code 0 on success, non-zero on error
    """

    # Check for help flag
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print_help()
        return 0

    # Check for version flag
    if len(sys.argv) > 1 and sys.argv[1] in ['-v', '--version', 'version']:
        print_version()
        return 0

    try:
        Main()
        return 0

    except IndexError as e:
        print(f"Error: {e}")
        print("\nUsage: mairex <script.jsom>")
        print("Try 'mairex --help' for more information.")
        return 1

    except ValueError as e:
        print(f"Error: {e}")
        return 1

    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        return 1

    except RuntimeError as e:
        print(f"Runtime Error: {e}")
        return 1

    except AttributeError as e:
        print(f"Attribute Error: {e}")
        return 1

    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user.")
        return 130

    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def print_help():
    """Print help message"""
    help_text = """
Mairex - A high-level orchestration language for AI models and system commands

USAGE:
    mairex <script.jsom>

ARGUMENTS:
    <script.jsom>    Path to the Mairex JSOM file to execute

OPTIONS:
    -h, --help       Show this help message
    -v, --version    Show version information

EXAMPLES:
    # Run a Mairex script
    mairex workflow.jsom

    # Run with API keys in current directory
    mairex analysis.jsom

DOCUMENTATION:
    For full documentation, visit:
    https://github.com/builderstar/mairex

    Quick start guide: README.md
    Syntax reference: SYNTAX_REFERENCE.md
    Tutorial: TUTORIAL.md
    Examples: EXAMPLES.md

API KEYS:
    To use cloud AI providers (OpenAI, Anthropic, etc.), create an
    API_keys.json file in your working directory:

    {
        "openai": "sk-your-key-here",
        "anthropic": "sk-ant-your-key-here",
        "gemini": "your-gemini-key",
        "xai": "your-xai-key"
    }

    For local AI models, install Ollama: https://ollama.ai
"""
    print(help_text)


def print_version():
    """Print version information"""
    try:
        from mairex import __version__
    except ImportError:
        __version__ = "0.9.2-dev"

    print(f"Mairex version {__version__}")


if __name__ == "__main__":
    sys.exit(main())
