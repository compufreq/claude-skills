---
name: job-hunter
description: >
  End-to-end job hunting assistant that finds matching jobs, refines or builds CVs from scratch,
  and writes tailored cover letters — all in ATS-compatible .docx and .pdf formats.
  Use this skill whenever the user mentions job search, job hunting, finding jobs, CV, résumé,
  resume, cover letter, application letter, ATS formatting, job matching, career search,
  job listings, applying for jobs, or anything related to preparing job application materials.
  Also trigger when the user uploads a CV or résumé for review, asks to improve their CV,
  wants help writing a cover letter for a specific role, or asks about job openings in a
  particular city, country, or field. Trigger even if the user doesn't say "job" explicitly
  but describes wanting to find work, switch careers, update their professional documents,
  or prepare application materials. This skill covers the full pipeline: job discovery →
  profile analysis → document creation → application-ready output.
---

# Job Hunter

A full-pipeline job hunting skill that helps users find matching jobs, build or refine their CV, and generate tailored cover letters — all optimized for Applicant Tracking Systems (ATS).

## Workflow Overview

The skill operates in four interconnected stages. The user may enter at any point — not everyone needs all four. Detect what the user needs and jump to the right stage.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  1. PROFILE      │ ──► │  2. CAREER       │ ──► │  3. JOB SEARCH   │ ──► │  4. DOCUMENTS    │
│  Understand the  │     │  ANALYSIS        │     │  Find matching   │     │  CV + Cover      │
│  user's skills   │     │  What roles fit   │     │  opportunities   │     │  Letter output   │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Stage 1: Profile Analysis

The goal here is to deeply understand who the user is professionally before doing anything else. The quality of job matching and document generation depends entirely on this step.

### If the user uploads an existing CV (and optionally a projects file)

1. Read the uploaded file(s) thoroughly. Supported formats: `.docx`, `.pdf`, `.md`, `.txt`, or any readable format.
   - Read the docx skill at `/mnt/skills/public/docx/SKILL.md` before processing `.docx` files.
   - Read the pdf-reading skill at `/mnt/skills/public/pdf-reading/SKILL.md` before processing `.pdf` files.
2. Extract and internalize:
   - **Contact info** (name, location, email, phone, LinkedIn, GitHub, portfolio)
   - **Professional summary / objective**
   - **Work experience** (titles, companies, durations, responsibilities, achievements)
   - **Technical and soft skills**
   - **Education and certifications**
   - **Projects** (from CV or a separate projects file — treat both as first-class sources)
   - **Languages spoken** (this matters for job search filtering later)
   - **Overall style profile**: tone (formal/conversational/technical), formatting patterns, vocabulary level, section structure. This profile drives cover letter generation later.
3. Provide the user with a brief summary of what you understood, highlighting:
   - Key strengths and top skills
   - Experience level (junior / mid / senior / lead / executive)
   - Any gaps or areas that could be improved
   - Ask if anything is missing or incorrect before proceeding.

### If the user has no CV (building from scratch)

Be flexible — some users will dump everything in one message, others prefer to be guided. Adapt to whichever approach the user takes.

**If the user wants step-by-step guidance**, walk through these areas one at a time:
1. Personal info (name, contact, location)
2. Professional summary — help them craft one based on their answers
3. Work experience (most recent first)
4. Education and certifications
5. Skills (technical + soft)
6. Projects and achievements
7. Languages spoken

**If the user provides everything at once**, parse it, organize it, confirm what you understood, and move on.

In either case, ask about their **target role/industry** — this shapes how the CV is framed.

**For from-scratch users, consider generating the CV immediately after profile gathering** — before moving to job search. This gives the user a tangible document to review and refine while searches run, and it confirms that their profile was captured correctly. The CV can always be further tailored once they pick a specific job from the results.

---

## Stage 2: Career Analysis

After completing the profile analysis (and before asking about job search criteria), provide the user with a **career fit analysis**. This is a crucial step that many job seekers find valuable — it shows them the full landscape of roles they qualify for, not just the one type they might have in mind.

### What to include:

1. **Primary role matches** — The job titles and role types that are the strongest fit for the user's current skill set and experience level. These are roles where the user could apply tomorrow with high confidence. Be specific: not just "Cloud Architect" but "Senior AWS Cloud Architect," "Platform Engineering Lead," "DevOps Team Lead," etc.

2. **Adjacent role opportunities** — Roles the user could transition into with minor upskilling or by leveraging transferable skills. Explain what bridge skills would be needed. For example: "Your AWS + Terraform background also positions you well for Site Reliability Engineer roles — the gap would be stronger observability tooling experience (Datadog, Prometheus)."

3. **Seniority assessment** — Where the user sits on the career ladder based on their years of experience, leadership history, and technical depth. Be honest: if someone has 3 years of experience, don't suggest Principal Architect roles.

4. **Industry fit** — Which industries value the user's specific combination of skills. A cloud architect with financial services experience has different options than one with healthcare experience.

