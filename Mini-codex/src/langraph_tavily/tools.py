from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional

from langchain_core.tools import tool

import re
import shlex
import shutil
from groq import Groq


# ============================================================
# WORKING DIRECTORY
# ============================================================

WORK_DIR_RAW = os.getenv("WORK_DIR")

if not WORK_DIR_RAW:
    raise RuntimeError(
        "WORK_DIR is not configured. Add WORK_DIR to your .env file."
    )

WORK_DIR = Path(WORK_DIR_RAW).expanduser().resolve()


# ============================================================
# SECURITY HELPERS
# ============================================================

PROTECTED_FILES = {
    ".env",
}


def _resolve_safe_path(path: str) -> Path:
    """
    Resolve a user supplied path while enforcing WORK_DIR.

    The returned path is guaranteed to be inside WORK_DIR.

    Raises:
        PermissionError:
            If the path escapes WORK_DIR.
    """

    if not path:
        candidate = WORK_DIR
    else:
        supplied = Path(path)

        if supplied.is_absolute():
            candidate = supplied.resolve()
        else:
            candidate = (WORK_DIR / supplied).resolve()

    try:
        candidate.relative_to(WORK_DIR)
    except ValueError:
        raise PermissionError(
            "Access denied: the requested path is outside WORK_DIR."
        )

    return candidate


def _is_protected_file(path: Path) -> bool:
    """
    Return True if the path is a protected secret file.
    """

    return path.name.lower() in PROTECTED_FILES


def _relative(path: Path) -> str:
    """
    Return a nice WORK_DIR-relative path for displaying to the user.
    """

    try:
        return str(path.relative_to(WORK_DIR))
    except ValueError:
        return str(path)


# ============================================================
# 1. LIST FILES
# ============================================================

@tool
def list_files(path: str = ".") -> str:
    """
    List files and folders inside a directory located within WORK_DIR.
    """

    try:
        target = _resolve_safe_path(path)

        if not target.exists():
            return f"Path does not exist: {path}"

        if not target.is_dir():
            return f"Not a directory: {path}"

        entries = sorted(
            target.iterdir(),
            key=lambda item: (not item.is_dir(), item.name.lower()),
        )

        if not entries:
            return "Directory is empty."

        output = []

        for entry in entries:
            prefix = "[DIR]" if entry.is_dir() else "[FILE]"
            output.append(f"{prefix} {_relative(entry)}")

        return "\n".join(output)

    except PermissionError as exc:
        return str(exc)

    except Exception as exc:
        return f"Failed to list directory: {exc}"



@tool
def read_file(
    path: str,
    allow_protected: bool = False,
) -> str:
    """
    Read a text file located inside WORK_DIR.

    Protected files such as .env require allow_protected=True.
    """

    try:
        target = _resolve_safe_path(path)

        if not target.exists():
            return f"File does not exist: {path}"

        if not target.is_file():
            return f"Not a file: {path}"

        if _is_protected_file(target) and not allow_protected:
            return (
                "Permission required: this is a protected file. "
                "The user must explicitly authorize reading it."
            )

        try:
            return target.read_text(encoding="utf-8")

        except UnicodeDecodeError:
            return (
                "This file does not appear to be a UTF-8 text file. "
                "Binary files are not supported by read_file."
            )

    except PermissionError as exc:
        return str(exc)

    except Exception as exc:
        return f"Failed to read file: {exc}"


@tool
def write_file(
    path: str,
    content: str,
    allow_protected: bool = False,
) -> str:
    """
    Create or overwrite a file inside WORK_DIR.

    Missing parent directories are created automatically.
    Protected files require explicit authorization.
    """

    try:
        target = _resolve_safe_path(path)

        if _is_protected_file(target) and not allow_protected:
            return (
                "Permission required: this is a protected file. "
                "The user must explicitly authorize modifying it."
            )

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        target.write_text(
            content,
            encoding="utf-8",
        )

        return f"Successfully wrote: {_relative(target)}"

    except PermissionError as exc:
        return str(exc)

    except Exception as exc:
        return f"Failed to write file: {exc}"
