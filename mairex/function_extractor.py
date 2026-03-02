import lizard
from whats_that_code.election import guess_language_all_methods

_LANG_MAP = {
    "python":      ".py",
    "javascript":  ".js",
    "delphi":      ".js",
    "typescript":  ".ts",
    "C":           ".c",
    "C++":         ".cpp",
    "Java":        ".java",
    "Go":          ".go",
    "Rust":        ".rs",
    "Ruby":        ".rb",
    "PHP":         ".php",
    "Kotlin":      ".kt",
    "Swift":       ".swift",
    "Bash":        ".sh",
    "C#":          ".cs",
}

def extract_functions(source: str, out_function: str) -> dict:
    prog_lang = guess_language_all_methods(source)
    try:
    	prog_lang_ext = _LANG_MAP.get(prog_lang)
    except:
    	print(
    	    f"Detected language {prog_lang} has no supported file extension"
    	    f"Supported: {list(_LANG_MAP.values())}"
    	)
    	return "Function extraction failed"
    
    if prog_lang_ext is None:
        print(
            f"Detected language '{prog_lang_ext}' is not supported. "
            f"Supported: {list(_LANG_MAP.keys())}"
        )
        return "Function extraction failed"
        
    analysis = lizard.analyze_file.analyze_source_code(f"script{prog_lang_ext}", source)
    results = {}
    source_lines = source.splitlines()
    
    for func in analysis.function_list:
        # Lizard provides 1-based line numbers, so we adjust for 0-based indexing
        start_line = func.start_line
        end_line = func.end_line
        
        # Extract the specific lines for this function
        function_body = "\n".join(source_lines[start_line:end_line])
        results[func.name + "()"] = function_body
    return results[out_function]