5. **Market positioning summary** — A brief, honest assessment: "Your profile is highly competitive for X roles, competitive for Y roles, and would need growth in Z to reach W roles."

Present this analysis conversationally — not as a rigid report. The goal is to give the user a clear picture of their options before narrowing down the search. After presenting, ask if they want to focus the job search on any particular direction from the analysis.

---

## Stage 3: Job Search

### Gathering Search Criteria

Before searching, collect the filters below from the user. **Ask one topic per message** — don't bundle multiple questions into a single response. If the user already provided some of these in their earlier messages, acknowledge what you already know and only ask about what's missing. Move through them conversationally, not as a checklist.

**Pacing example**: After the career analysis, you might say "Let's narrow down the search. Which country are you targeting?" Then after they answer, "And is there a specific city, or are you open to anywhere in [country]?" — one topic at a time.

The filters to collect (in a natural order):

1. **Country** — Required. Which country to search in.
2. **City** — Optional. Specific city or region, or nationwide.
3. **Job type** — Remote, hybrid, on-site, or a combination (e.g., "remote or hybrid").
4. **User's language proficiency** — Ask what languages the user speaks and at what level (native, fluent, conversational, basic). This is different from the listing language filter — it determines which jobs the user actually qualifies for. Many listings require specific language skills (e.g., "German B2 required"), and results that demand a language the user doesn't speak must be filtered out.
5. **Listing language** — What language should the job listings and work environment be in? Default to English if not specified. A user who speaks basic German might still want English-only listings because they're not confident working in German.
6. **Salary range** — Ask for their expected annual salary range in local currency. This is important for filtering — don't skip it. Phrase it matter-of-factly: "What salary range are you targeting? This helps me filter out roles that wouldn't be a fit."
7. **Number of results** — How many matching jobs to return. Let the user decide.

### Searching for Jobs

Use web search to find jobs across major job boards and company career pages. Good sources include LinkedIn Jobs, Indeed, Glassdoor, StepStone, Monster, and country-specific boards. For **remote-only searches**, also check remote-focused boards: RemoteOK, WeWorkRemotely, remote.co, and Remotive — these often have better remote-specific coverage than general boards.

Search strategies:

1. Build search queries from the user's **top skills**, **job titles** from their experience, and **target role** if specified.
2. **Construct all search queries in the user's specified language.** If the user wants English-only listings, write queries in English and include language qualifiers like "English-speaking" or "English language" in the search terms. If they want German-language roles, search in German. This is the most effective way to filter by language since most job boards don't have reliable language filters in URL parameters.
3. Run multiple searches with varied queries to cast a wide net (e.g., search by job title, then by key skills, then by industry).
4. For each result, extract: job title, company, location, job type, salary (if listed), required skills, required experience, language requirements, and the listing URL.
5. **Verify language requirements from the actual posting**: For every potential result, use `web_fetch` to read the full job listing page. Scan the **entire** listing — not just the title or summary — for any language requirements. Look for all of these patterns and their variations:
   - Explicit requirements: "German required", "German B2", "Deutsch erforderlich", "Deutschkenntnisse", "fließend Deutsch", "German is a must", "must speak German", "Deutsch (mindestens B2)", "German language skills required"
   - Soft requirements that are actually hard: "German preferred", "German advantageous", "good German skills", "Deutsch von Vorteil" — these often mean the role operates in German day-to-day
   - Bilingual indicators: "German and English", "Deutsch/Englisch", listing written half in German
   - If the listing itself is written in German, that's a strong signal German is required for the role — even if it doesn't explicitly say so
   
   Compare every language demand against the user's stated language proficiency. If a listing requires a language the user doesn't speak at the required level, **exclude it** — no exceptions, even if everything else matches perfectly. When in doubt about whether "preferred" means "required," exclude the listing and explain in the results that a few borderline listings were removed due to potential German requirements.

6. **Verify the posting is current**: Check the posting date or "posted X days ago" indicator on each listing. **Exclude any job posted more than 30 days ago**, or any listing that shows signs of being expired (application closed, page returns 404, "this position has been filled" messages, or the listing redirects to a generic careers page). If no posting date is visible, look for contextual clues (e.g., "apply by [past date]"). Only include jobs that are actively open and recently posted. Stale listings waste the user's time and signal an unreliable search.

### Match Scoring

Score each job against the user's profile on a 0–100% scale using these weighted factors:

- **Skills match (40%)**: How many of the job's required/preferred skills does the user have?
- **Experience level (25%)**: Does the user's seniority match what the role asks for?
- **Job title alignment (20%)**: How closely does the role title match the user's current/past titles or target role?
- **Qualifications (15%)**: Required education, certifications, or specific credentials.

**Only present jobs scoring 80% or higher.** This keeps the list focused and actionable.

