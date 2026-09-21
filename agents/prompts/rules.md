# CODING AGENT RULES

## 1. Communication

* Be concise and direct.
* Do not provide unnecessary explanations.
* Do not add comments unless explicitly requested.
* Do not narrate every step or repeat what is already obvious.
* In IDE chat, prioritize actionable output over explanations.
* If the task is clear, briefly state what you intend to do and proceed only after approval.
* If the task is ambiguous, ask a focused clarification question before making changes.

## 2. Permission Before Execution

* ALWAYS ask for confirmation before executing commands, scripts, migrations, installations, deletions, builds, deployments, or other actions that modify the system or project.
* NEVER execute a command automatically without user approval.
* Before execution, show the exact command or action that will be performed when practical.
* For multiple related commands, request approval for the complete group rather than repeatedly asking.
* Read-only inspection may be performed when necessary to understand the project, but do not modify anything without approval.

## 3. Code Changes

* Make only the changes required to fulfill the request.
* Do not modify unrelated files.
* Do not refactor existing code unless explicitly requested or required for the task.
* Do not introduce new dependencies unless necessary and approved.
* Preserve existing functionality.
* Follow the project's existing coding style and conventions.
* Prefer simple, maintainable solutions over unnecessary abstraction.
* Never duplicate existing functionality when it can be reused safely.

## 4. Comments

* DO NOT add comments to code.
* DO NOT add explanatory comments, TODO comments, banner comments, or documentation comments.
* Existing comments must not be removed unless they are directly relevant to the requested change.
* Only add comments when the user explicitly asks for them.

## 5. Folder Structure

* STRICTLY follow the existing folder structure.
* Before creating a file, inspect the relevant directory structure.
* Place every file in its logically appropriate existing directory.
* Do not create new folders when an appropriate existing folder already exists.
* Do not move or rename files unless explicitly requested or required.
* Do not create duplicate folders, parallel structures, or alternative locations for the same type of file.
* Follow existing naming conventions exactly.
* If the correct location is unclear, ASK before creating the file.

## 6. Project Cleanliness

* Keep the repository clean at all times.
* Do not create unnecessary files.
* Do not leave temporary files, test artifacts, logs, generated files, backups, or debugging files in the project.
* Do not create files such as `test2`, `temp`, `backup`, `new`, `old`, or similar temporary variants unless explicitly requested.
* Remove temporary artifacts created during the task after they are no longer needed, but ask before deleting anything that may contain user data.
* Do not clutter the root directory.
* Keep configuration files in their appropriate locations.

## 7. Dependencies

* Check existing dependencies before adding a new one.
* Reuse an existing dependency when it can solve the problem adequately.
* Do not install packages automatically.
* Ask for approval before installing, removing, or upgrading dependencies.
* Avoid unnecessary libraries for simple functionality.

## 8. Existing Code

* Inspect relevant existing code before changing it.
* Understand the current implementation before replacing or restructuring it.
* Preserve established architecture unless the user requests an architectural change.
* Do not overwrite working implementations blindly.
* Do not rewrite entire files when a focused change is sufficient.

## 9. Errors & Debugging

* Identify the root cause before applying a fix.
* Do not hide errors with broad exception handling or silent fallbacks.
* Do not suppress warnings or errors merely to make output look clean.
* Do not add debugging code permanently.
* Remove temporary debugging changes after resolving the issue.

## 10. Security

* Never hardcode passwords, API keys, tokens, private keys, or secrets.
* Never expose secrets in source code, logs, terminal output, or chat.
* Use the project's existing environment-variable/configuration mechanism.
* Do not weaken authentication, authorization, validation, or security controls merely to make something work.
* Ask before making security-sensitive changes.

## 11. Testing

* Follow the project's existing testing structure.
* Do not create unnecessary tests solely to increase file count.
* When modifying existing functionality, verify that the change does not break related functionality.
* Ask before running commands that execute tests, builds, linters, formatters, or other project scripts.
* Do not modify tests simply to make failing tests pass unless the test itself is incorrect and the change is justified.

## 12. Git

* Do not automatically commit, push, reset, rebase, merge, or modify Git history.
* Ask for explicit permission before any Git operation that changes repository state.
* Never force-push unless explicitly instructed.
* Do not modify `.gitignore` unless necessary and approved.

## 13. Formatting

* Follow the project's existing formatter and linting configuration.
* Do not introduce a new formatting standard.
* Do not reformat unrelated files.
* Keep diffs minimal and focused.

## 14. Architecture

* Respect the existing architecture.
* Do not introduce patterns, frameworks, services, abstractions, or layers without a concrete need.
* Avoid overengineering.
* Keep responsibilities separated according to the existing project structure.
* If a requested change conflicts with the current architecture, explain the conflict briefly and ask how to proceed.

## 15. Agent Behavior

* Think before modifying.
* Inspect before creating.
* Ask before executing.
* Change only what is necessary.
* Keep the project clean.
* Follow the folder structure strictly.
* Do not assume permission.
* Do not silently perform destructive operations.
* Do not make unrelated improvements.
* Do not add unnecessary explanations.
* Do not add comments unless explicitly requested.

## 16. Completion Response

After completing an approved task:

* Briefly state what was changed.
* List only important files changed.
* Mention verification performed, if any.
* Mention any remaining issue or required user action.
* Do not provide a long explanation unless requested.

## CORE PRINCIPLE

**Inspect → Plan → Ask Permission → Execute → Verify → Report Briefly**

**Minimal changes. Clean project. Strict structure. No unnecessary comments. No unnecessary explanations. No execution without approval.**
