# Claude Code Custom Commands

This directory contains custom slash commands for Claude Code.

## Available Commands

### `/musk` - Musk Management Framework Refactor

Apply Elon Musk's 5-step management framework to ruthlessly eliminate waste from your codebase.

**When to use:**
- Codebase feels bloated with unnecessary abstractions
- Multiple files/docs doing similar things
- Lots of "just in case" code that's never used
- Unclear which configs/docs are authoritative
- Historical artifacts cluttering the repo

**What it does:**
1. **Round 1:** Challenges architectural layers and unused features
2. **Round 2:** Identifies and consolidates code duplication
3. **Round 3:** Eliminates redundant configuration files
4. **Round 4:** Deletes competing/redundant documentation
5. **Round 5:** Removes historical development cruft

**How to use:**
```bash
/musk
```

The command will guide you through 5 systematic rounds of analysis and deletion. For each round:
- Claude presents findings with concrete evidence
- You choose deletion strategy (conservative → nuclear)
- Claude executes changes and commits
- Progress is measured and tracked

**Expected results:**
- 40-60% codebase reduction (based on this project: 58%)
- Clearer structure and entry points
- Eliminated duplication and redundancy
- Faster onboarding for new developers
- Less maintenance burden

## Installing in Other Projects

To use these commands in another project:

1. Copy the entire `.claude/` directory to your project root
2. Run `/musk` to start the refactoring process
3. Adjust the prompt if needed for your specific codebase

## Creating New Commands

To create a new slash command:

1. Create a markdown file in `.claude/commands/`
2. Name it `<command-name>.md`
3. Write the prompt that Claude should follow
4. Use it with `/<command-name>`

Example:
```bash
# Create new command
echo "Your prompt here" > .claude/commands/mycommand.md

# Use it
/mycommand
```

## Command Best Practices

**Good commands:**
- Are specific and actionable
- Provide clear success criteria
- Include examples and patterns
- Guide Claude step-by-step
- Wait for user approval on risky actions

**Avoid:**
- Vague instructions like "improve the code"
- One-size-fits-all approaches
- Skipping user approval for deletions
- Commands without measurable outcomes

## References

- [Claude Code Documentation](https://github.com/anthropics/claude-code)
- [Original Musk Framework Application PR](#) - See `PULL_REQUEST.md` for detailed results

---

**Pro tip:** The `/musk` command works best on codebases that have grown organically over time. Run it periodically (quarterly?) to prevent bloat accumulation.