@tool
def delete_file(
    path: str,
    explicitly_authorized: bool = False,
) -> str:
    """
    Delete a file inside WORK_DIR.

    The caller must confirm that the user explicitly requested deletion.
    """

    if not explicitly_authorized:
        return (
            "Deletion refused. "
            "The user must explicitly request deletion of this file."
        )

    try:
        target = _resolve_safe_path(path)

        if target == WORK_DIR:
            return "Refusing to delete WORK_DIR."

        if not target.exists():
            return f"File does not exist: {path}"

        if not target.is_file():
            return (
                "delete_file only deletes files. "
                "Directory deletion is not supported."
            )

        target.unlink()

        return f"Deleted: {_relative(target)}"

    except PermissionError as exc:
        return str(exc)

    except Exception as exc:
        return f"Failed to delete file: {exc}"


@tool
def show_untracked_files() -> str:
    """
    Show Git files that are currently untracked inside WORK_DIR.
    """

    try:
        result = subprocess.run(
            [
                "git",
                "ls-files",
                "--others",
                "--exclude-standard",
            ],
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
            timeout=10,
            shell=False,
        )

        if result.returncode != 0:
            error = result.stderr.strip()

            return (
                "Unable to retrieve untracked files."
                + (f"\nGit error: {error}" if error else "")
            )

        files = [
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip()
        ]

        if not files:
            return "No untracked files."

        return "Untracked files:\n" + "\n".join(
            f"- {file}" for file in files
        )

    except subprocess.TimeoutExpired:
        return "Git command timed out."

    except FileNotFoundError:
        return "Git is not installed or is not available in PATH."

    except Exception as exc:
        return f"Failed to inspect Git repository: {exc}"

@tool
def git_status() -> str:
    """
    Show the current Git working-tree status for WORK_DIR.
    """

    try:
        result = subprocess.run(
            [
                "git",
                "status",
                "--short",
            ],
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
            timeout=10,
            shell=False,
        )

        if result.returncode != 0:
            error = result.stderr.strip()

            return (
                "Unable to retrieve Git status."
                + (f"\nGit error: {error}" if error else "")
            )

        output = result.stdout.strip()

        if not output:
            return "Working tree is clean."

        return output

    except subprocess.TimeoutExpired:
        return "Git status timed out."

    except FileNotFoundError:
        return "Git is not installed or is not available in PATH."

    except Exception as exc:
        return f"Failed to retrieve Git status: {exc}"


@tool
def git_diff(staged: bool = False) -> str:
    """
    Return the current Git diff inside WORK_DIR.

    staged=False:
        Show unstaged changes.

    staged=True:
        Show staged changes.
    """

    try:
        command = ["git", "diff"]

        if staged:
            command.append("--cached")

        result = subprocess.run(
            command,
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
            timeout=15,
            shell=False,
        )

        if result.returncode != 0:
            error = result.stderr.strip()

            return (
                "Unable to retrieve Git diff."
                + (f"\nGit error: {error}" if error else "")
            )

        output = result.stdout.strip()

        if not output:
            if staged:
                return "There are no staged changes."

            return "There are no unstaged changes."

        return output

    except subprocess.TimeoutExpired:
        return "Git diff timed out."

    except FileNotFoundError:
        return "Git is not installed or is not available in PATH."

    except Exception as exc:
        return f"Failed to retrieve Git diff: {exc}"