**If fewer results than requested meet the 80% threshold**, present what's available and explain why the pool is limited (e.g., niche role, restrictive language filter, narrow location). Then suggest concrete ways to broaden the search — for example, lowering the threshold to 70%, expanding from city-specific to nationwide, adding hybrid to a remote-only filter, or considering neighboring countries with similar job markets. Let the user decide whether to adjust.

### Presenting Results

Display results as a clear, scannable list. For each job include:

- **Match score** (e.g., "92% match")
- **Job title** and **Company**
- **Location** and **Job type** (remote/hybrid/on-site)
- **Posted date** (e.g., "Posted 3 days ago" or "Posted March 25, 2026")
- **Salary** (if available from the listing)
- **Language requirements** (what the listing actually demands)
- **Key matching skills** (what the user has that the job wants)
- **Gaps** (skills or qualifications the user is missing, if any)
- **Link** to the listing (see URL rules below)

**URL rules — every result must link to the job, no exceptions:**

- **Tier 1 (preferred): Direct URL** — A full, clickable URL that takes the user straight to the specific job posting. This is always the goal. Example: `https://nordcloud-career.breezy.hr/p/0b24dcda2ca601-senior-aws-cloud-architect`

- **Tier 2 (fallback): Closest URL + step-by-step navigation guide** — If a direct URL to the specific listing truly cannot be found (some company career pages use dynamic content or require login), provide the closest reachable URL (e.g., the company's careers page or a filtered search results page) **plus** a numbered, step-by-step guide to reach the specific posting. Example:
  ```
  Link: https://www.epam.com/careers/job-listings
  How to find it:
  1. Click "Location" filter → select "Germany"
  2. In the search box, type "Cloud Systems Architect"
  3. Look for "Cloud Systems Architect / Platform Architect (m/f/d)"
  4. The posting should show "Remote" under location
  ```

- **Never acceptable**: Vague instructions like "Search for X on Glassdoor" or "Filter for Y on StepStone" without a specific URL and clear steps. Every result must give the user a concrete path to the exact listing — either one click (Tier 1) or a URL plus a few guided steps (Tier 2).

Sort by match score, highest first. After presenting, ask the user which job(s) they'd like to apply to — this feeds into cover letter generation.

---

## Stage 4: Document Generation

### CV Refinement or Creation

Whether refining an existing CV or building from scratch, the output must be **ATS-compatible**. Read the ATS formatting reference at `references/ats-guidelines.md` before generating any document.

**Process:**
1. Read the docx skill at `/mnt/skills/public/docx/SKILL.md` — follow its instructions for creating `.docx` files.
2. Read the pdf skill at `/mnt/skills/public/pdf/SKILL.md` — follow its instructions for creating `.pdf` files.
3. Structure the CV following ATS guidelines (see reference file).
4. If refining an existing CV: preserve the user's style, tone, and vocabulary level while improving content, fixing formatting issues, and ensuring ATS compatibility.
5. If building from scratch: use a clean, professional, ATS-friendly template.
6. Tailor the CV toward the target role if one has been selected from the job search results.
7. Output both `.docx` and `.pdf` versions.

### Cover Letter Generation

The cover letter must feel like the same person wrote both their CV and the letter. This means matching:

- **Tone**: If the CV is formal and traditional, the cover letter should be too. If it's more modern and conversational, match that.
- **Formatting**: Mirror the CV's header style, font choices (within .docx constraints), and overall visual density.
- **Vocabulary level**: If the CV uses highly technical language, the cover letter should too. If it's accessible and non-jargon-heavy, keep the letter the same way.

**Process:**
1. Ask which job the cover letter is for (from the search results, or a job the user provides separately).
2. Extract key requirements and company info from the job listing (use web_fetch to read the full listing if needed).
3. Write a cover letter that:
   - Opens with genuine interest in the specific role and company (not generic)
   - Highlights 2–3 of the user's most relevant experiences/skills that map to the job's requirements
   - Addresses any notable gaps honestly but positively (e.g., "While my experience is primarily in X, my work on Y demonstrates transferable skills in Z")
   - Closes with a clear call to action
   - Stays within one page
4. Apply ATS formatting (see reference file).
5. Output both `.docx` and `.pdf` versions.

---

## Important Behavioral Notes

- **Don't rush the intake.** The profile analysis stage is the foundation. If the user's CV is vague or the projects file is sparse, ask clarifying questions. Better to spend time here than produce poor matches later.
- **Be transparent about match scoring.** If you're estimating and the data is incomplete (e.g., no salary listed on the job), say so.
- **Respect the user's voice.** When refining a CV or writing a cover letter, you're a ghostwriter — the output should sound like *them*, not like a generic template.
- **Handle partial workflows gracefully.** The user might only want a CV review, or only want a job search, or only need a cover letter for a job they already found. Don't force them through all four stages.
- **Language awareness.** If the user wants jobs in German, search in German. If they want a CV in English but jobs in French-speaking regions, handle that bilingual context. Always confirm language preferences before generating documents.
- **Salary is sensitive.** Ask for it matter-of-factly and don't judge the range. Use it purely for filtering.
