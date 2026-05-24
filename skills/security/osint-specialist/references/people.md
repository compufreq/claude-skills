# People / Identity OSINT Reference

## Username Investigation

### Cross-Platform Enumeration
Search for a username across multiple platforms in this order:

1. **Web search**: `"username"` — find all indexed mentions
2. **Social platforms**: Search each major platform
   - `site:github.com "username"`
   - `site:reddit.com/user "username"`
   - `site:twitter.com "username"` or `site:x.com "username"`
   - `site:instagram.com "username"`
   - `site:linkedin.com/in "username"`
   - `site:medium.com/@username`
   - `site:keybase.io "username"`
3. **Developer platforms**:
   - `site:stackoverflow.com/users "username"`
   - `site:hub.docker.com/u "username"`
   - `site:gitlab.com "username"`
   - `site:npmjs.com/~username`
   - `site:pypi.org/user/username`
4. **Gaming/Community**:
   - `site:steamcommunity.com "username"`
   - `site:discord.me "username"` or Discord server searches
   - `site:twitch.tv "username"`

### Username Variations
People reuse patterns. If you find `johndoe123`, also check:
- `johndoe`, `john_doe`, `john-doe`, `jdoe123`
- `johndoe123` + common suffixes (`_dev`, `_official`, `_real`)
- Same pattern on email: `johndoe123@gmail.com`, `johndoe123@protonmail.com`

### Kali Follow-up
```bash
sherlock "username" --timeout 10 --print-found
# For bulk username lists:
sherlock --input usernames.txt --output results/
```

## Email Investigation

### Email Discovery
1. Search `"email@domain.com"` for public mentions
2. Search `"email@domain.com" site:pastebin.com OR site:ghostbin.com` for paste exposure
3. Search `"email@domain.com" site:github.com` for code commits with email
4. Check breach exposure: `web_fetch https://haveibeenpwned.com/api/v3/breachedaccount/{email}`
   (Note: API may require key — fall back to web search `"email" haveibeenpwned` or suggest manual check)

### Email-to-Person Correlation
- Check Gravatar: `https://www.gravatar.com/{md5_of_email}`
- Search LinkedIn: `"email@domain.com" site:linkedin.com`
- Check GitHub commits: `"email@domain.com" site:github.com`
- Google the email with quotes to find registrations, forum posts, mailing lists

### Email Format Discovery (for organizations)
Find the naming convention:
- Search `"@target.com"` to find exposed emails
- Check LinkedIn employees + common patterns: `first.last@`, `flast@`, `firstl@`
- Use `web_fetch` on Hunter.io or similar: `https://hunter.io/search/target.com` (may need manual check)

### Kali Follow-up
```bash
theHarvester -d target.com -b all -l 500
# Email verification
smtp-user-enum -M VRFY -U users.txt -t mail.target.com
```

## Phone Number Investigation

Phone OSINT is primarily web-search driven. Don't waste time with infrastructure tools
(nmap, dns_enum, etc.) — they're irrelevant for phone numbers.

### Step 1: Identify the Number
Determine country, carrier, and number type from the prefix:
- Search `web_search "[prefix] UK mobile network"` or equivalent for the country
- UK mobile: 07xxx = mobile (077 = O2, 074/075 = Vodafone, 07 = various)
- Note: number portability means carrier from prefix is original issuer only

### Step 2: Search All Formats
Search the number in every common format — results differ by format:
- International with plus: `"+447731375483"`
- International without plus: `"447731375483"`
- National format: `"07731375483"`
- Spaced format: `"07731 375483"`
- Hyphenated: `"07731-375483"`

### Step 3: Reverse Phone Lookup Services
Use `web_search` to find the number on these services, then `web_fetch` the results page:
- **UK**: who-called.co.uk, whocalled.co.uk, tellows.co.uk, unknownphone.com
- **Germany**: Das Örtliche (dasoertliche.de), Telefonbuch (telefonbuch.de), tellows.de
- **US**: whitepages.com, truecaller.com, youmail.com
- **International**: sync.me, truecaller.com, numberway.com

Search pattern: `web_search "07731375483 who called"` or `web_search "07731375483" site:tellows.co.uk`

### Step 4: Social Media & Messaging Platform Checks

