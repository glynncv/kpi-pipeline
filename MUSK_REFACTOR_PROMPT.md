# 🔥 Musk Management Framework - Code Refactoring Prompt

**Copy this entire prompt to Claude Code in any project to ruthlessly eliminate bloat.**

---

I want you to apply Elon Musk's 5-step management framework to eliminate waste from this codebase:

## The Framework

1. **Challenge Requirements** - Question every requirement, especially from smart people
2. **Delete Ruthlessly** - Delete parts or processes; add back only if truly needed
3. **Simplify/Optimize** - Never optimize what shouldn't exist
4. **Accelerate Cycle** - Go faster, but only after the first three steps
5. **Automate** - The very last step

## Your Mission

Analyze this codebase in **5 systematic rounds** and identify waste. For each round:

1. Present findings with concrete evidence (file:line, grep results, usage analysis)
2. Provide 2-3 deletion options (conservative → aggressive)
3. Wait for my approval before proceeding
4. Execute the deletions and update all references
5. Commit the changes with clear messages
6. Measure the impact (lines/files deleted)

## Round 1: Challenge Architectural Layers

**Find and eliminate:**
- Intermediate layers that add no value (bypassed abstractions)
- Unused features, CLI flags, optional modes
- Premature optimizations (caching, queuing, batching)
- "Just in case" code paths that never execute

**For each finding:**
- Show where it exists (file:line)
- Prove it's unused (grep for actual usage)
- Calculate deletion impact (lines, files, dependencies)
- Provide options (conservative → aggressive)

## Round 2: Challenge Code Duplication

**Find and consolidate:**
- Duplicate implementations (similar functions across files)
- Copy-paste code (same logic patterns repeated)
- Redundant utilities (multiple versions of formatting, validation)
- Should-be-shared code (constants, types, helpers)

**For each finding:**
- Show the duplication with code samples
- Measure duplication (lines × occurrences)
- Extract to shared module
- Estimate lines saved

## Round 3: Challenge Configuration

**Find and eliminate:**
- Redundant config files (same info in multiple formats)
- Never-loaded configs (referenced in docs but not code)
- Example/template configs (should be in docs)
- Competing configs (which is source of truth?)

**For each finding:**
- Grep for actual code loading the config
- Show what's redundant (diff analysis)
- Propose single source of truth
- List files needing updates

## Round 4: Challenge Documentation

**Find and eliminate:**
- Competing entry points (README, START_HERE, QUICKSTART, etc.)
- Redundant docs (same info in multiple files)
- Stale documentation (describes old code/features)
- Inline-worthy docs (should be code comments or config)

**Red flags to eliminate:**
- Multiple "getting started" docs
- Generic templates (CODE_OF_CONDUCT, CONTRIBUTING) for internal tools
- Documentation duplicating what code/config already says
- Historical development notes (should be in git/PRs)

**For each finding:**
- Map the redundancy (which files overlap)
- Identify canonical version (keep the best)
- Provide tiered options (conservative → nuclear)
- List files referencing deleted docs

## Round 5: Final Sweep - Historical Cruft

**Find and eliminate:**
- Development artifacts (session notes, PR drafts, planning docs)
- Reference implementations (old code kept "for reference")
- Deprecated features (commented-out code, disabled modules)
- Build artifacts (cached files, compiled outputs)

**For each finding:**
- Confirm it's truly historical (not needed for current code)
- Verify it exists elsewhere (git history, GitHub PRs)
- Calculate total waste (files, lines, disk space)
- Provide nuclear option (delete entire directories)

## Rules of Engagement

1. ✅ **NEVER delete without evidence** - Use Grep to prove it's unused
2. ✅ **ALWAYS provide options** - Let me choose risk tolerance
3. ✅ **DELETE, don't comment out** - Commented code is still bloat
4. ✅ **CONSOLIDATE before deleting** - Extract shared utilities from dupes
5. ✅ **MEASURE everything** - Lines, files, bytes - make waste visible
6. ✅ **ONE round at a time** - Build momentum, don't overwhelm
7. ✅ **COMMIT after each round** - Track progress, enable rollback

## Output Format Per Round

```
## Round X: [Title]

### 🔍 Findings
1. [File:line] - [Description] - [Lines affected]
2. [File:line] - [Description] - [Lines affected]

### 📊 Evidence
[Grep results, usage analysis, etc.]

### 🎯 Deletion Options

**Option A (Conservative):** [Description]
- Delete: [specific items]
- Impact: -X lines

**Option B (Aggressive):** [Description]
- Delete: [specific items]
- Impact: -Y lines

**Option C (Nuclear):** [Description]
- Delete: [specific items]
- Impact: -Z lines

### ⏸️ Your Choice?
[Wait for A, B, or C]
```

After each round, show cumulative progress:

```
📊 Cumulative Impact After Round X:
─────────────────────────────────────
Lines deleted:    X,XXX
Lines added:        XXX  (shared utilities)
Net reduction:   -X,XXX  (XX% of bloat)
Files deleted:       XX
Files created:        X
Files modified:      XX
```

## Getting Started

1. Start with Round 1 (Challenge Architectural Layers)
2. Use Task tool with Explore agent for thorough analysis
3. Present findings with concrete evidence
4. Wait for my approval (A, B, or C)
5. Execute deletions and commit
6. Move to Round 2

**Ready?** Begin with Round 1 analysis.

---

## Success Story Reference

This framework eliminated **58% of bloat** from a KPI pipeline codebase:
- 14,773 lines deleted
- 439 lines added (shared utilities)
- Net: -14,334 lines
- 45 files deleted
- Clearer structure, faster onboarding, less maintenance

**Remember:** *"The most common error of a smart engineer is to optimize a thing that should not exist."* - Elon Musk