@tool
def project_structure(
    max_depth: int = 4,
) -> str:
    """
    Return the directory structure inside WORK_DIR.

    Protected files are shown by filename only and are never read.
    """

    if max_depth < 1:
        return "max_depth must be at least 1."

    if max_depth > 10:
        max_depth = 10

    lines: list[str] = []

    def walk(directory: Path, depth: int) -> None:
        if depth > max_depth:
            return

        try:
            entries = sorted(
                directory.iterdir(),
                key=lambda item: (
                    not item.is_dir(),
                    item.name.lower(),
                ),
            )
        except PermissionError:
            return

        for entry in entries:
            relative = entry.relative_to(WORK_DIR)

            # Skip noisy internal Git data.
            if ".git" in relative.parts:
                continue

            indentation = "    " * (depth - 1)

            if entry.is_dir():
                lines.append(
                    f"{indentation}[DIR] {entry.name}/"
                )

                walk(
                    entry,
                    depth + 1,
                )

            else:
                lines.append(
                    f"{indentation}[FILE] {entry.name}"
                )

    walk(
        WORK_DIR,
        1,
    )

    if not lines:
        return "WORK_DIR is empty."

    return "\n".join(lines)

@tool
def run_python_file(
    path: str,
    timeout_seconds: int = 20,
) -> str:
    """
    Run a Python file located inside WORK_DIR.

    This provides controlled execution but is NOT a full OS sandbox.
    """

    try:
        target = _resolve_safe_path(path)

        if not target.exists():
            return f"File does not exist: {path}"

        if not target.is_file():
            return f"Not a file: {path}"

        if target.suffix.lower() != ".py":
            return "Only Python (.py) files are supported."

        timeout_seconds = max(
            1,
            min(timeout_seconds, 60),
        )

        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                str(target),
            ],
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            shell=False,
            env={
                "PATH": os.environ.get("PATH", ""),
                "PYTHONIOENCODING": "utf-8",
            },
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        parts = [
            f"Exit code: {result.returncode}",
        ]

        if stdout:
            parts.append(
                f"\nSTDOUT:\n{stdout[:20_000]}"
            )

        if stderr:
            parts.append(
                f"\nSTDERR:\n{stderr[:20_000]}"
            )

        if not stdout and not stderr:
            parts.append("\nNo output.")

        return "\n".join(parts)

    except PermissionError as exc:
        return str(exc)

    except subprocess.TimeoutExpired:
        return (
            f"Execution stopped because it exceeded "
            f"{timeout_seconds} seconds."
        )

    except FileNotFoundError:
        return "uv is not installed or is not available in PATH."

    except Exception as exc:
        return f"Failed to execute Python file: {exc}"    

PACKAGE_PATTERN = re.compile(
    r"^[A-Za-z0-9_.-]+"
    r"(?:\[[A-Za-z0-9_,.-]+\])?"
    r"(?:==|>=|<=|~=|>|<)?"
    r"[A-Za-z0-9*_.+-]*$"
)


@tool
def install_package(
    package: str,
    explicitly_authorized: bool = False,
) -> str:
    """
    Install a Python package into the current UV project.

    The user must explicitly request package installation.
    """

    if not explicitly_authorized:
        return (
            "Package installation refused. "
            "The user must explicitly request installation."
        )

    package = package.strip()

    if not package:
        return "Package name cannot be empty."

    # Prevent:
    # ../../evil
    # https://...
    # --some-flag
    # shell injection
    if not PACKAGE_PATTERN.fullmatch(package):
        return (
            "Invalid package specification. "
            "Only normal PyPI package names/version specifications are allowed."
        )

    try:
        env = os.environ.copy()

        # Keep UV-generated caches/install state in the workspace
        # as much as practical.
        env["UV_CACHE_DIR"] = str(WORK_DIR / ".uv-cache")
        env["UV_PYTHON_INSTALL_DIR"] = str(WORK_DIR / ".uv-python")

        result = subprocess.run(
            [
                "uv",
                "add",
                package,
            ],
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
            timeout=180,
            shell=False,
            env=env,
        )

        output = []

        if result.stdout.strip():
            output.append(result.stdout.strip())

        if result.stderr.strip():
            output.append(result.stderr.strip())

        if result.returncode != 0:
            return (
                f"Package installation failed "
                f"(exit code {result.returncode}).\n"
                + "\n".join(output)
            )

        return (
            f"Successfully installed dependency: {package}\n"
            + "\n".join(output)
        )

    except subprocess.TimeoutExpired:
        return "Package installation timed out after 180 seconds."

    except FileNotFoundError:
        return "uv was not found. Make sure UV is installed."

    except Exception as exc:
        return f"Package installation failed: {exc}"