**Social media search:**
- Search `"07731375483" site:facebook.com OR site:instagram.com OR site:twitter.com`
- Search `"+447731375483" WhatsApp OR Telegram OR Signal`

**WhatsApp — ACTIVE CHECK via kali_shell:**
Use curl to probe the wa.me shortlink. A registered number returns HTTP 200 and redirects
to `api.whatsapp.com/send/`. An unregistered number returns a different response.

```bash
kali_shell: curl -sL -o /dev/null -w '%{http_code} %{url_effective}' https://wa.me/<number_without_plus>
```
Example: `curl -sL -o /dev/null -w '%{http_code} %{url_effective}' https://wa.me/447731375483`

- **HTTP 200 + redirect to api.whatsapp.com/send/?phone=...** → number IS on WhatsApp
- **Other response** → number is NOT on WhatsApp or link is broken

This is a key check — always run it for phone number investigations. WhatsApp has 2+ billion
users, so the probability of a hit is very high.

After confirming WhatsApp registration, suggest the user manually check for:
- Profile photo (may reveal face, identity, or interests)
- About/Status text (may contain name, job, or personal info)
- Last seen / online status (activity patterns)

**Telegram — ACTIVE CHECK via kali_shell:**
Telegram's t.me shortlink can also be probed, but only for usernames, not phone numbers.
For phone-to-username mapping, suggest the user check manually in the Telegram app.

**Signal:** No programmatic check available — suggest manual verification.

### Step 5: Breach & Exposure Check
- Check HaveIBeenPwned (supports phone numbers): `web_search "447731375483" haveibeenpwned breach`
- Search paste sites: `"07731375483" site:pastebin.com OR site:github.com`
- Search for the number in data leak discussions: `"07731375483" breach OR leaked OR exposed`

### Step 6: Business/Service Association
- Search `"07731375483"` alone — may reveal business listings, classifieds, or ad postings
- Check Google Maps: `web_search "07731375483" maps OR business`
- Search classified sites: `"07731375483" site:gumtree.com OR site:ebay.co.uk`

### Manual Follow-up (suggest to user)
These require authentication or app access that Claude can't do directly:
- **Truecaller** (truecaller.com) — the #1 phone OSINT tool, shows caller ID and spam reports
- **Sync.me** (sync.me) — reverse lookup with social media profile matching
- **WhatsApp** — if registered (confirmed via wa.me check above), save as contact to view profile photo/About
- **Telegram** — search by phone number to find linked accounts and username
- **GetContact** — crowdsourced contact name database

## Real Name Investigation

1. Search `"First Last"` with quotes
2. Add location qualifiers: `"First Last" Berlin` or `"First Last" Germany`
3. Check LinkedIn: `site:linkedin.com/in "First Last"`
4. Check corporate pages: `"First Last" site:target-company.com`
5. Search public records / registries relevant to the country
6. Check academic publications: `"First Last" site:scholar.google.com OR site:researchgate.net`
7. Check social media with full name variations

## Social Media Deep Dive

Once you find a profile, extract maximum intelligence:

### GitHub
- Fetch the profile: `web_fetch https://api.github.com/users/{username}`
- Check repos for leaked secrets: `web_search "{username}" site:github.com password OR secret OR token OR api_key`
- Check commit emails: `web_fetch https://api.github.com/users/{username}/events/public`
- Review starred repos for interest/tech stack mapping

### LinkedIn (via web search — direct scraping blocked)
- `site:linkedin.com/in "Full Name" "Company"` for specific person
- Extract job history, skills, education, connections
- Job postings from their company reveal tech stack

### Reddit
- `site:reddit.com/user/{username}` for post history
- Cross-reference subreddits for interest mapping
- Check for personal info leaks in comments

## Breach Data Correlation

When checking for breaches:
1. Use web_search for `"email" breach OR leaked OR exposed OR dump`
2. Try `web_fetch https://haveibeenpwned.com/api/v3/breachedaccount/{email}` (may need API key)
3. **Phone numbers**: HIBP also supports phone lookups — search `"phone_number" haveibeenpwned`
   or try the API with the phone in E.164 format (e.g., +447731375483)
4. Note which breaches the target appeared in — this reveals which services they use
5. Cross-reference breach dates with password change patterns
6. Check if leaked passwords follow patterns that suggest reuse
