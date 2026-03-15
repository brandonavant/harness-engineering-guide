# Context Reset Checklist -- When to /clear, /compact, or Start Fresh

Context management is one of the most underrated skills in working with Claude Code. A cluttered context leads to degraded output quality, repeated mistakes, and the agent "forgetting" decisions made earlier in the session. Knowing when and how to reset context is the difference between a productive session and a frustrating one.

---

## Decision Tree

### Use /clear when:
- You are **switching to an unrelated task**. If the previous task was backend auth and the next is frontend styling, the old context is noise.
- You have made **2+ failed corrections** on the same issue. The context now contains multiple wrong approaches, and the agent is more likely to blend them than to start clean.
- The context feels **"polluted" with wrong approaches**. If you told the agent to try approach A, then switched to B, then back to a modified A, the agent's understanding of what you want is muddled.
- You are **starting a new phase**. Each phase deserves a fresh context with only the relevant instructions loaded.

### Use /compact when:
- The context is **growing but the task is not done**. You are midway through implementation and need to keep going, but the accumulated tool output and exploration is crowding out the important decisions.
- You want to **preserve key decisions but shed tool output**. Compaction keeps the high-level narrative while dropping verbose file reads, search results, and intermediate steps.
- You are in a **long implementation session** and quality is starting to drift. Compaction can restore focus without losing the thread.

### Use /compact with focus instructions when:
- You want to **preserve specific context** while shedding everything else. For example: `/compact Focus on the auth integration approach we decided on and the database schema for user sessions.`
- You are about to **shift sub-tasks** within the same phase. Focusing the compaction on what matters next prevents the agent from carrying irrelevant details forward.

### Start a brand new session when:
- **/compact is not recovering quality**. If you compact and the agent still produces off-target output, the session state may be too damaged to salvage.
- The session has been **running for hours with diminishing returns**. Long sessions accumulate subtle context drift that compaction cannot fully resolve.
- You want a **completely fresh perspective**. Sometimes the best thing is a clean slate with no preconceptions from a previous attempt.

---

## Before Any Reset

- [ ] **Commit all changes.** Uncommitted work exists only in the filesystem. It will survive a reset, but you lose the ability to diff against a known state.
- [ ] **Ensure the agent state file is updated.** Write down what was completed, what was in progress, and what decisions were made. The state file is the bridge between the dying context and the new one.
- [ ] **Save important decisions.** If you made a key architectural decision during the session, write it to auto-memory, the agent state file, or a doc. Context resets erase decisions that only existed in conversation.

## After Any Reset

- [ ] **Re-read the relevant instructions.** Tell the agent to read CLAUDE.md, the relevant agent instruction file, or the specific skill needed for the current task. Do not assume it knows what it knew before.
- [ ] **Re-invoke the relevant skill.** If the task requires a mandatory skill (design enforcement, contract check), invoke it explicitly. Skills load context at the moment of maximum relevance.
- [ ] **Check the agent state file.** Have the agent read its state file to pick up where the previous session left off. The state file is your continuity mechanism across context boundaries.