@tool
def browse_documentation(
    query: str,
    technology: str = "",
) -> str:
    """
    Search current official documentation for a programming language,
    library, framework, or tool.

    Intended for build errors, API changes, version differences,
    configuration issues, and current documentation.
    """

    query = query.strip()
    technology = technology.strip()

    if not query:
        return "Documentation query cannot be empty."

    try:
        client = Groq()

        target = (
            f"Technology/framework/language: {technology}\n"
            if technology
            else ""
        )

        prompt = f"""
You are researching a software-development issue.

{target}
Question:
{query}

Search the current web documentation.

IMPORTANT:
- Prefer official documentation and official project repositories.
- Prefer current documentation over old tutorials.
- Mention version-specific behavior when relevant.
- Do not invent APIs.
- If official documentation conflicts with blogs, use official documentation.
- Give a concise practical answer.
- Include the documentation/source references returned by search.
"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            tools=[
                {
                    "type": "browser_search",
                }
            ],
            tool_choice="required",
            reasoning_effort="low",
            max_completion_tokens=4000,
        )

        content = response.choices[0].message.content

        if not content:
            return "Documentation search returned no useful content."

        return content

    except Exception as exc:
        return f"Documentation search failed: {exc}"        

ALLOWED_COMMANDS = {
    "python",
    "python3",
    "uv",
    "pytest",
    "ruff",
    "mypy",
    "node",
    "npm",
    "npx",
    "pnpm",
    "yarn",
    "cargo",
    "rustc",
    "go",
    "java",
    "javac",
    "dotnet",
}


DANGEROUS_ARGUMENTS = {
    "rm",
    "rmdir",
    "del",
    "format",
    "shutdown",
    "reboot",
    "kill",
    "taskkill",
}


@tool
def run_project_command(
    command: str,
    timeout_seconds: int = 60,
) -> str:
    """
    Run an approved development/build/test command from WORK_DIR.

    Arbitrary shell syntax is not supported.
    """

    command = command.strip()

    if not command:
        return "Command cannot be empty."

    # We intentionally reject shell operators.
    forbidden_tokens = [
        "&&",
        "||",
        ";",
        "|",
        ">",
        "<",
        "`",
        "$(",
        "\n",
        "\r",
    ]

    if any(token in command for token in forbidden_tokens):
        return (
            "Command rejected: shell operators, redirection, "
            "pipes, and command chaining are not allowed."
        )

    try:
        args = shlex.split(
            command,
            posix=os.name != "nt",
        )
    except ValueError as exc:
        return f"Invalid command syntax: {exc}"

    if not args:
        return "Command cannot be empty."

    executable = Path(args[0]).name.lower()

    if executable.endswith(".exe"):
        executable = executable[:-4]

    if executable not in ALLOWED_COMMANDS:
        return (
            f"Command '{executable}' is not in the allowed "
            f"development-command list."
        )

    lowered = {
        arg.lower()
        for arg in args
    }

    if lowered.intersection(DANGEROUS_ARGUMENTS):
        return "Command rejected because it contains a dangerous operation."

    timeout_seconds = max(
        1,
        min(timeout_seconds, 180),
    )

    try:
        env = os.environ.copy()

        env["UV_CACHE_DIR"] = str(
            WORK_DIR / ".uv-cache"
        )

        result = subprocess.run(
            args,
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            shell=False,
            env=env,
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        output = [
            f"Command: {command}",
            f"Exit code: {result.returncode}",
        ]

        if stdout:
            output.append(
                "\nSTDOUT:\n"
                + stdout[:30_000]
            )

        if stderr:
            output.append(
                "\nSTDERR:\n"
                + stderr[:30_000]
            )

        if not stdout and not stderr:
            output.append("\nNo output.")

        return "\n".join(output)

    except subprocess.TimeoutExpired:
        return (
            f"Command stopped after exceeding "
            f"{timeout_seconds} seconds."
        )

    except FileNotFoundError:
        return (
            f"Executable '{args[0]}' was not found."
        )

    except Exception as exc:
        return f"Command execution failed: {exc}"

@tool
def git_current_branch() -> str:
    """
    Return the current Git branch.
    """

    try:
        result = subprocess.run(
            [
                "git",
                "branch",
                "--show-current",
            ],
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
            timeout=10,
            shell=False,
        )

        if result.returncode != 0:
            return (
                "Failed to determine Git branch:\n"
                + result.stderr.strip()
            )

        branch = result.stdout.strip()

        if not branch:
            return "Git repository is currently in detached HEAD state."

        return branch

    except Exception as exc:
        return f"Failed to determine Git branch: {exc}"

@tool
def git_add(
    paths: list[str],
    explicitly_authorized: bool = False,
) -> str:
    """
    Stage one or more paths in the Git repository.

    All paths must resolve inside WORK_DIR.
    """

    if not explicitly_authorized:
        return (
            "Git staging refused. "
            "The user must explicitly ask to stage/add files."
        )

    if not paths:
        return "No paths were provided."

    safe_paths = []

    try:
        for path in paths:
            target = _resolve_safe_path(path)

            if _is_protected_file(target):
                return (
                    f"Refusing to stage protected file: "
                    f"{_relative(target)}"
                )

            safe_paths.append(
                str(target.relative_to(WORK_DIR))
            )

        result = subprocess.run(
            [
                "git",
                "add",
                "--",
                *safe_paths,
            ],
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
            timeout=15,
            shell=False,
        )

        if result.returncode != 0:
            return (
                "git add failed:\n"
                + result.stderr.strip()
            )

        return (
            "Successfully staged:\n"
            + "\n".join(
                f"- {path}"
                for path in safe_paths
            )
        )

    except PermissionError as exc:
        return str(exc)

    except Exception as exc:
        return f"git add failed: {exc}"


@tool
def git_commit(
    message: str,
    explicitly_authorized: bool = False,
) -> str:
    """
    Create a Git commit from already-staged changes.
    """

    if not explicitly_authorized:
        return (
            "Commit refused. "
            "The user must explicitly request a Git commit."
        )

    message = message.strip()

    if not message:
        return "Commit message cannot be empty."

    if len(message) > 500:
        return "Commit message is too long."

    try:
        staged = subprocess.run(
            [
                "git",
                "diff",
                "--cached",
                "--name-only",
            ],
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
            timeout=10,
            shell=False,
        )

        if staged.returncode != 0:
            return staged.stderr.strip()

        files = [
            line.strip()
            for line in staged.stdout.splitlines()
            if line.strip()
        ]

        if not files:
            return "There are no staged changes to commit."

        protected = {
            ".env",
            ".env.local",
            ".env.production",
            ".env.development",
        }

        for filename in files:
            if Path(filename).name.lower() in protected:
                return (
                    f"Commit refused because protected file "
                    f"'{filename}' is staged."
                )

        result = subprocess.run(
            [
                "git",
                "commit",
                "-m",
                message,
            ],
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
            timeout=30,
            shell=False,
        )

        output = (
            result.stdout.strip()
            or result.stderr.strip()
        )

        if result.returncode != 0:
            return f"Git commit failed:\n{output}"

        return f"Commit created successfully:\n{output}"

    except Exception as exc:
        return f"Git commit failed: {exc}"

@tool
def git_push(
    remote: str = "origin",
    branch: str = "",
    explicitly_authorized: bool = False,
) -> str:
    """
    Push the current Git branch to a configured remote.

    The user must explicitly request the push.
    """

    if not explicitly_authorized:
        return (
            "Push refused. "
            "The user must explicitly request pushing to GitHub."
        )

    safe_name_pattern = re.compile(
        r"^[A-Za-z0-9._/-]+$"
    )

    if not safe_name_pattern.fullmatch(remote):
        return "Invalid Git remote name."

    try:
        if not branch:
            branch_result = subprocess.run(
                [
                    "git",
                    "branch",
                    "--show-current",
                ],
                cwd=WORK_DIR,
                capture_output=True,
                text=True,
                timeout=10,
                shell=False,
            )

            branch = branch_result.stdout.strip()

        if not branch:
            return (
                "Cannot push because the repository "
                "is in detached HEAD state."
            )

        if not safe_name_pattern.fullmatch(branch):
            return "Invalid branch name."

        # Check whether obvious secret files are tracked.
        tracked_result = subprocess.run(
            [
                "git",
                "ls-files",
            ],
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
            timeout=10,
            shell=False,
        )

        tracked_files = {
            line.strip()
            for line in tracked_result.stdout.splitlines()
        }

        protected_names = {
            ".env",
            ".env.local",
            ".env.production",
            ".env.development",
        }

        dangerous_tracked = [
            file
            for file in tracked_files
            if Path(file).name.lower() in protected_names
        ]

        if dangerous_tracked:
            return (
                "Push refused because secret configuration "
                "files are tracked by Git:\n"
                + "\n".join(
                    f"- {file}"
                    for file in dangerous_tracked
                )
            )

        result = subprocess.run(
            [
                "git",
                "push",
                remote,
                branch,
            ],
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
            timeout=120,
            shell=False,
        )

        output = "\n".join(
            part
            for part in [
                result.stdout.strip(),
                result.stderr.strip(),
            ]
            if part
        )

        if result.returncode != 0:
            return (
                f"Git push failed "
                f"(exit code {result.returncode}):\n"
                f"{output}"
            )

        return (
            f"Successfully pushed branch "
            f"'{branch}' to '{remote}'.\n"
            f"{output}"
        )

    except subprocess.TimeoutExpired:
        return "Git push timed out."

    except Exception as exc:
        return f"Git push failed: {exc}"

@tool
def git_remotes() -> str:
    """
    Show configured Git remotes without exposing credentials.
    """

    try:
        result = subprocess.run(
            [
                "git",
                "remote",
                "-v",
            ],
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
            timeout=10,
            shell=False,
        )

        if result.returncode != 0:
            return (
                "Unable to retrieve Git remotes:\n"
                + result.stderr.strip()
            )

        output = result.stdout.strip()

        if not output:
            return "No Git remotes are configured."

        # Hide credentials accidentally embedded in HTTPS URLs.
        output = re.sub(
            r"https://[^@\s]+@",
            "https://***@",
            output,
        )

        return output

    except Exception as exc:
        return f"Unable to retrieve Git remotes: {exc}"

@tool
def create_github_repository(
    name: str,
    private: bool = True,
    explicitly_authorized: bool = False,
) -> str:
    """
    Create a GitHub repository from WORK_DIR using GitHub CLI.

    Requires:
        gh installed
        gh auth login already completed
    """

    if not explicitly_authorized:
        return (
            "Repository creation refused. "
            "The user must explicitly request it."
        )

    name = name.strip()

    if not re.fullmatch(
        r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)?",
        name,
    ):
        return "Invalid GitHub repository name."

    if shutil.which("gh") is None:
        return (
            "GitHub CLI (gh) is not installed or "
            "not available in PATH."
        )

    visibility = "--private" if private else "--public"

    try:
        result = subprocess.run(
            [
                "gh",
                "repo",
                "create",
                name,
                visibility,
                "--source",
                str(WORK_DIR),
                "--remote",
                "origin",
            ],
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
            timeout=90,
            shell=False,
        )

        output = "\n".join(
            part
            for part in [
                result.stdout.strip(),
                result.stderr.strip(),
            ]
            if part
        )

        if result.returncode != 0:
            return (
                f"GitHub repository creation failed:\n"
                f"{output}"
            )

        return (
            "GitHub repository created successfully.\n"
            + output
        )

    except subprocess.TimeoutExpired:
        return "GitHub repository creation timed out."

    except Exception as exc:
        return (
            f"GitHub repository creation failed: {exc}"
        )                            


@tool
def collect_project_context() -> str:
    """
    Collect basic project metadata for summaries and architecture analysis.

    Does not read .env or secret files.
    """

    important_files = [
        "pyproject.toml",
        "requirements.txt",
        "package.json",
        "Cargo.toml",
        "go.mod",
        "README.md",
        "README",
    ]

    sections = []

    sections.append(
        f"Project root: {WORK_DIR.name}"
    )

    try:
        top_level = sorted(
            WORK_DIR.iterdir(),
            key=lambda item: (
                not item.is_dir(),
                item.name.lower(),
            ),
        )

        sections.append(
            "\nTop-level structure:\n"
            + "\n".join(
                (
                    f"[DIR] {entry.name}/"
                    if entry.is_dir()
                    else f"[FILE] {entry.name}"
                )
                for entry in top_level
                if entry.name != ".git"
            )
        )

        for filename in important_files:
            target = WORK_DIR / filename

            if not target.exists() or not target.is_file():
                continue

            try:
                content = target.read_text(
                    encoding="utf-8"
                )

                sections.append(
                    f"\n--- {filename} ---\n"
                    + content[:12_000]
                )

            except UnicodeDecodeError:
                continue

        return "\n".join(sections)

    except Exception as exc:
        return f"Could not collect project context: {exc}"

@tool
def setup_documentation(
    explicitly_authorized: bool = False,
) -> str:
    """
    Create a basic project documentation structure inside WORK_DIR.

    Existing files are never overwritten.
    """

    if not explicitly_authorized:
        return (
            "Documentation creation refused. "
            "The user must explicitly request it."
        )

    files = {
        "README.md": """# Project

