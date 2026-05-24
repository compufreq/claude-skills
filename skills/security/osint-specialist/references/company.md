# Company / Organization OSINT Reference

## Corporate Registry Lookups

### Germany
- **Handelsregister**: `web_search "Company Name" Handelsregister`
  - `web_fetch https://www.handelsregister.de` — search for company filings
  - Reveals: legal form, registered address, managing directors, Stammkapital
- **Bundesanzeiger**: `web_search "Company Name" site:bundesanzeiger.de`
  - Annual financial statements (Jahresabschluss) for GmbHs
- **North Data**: `web_search "Company Name" site:northdata.de`
  - Free aggregator of German company data, relationships, financials

### International
- **UK**: Companies House — `web_fetch https://find-and-update.company-information.service.gov.uk/search/companies?q=COMPANY`
- **US**: SEC EDGAR — `web_search "Company Name" site:sec.gov`
  - `web_fetch https://efts.sec.gov/LATEST/search-index?q="Company Name"&dateRange=custom&startdt=2024-01-01`
- **EU**: European Business Register — `web_search "Company Name" business register [country]`
- **OpenCorporates**: `web_fetch https://api.opencorporates.com/v0.4/companies/search?q=COMPANY`

### What to Extract
- Legal entity name and type
- Registration number
- Registered address vs operational address
- Directors, officers, shareholders
- Date of incorporation
- Financial summaries (revenue, profit, capital)
- Related companies (subsidiaries, parent companies)
- Filing history (reveals changes, restructuring)

## Employee Enumeration

### LinkedIn Mining
- `site:linkedin.com/in "Company Name"` — find current employees
- `site:linkedin.com/in "Company Name" "engineer" OR "developer"` — filter by role
- `site:linkedin.com/in "Company Name" "security" OR "infosec" OR "CISO"` — find security team
- `site:linkedin.com/in "Company Name" "IT" OR "system administrator"` — find IT staff
- Note job titles, reporting structures, and team sizes

### Job Postings Intelligence
Job postings reveal enormous amounts about internal infrastructure:
- `web_search "Company Name" hiring OR careers OR jobs`
- `site:linkedin.com/jobs "Company Name"`
- `site:indeed.com "Company Name"`
- `site:glassdoor.com "Company Name"`

**Extract from job postings:**
- Tech stack (languages, frameworks, databases, cloud providers)
- Security tools in use (SIEM, EDR, firewall vendors)
- Team structures and sizes
- Office locations
- Compliance requirements (PCI, SOC2, ISO 27001 — reveals maturity)
- Salary ranges (budget indicators)

### Email Harvesting
Once you know the email format:
- Combine employee names from LinkedIn with the email format
- Search `"@company.com"` for exposed emails
- Check GitHub commits: `"@company.com" site:github.com`
- Check mailing list archives

### Kali Follow-up
```bash
theHarvester -d company.com -b all -l 500
# LinkedIn enumeration (requires auth)
linkedin2username -c "Company Name" -n 3
# Metadata extraction from public documents
metagoofil -d company.com -t pdf,doc,xls,ppt -l 200 -o ./metadata/
```

## Digital Footprint Mapping

### Web Presence
1. Main website analysis (technology, hosting, structure)
2. Subdomain enumeration (see infrastructure reference)
3. Social media accounts:
   - `"Company Name" site:twitter.com OR site:facebook.com OR site:instagram.com`
   - `"Company Name" site:youtube.com`
   - `"Company Name" site:tiktok.com`
4. Developer presence:
   - `org:companyname site:github.com` — official repos
   - `"Company Name" site:github.com` — mentions in other repos
   - `"@company.com" site:github.com` — employee commits
5. App store presence:
   - `"Company Name" site:play.google.com`
   - `"Company Name" site:apps.apple.com`

### Third-Party Mentions
- Press releases: `"Company Name" press release OR announcement`
- News: `"Company Name" news`
- Reviews: `"Company Name" site:trustpilot.com OR site:g2.com`
- Legal: `"Company Name" lawsuit OR court OR litigation`
- Government contracts: `"Company Name" contract OR tender OR procurement`

### Supply Chain & Partners
- `"Company Name" partner OR partnership OR integration`
- Check their website for partner/customer logos
- Search for shared infrastructure (same IP ranges, same hosting)
- API documentation reveals third-party integrations

## Financial Intelligence

### Public Companies
- SEC filings (10-K, 10-Q, 8-K, proxy statements)
- Investor relations pages on company website
- Analyst reports: `"Company Name" analyst report OR earnings`
- Stock data and market cap

### Private Companies
- Bundesanzeiger (Germany) — mandatory financial filings for GmbHs
- Crunchbase: `web_search "Company Name" site:crunchbase.com`
  - Funding rounds, investors, valuation estimates
- PitchBook mentions: `"Company Name" funding OR investment OR raised`
- Import/export records: `"Company Name" import export records`

### Financial Red Flags to Note
- Rapid leadership changes
- Unusual corporate structure (many shell companies)
- Discrepancies between claimed revenue and filed financials
- Related party transactions
- Offshore subsidiaries in tax havens

## Organizational Structure

### Mapping the Org
- **Executive team**: Usually on company website `/about` or `/team` page
- **Board of directors**: Corporate filings, annual reports
- **Department structure**: Inferred from LinkedIn job titles and reporting lines
- **Key personnel changes**: `"Company Name" "appointed" OR "hired" OR "joined"`
- **Departures**: `"Company Name" "departed" OR "resigned" OR "left"`

### Relationship Mapping
- Directors who sit on multiple boards (cross-reference names across registries)
- Shared addresses between companies
- Common investors or shareholders
- Vendor/supplier relationships revealed in job postings or press releases
