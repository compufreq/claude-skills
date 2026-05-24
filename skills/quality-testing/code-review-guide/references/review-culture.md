# Review Culture & Etiquette Reference

## 1. Constructive Feedback Framework

### Comment Types (Prefix Convention)

| Prefix | Meaning | Blocking? |
|--------|---------|----------|
| `fix:` | Must change — bug, security, correctness | Yes |
| `suggestion:` | Better approach exists, but current works | No |
| `nit:` | Style, formatting, minor preference | No |
| `question:` | Need to understand intent | Maybe |
| `praise:` | Something done well | No |
| `thought:` | Brainstorming, future consideration | No |

### Good vs Bad Comments

**Bad (vague, dismissive, personal):**
- "This is wrong"
- "Why would you do it this way?"
- "This code is terrible"
- "Just rewrite this"

**Good (specific, constructive, collaborative):**
- "fix: This query isn't parameterized — it's vulnerable to SQL injection. Here's how to fix it: `cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))`"
- "suggestion: Consider using a guard clause here to reduce nesting — it would make the happy path clearer"
- "nit: Our convention is `snake_case` for function names"
- "question: I'm not sure I understand the business logic here — could you add a comment explaining why we skip validation for admin users?"
- "praise: Great test coverage on the edge cases here!"

## 2. Review Etiquette

### For Reviewers
1. **Review promptly** — within 4 hours during business hours
2. **Be kind** — the author is a colleague, not an adversary
3. **Explain why** — don't just say "change this"; explain the reasoning
4. **Suggest, don't dictate** — "consider X" not "do X"
5. **Distinguish blocking from non-blocking** — use prefixes
6. **Praise good code** — not just criticism
7. **Don't bike-shed** — focus on substance, not style (let linters handle style)
8. **Ask questions** — assume you might be missing context
9. **Offer alternatives** — include code suggestions when possible
10. **Keep comments focused** — one topic per comment thread

### For Authors
1. **Don't take it personally** — feedback is about code, not you
2. **Explain your reasoning** — if you disagree, share your thinking
3. **Respond to every comment** — even if just "done" or "acknowledged"
4. **Say thank you** — reviewers are investing time to help
5. **Be open to change** — you might not have the best approach
6. **Split large PRs proactively** — don't make reviewers suffer
7. **Provide context** — good PR descriptions save review time
8. **Test before requesting review** — don't waste reviewer time on broken code

## 3. Team Dynamics

### Code Review Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| **Rubber-stamping** | Approving without reading | Set review time expectations, track metrics |
| **Gatekeeping** | One person blocks all merges with nits | Distinguish blocking from non-blocking |
| **Review avoidance** | PRs sit for days | SLA (4-hour first response), rotation |
| **Nitpick wars** | Endless style debates | Linters + style guide settle these automatically |
| **Hero reviewer** | One person reviews everything | Rotate reviewers, set CODEOWNERS |
| **Fear of feedback** | Authors avoid asking for review | Psychological safety, blameless culture |

### Review Metrics to Track

| Metric | Target | Why |
|--------|--------|-----|
| Time to first review | < 4 hours | Don't block authors |
| Review cycles | < 3 rounds | Efficient reviews |
| PR size | < 400 lines | Thorough reviews |
| Comments per PR | 3-10 (avg) | Engaged but not excessive |
| Approval rate | > 80% first submission | Quality submissions |

### CODEOWNERS
```
# .github/CODEOWNERS
# Global reviewers
*                       @team-leads

# Service-specific owners
/services/auth/         @auth-team
/services/payments/     @payments-team
/infrastructure/        @platform-team
/docs/                  @tech-writers

# Security-sensitive files
*.env*                  @security-team
**/auth/**              @security-team
**/migrations/**        @dba-team
```

## 4. Review Automation

### Pre-Review Automation (CI)
```yaml
# .github/workflows/pr-checks.yml
name: PR Checks
on: pull_request
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint
        run: npm run lint
      - name: Type check
        run: npm run typecheck
      - name: Unit tests
        run: npm test -- --coverage
      - name: Security scan
        run: npm audit --audit-level=high
      - name: PR size check
        uses: actions/github-script@v7
        with:
          script: |
            const { additions, deletions } = context.payload.pull_request;
            const total = additions + deletions;
            if (total > 800) {
              core.warning(`PR is ${total} lines — consider splitting`);
            }
```

### Automated Review Comments
```yaml
# danger.js or similar — auto-comment on PRs
- Warn if PR > 500 lines
- Warn if no tests added for new files
- Warn if TODO/FIXME added without ticket reference
- Fail if secrets detected (using gitleaks)
- Fail if lockfile modified without package.json change
```



---