## Overview

TODO

## Installation

TODO

## Usage

TODO

## Project Structure

TODO

## Development

TODO

""",
        "docs/architecture.md": """# Architecture

## Overview

TODO

## Components

TODO

## Data Flow

TODO

## Design Decisions

TODO
""",
        "docs/development.md": """# Development Guide

## Setup

TODO

## Running the Project

TODO

## Testing

TODO

## Code Quality

TODO
""",
    }

    created = []
    skipped = []

    try:
        for relative_path, content in files.items():
            target = _resolve_safe_path(
                relative_path
            )

            if target.exists():
                skipped.append(relative_path)
                continue

            target.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            target.write_text(
                content,
                encoding="utf-8",
            )

            created.append(relative_path)

        output = []

        if created:
            output.append(
                "Created:\n"
                + "\n".join(
                    f"- {file}"
                    for file in created
                )
            )

        if skipped:
            output.append(
                "\nAlready existed and were not overwritten:\n"
                + "\n".join(
                    f"- {file}"
                    for file in skipped
                )
            )

        return "\n".join(output)

    except Exception as exc:
        return f"Documentation setup failed: {exc}"
TOOLS = [
    # Files
    list_files,
    read_file,
    write_file,
    delete_file,

    # Project inspection
    project_structure,
    collect_project_context,

    # Execution / building
    run_python_file,
    run_project_command,
    install_package,

    # Documentation
    browse_documentation,
    setup_documentation,

    # Git
    git_status,
    git_diff,
    show_untracked_files,
    git_current_branch,
    git_remotes,
    git_add,
    git_commit,
    git_push,
    create_github_repository,
]        