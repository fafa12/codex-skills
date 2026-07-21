---
name: generate-menglingfa-commit-message
description: Inspect the current Git diff and recent commits authored by menglingfa, then generate a Chinese commit message matching that author's local style without committing changes. Trigger when the user says `cm` or `commit message` in a Git/SG2 development context, including terse standalone requests. Also use for requests such as "参考menglingfa的提交，根据当前diff输出commit message", "按孟令发风格生成提交信息", "输出server/lsserver的commit message", "输出protocol的commit message", "protocol也生成", or "分protocol和lsserver输出".
---

# Generate Menglingfa Commit Message

Generate evidence-based commit messages from the current worktree. Never edit files, stage changes, or create commits.

## Workflow

1. Resolve repository scope from the request.
   - Treat a standalone `cm` or `commit message` as "generate a commit message from the current diff".
   - Prefer an explicit repository path or named module.
   - Treat `server` as `lsserver` when the surrounding workspace uses that name.
   - If the current directory is a Git repository, inspect it.
   - In the SG2 workspace, use `C:\00work\code\sg2\lsserver` and `C:\00work\code\sg2\protocol` as known candidates.
   - If no target is explicit and the current directory is not a repository, check candidate repositories for changes. Use the only dirty repository; if multiple are dirty, inspect each and output separate messages.

2. Gather fresh evidence for every request. Do not reuse a diff or conclusion from an earlier turn.
   - On Windows, run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <skill-dir>\scripts\collect-git-context.ps1 -RepoPath <repo>`.
   - Otherwise run `git status --short`, `git diff HEAD --stat`, `git diff HEAD --name-status`, `git diff HEAD`, and `git log --author=menglingfa --no-merges --max-count=20 --pretty=format:"%h%x09%s%n%b%n---"`.
   - Inspect relevant untracked source or configuration files separately because `git diff HEAD` omits them.
   - Exclude generated artifacts such as `__pycache__`, build output, IDE metadata, and logs from the proposed message. Mention them briefly only when they are present and likely to be committed accidentally.

3. Infer the behavioral intent from the patch.
   - Read the actual changed code, not only filenames or diff statistics.
   - Group related changes into user-visible behavior, correctness fixes, protocol changes, cleanup, and tests.
   - Use nearby author commits affecting the same module as the strongest style reference.

4. Compose the message in the repository's observed style.
   - Preserve the established module prefix. For JianGe/JGZZ changes, normally use `[剑阁]`.
   - Use `修复` for defects, `优化` for behavior or flow improvements, `新增` for new capability, and `适配` for compatibility changes.
   - Keep the title concrete and concise; describe behavior rather than implementation class names.
   - Add 2-5 Chinese body bullets when the diff has multiple meaningful changes. Use 1-3 bullets for a narrow change.
   - Include test changes in the last bullet only when they materially improve coverage.
   - Do not claim effects that cannot be supported by the diff.

5. Format the result for direct use.
   - For one repository, output one fenced text block containing the title and optional body.
   - When the user requests `protocol` and `lsserver` separately, label each repository and provide one fenced text block per repository.
   - If a requested repository has no meaningful changes, state that instead of inventing a message.
   - Do not add a long analysis unless the user asks for reasoning.

## Output Pattern

```text
[剑阁] 优化据点车轮战推进和结算调度清理

- 据点车轮战增加开始/结束状态控制，统一在战斗完成后推进下一场
- 防守被突破后，将剩余攻击队列按顺序转为驻防队列
- 结算后停止相关定时调度，并补充关键流程单测
```
