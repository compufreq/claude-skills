# Infrastructure / Network OSINT Reference

## Domain Investigation

### DNS Enumeration
Use `kali_dns_enum` MCP tool for each record type:

- `kali_dns_enum(domain="target.com", record_type="A")`
- `kali_dns_enum(domain="target.com", record_type="AAAA")`
- `kali_dns_enum(domain="target.com", record_type="MX")`
- `kali_dns_enum(domain="target.com", record_type="TXT")`
- `kali_dns_enum(domain="target.com", record_type="NS")`
- `kali_dns_enum(domain="target.com", record_type="SOA")`

For operations not covered by the dedicated tool, use `kali_shell`:
```bash
# Reverse DNS
dig -x <IP_ADDRESS> +short

# DNS zone transfer attempt (often blocked but worth trying)
dig axfr target.com @ns1.target.com

# Check for DNSSEC
dig target.com DNSKEY +short
```

### WHOIS Lookup
Use `kali_whois` MCP tool:
- `kali_whois(target="target.com")` for domains
- `kali_whois(target="<IP_ADDRESS>")` for IPs

Key fields to extract from WHOIS:
- Registrant name, org, email (if not privacy-protected)
- Registration and expiry dates
- Name servers (reveal hosting provider)
- Registrar (reveals where domain was purchased)

If WHOIS is privacy-protected, note the privacy service and try:
- Historical WHOIS via web_search `"target.com" whois history`
- Check if other domains share the same privacy service contact

### Subdomain Discovery

**Passive techniques (use these first):**

1. **Certificate Transparency logs** — the single best passive source:
   ```
   web_fetch https://crt.sh/?q=%.target.com&output=json
   ```
   Parse the JSON for unique subdomain names.

2. **Google dorking**:
   - `site:target.com -www`
   - `site:*.target.com`

3. **Web search for subdomain lists**:
   - `"target.com" subdomains`
   - `site:dnsdumpster.com "target.com"`

4. **Shodan MCP** — search for SSL certificates:
   - Use `search_shodan` with query: `ssl.cert.subject.cn:target.com`
   - Or: `hostname:target.com`

5. **Security crawlers**:
   - `web_fetch https://otx.alienvault.com/api/v1/indicators/domain/target.com/passive_dns`
   - `web_fetch https://api.hackertarget.com/hostsearch/?q=target.com`

### Active Subdomain Brute-Force via MCP
Use `kali_gobuster` in DNS mode:
- `kali_gobuster(target_url="target.com", mode="dns", wordlist="/usr/share/wordlists/dirb/common.txt")`

### Kali Shell Follow-up (if installed in container)
```bash
# Comprehensive passive enumeration
amass enum -passive -d target.com -o amass_results.txt
subfinder -d target.com -all -o subfinder_results.txt

# DNS brute force with custom wordlists
dnsenum target.com
fierce --domain target.com --subdomains subdomains.txt
```

## IP Address Investigation

### Basic IP Recon
Use kali-tools MCP:
- `kali_whois(target="<IP>")` — IP block ownership
- `kali_nmap_scan(target="<IP>", options="--top-ports 100 -sV")` — quick service scan
- `kali_dns_enum(domain="<reverse-dns>", record_type="A")` — verify reverse DNS

Via `kali_shell`:
```bash
# Reverse DNS
dig -x <IP> +short
host <IP>
```

### Shodan Deep Dive
Use the Shodan MCP tools (load via `tool_search` first):

1. **get_host_info** — get full service/port details for an IP
   - Open ports and services
   - Software versions and banners
   - SSL certificate details
   - Known vulnerabilities (CVEs)
   - Organization and ISP info

2. **search_shodan** — find related hosts
   - `org:"Organization Name"` — all hosts belonging to an org
   - `net:x.x.x.0/24` — scan a CIDR range
   - `ssl.cert.subject.cn:target.com` — hosts with matching SSL certs
   - `http.title:"Admin Panel"` — find specific web applications
   - `port:22 org:"Target Org"` — find specific services
   - `product:"Apache" org:"Target Org"` — find specific software

3. **scan_network_range** — enumerate a subnet

### IP-to-Infrastructure Mapping
From an IP, determine:
- **Hosting provider**: WHOIS org field, or search `"<IP>" hosting provider`
- **Shared hosting**: `web_search "site:<IP>"` or Shodan reverse DNS
- **CDN detection**: If IP belongs to Cloudflare/Akamai/AWS CloudFront, the real IP may be hidden
  - Check DNS history for pre-CDN records
  - Check for direct IP leaks in email headers (MX records)
  - Search `"target.com" real IP` or check historical DNS records

### Deep Scan via MCP (active — touches target)
```
kali_nmap_scan(target="<IP>", options="-sV -sC -p-", timeout=600)     # full port scan
kali_nmap_scan(target="<IP>", options="-sU --top-ports 100", timeout=300)  # UDP
kali_nmap_scan(target="<IP>", options="-O", timeout=120)                    # OS fingerprint
kali_nmap_scan(target="<IP>", options="--script vuln", timeout=300)         # vuln scan
```

## Web Technology Fingerprinting

### Via kali-tools MCP
Use `kali_whatweb` as the primary fingerprinting tool:
- `kali_whatweb(target_url="https://target.com", aggression=1)` — stealthy first pass
- `kali_whatweb(target_url="https://target.com", aggression=3)` — aggressive if needed

Also check for WAF:
- `kali_waf_detect(target_url="https://target.com")`

### Via web_fetch
Fetch the target homepage and analyze:
- HTTP response headers (Server, X-Powered-By, X-Generator)
- HTML source for framework signatures (React, Angular, WordPress, etc.)
- JavaScript library references
- CSS framework classes
- Meta generator tags
- Cookie names (reveal backend frameworks)

### Via web_search
- `builtwith.com target.com` — technology profile
- `site:wappalyzer.com target.com`
- Look for `robots.txt`, `sitemap.xml`, `.well-known/` endpoints

### Deeper Scanning via MCP
```
kali_nikto_scan(target_url="https://target.com", timeout=300)  # vulnerability scan
kali_gobuster(target_url="https://target.com", mode="dir")     # directory enumeration
```

## Email Infrastructure Analysis

Use `kali_dns_enum` for email-related records:
- `kali_dns_enum(domain="target.com", record_type="MX")` — mail servers
- `kali_dns_enum(domain="target.com", record_type="TXT")` — SPF, DMARC, DKIM

For specific DMARC/DKIM records, use `kali_shell`:
```bash
# DMARC policy
dig _dmarc.target.com TXT +short

# DKIM (try common selectors)
dig default._domainkey.target.com TXT +short
dig google._domainkey.target.com TXT +short
dig selector1._domainkey.target.com TXT +short
```

SPF records are goldmines — they list all IP ranges authorized to send email,
often revealing cloud providers, marketing platforms, and third-party services.

## Historical Data

- **Wayback Machine**: `web_fetch https://web.archive.org/web/*/target.com`
  - Look for old pages that reveal removed content, old employee lists, deprecated services
- **Historical DNS**: Search `"target.com" dns history securitytrails OR viewdns`
- **Cached pages**: `cache:target.com` in Google search
- **Google dorking for old content**: `site:target.com inurl:old OR inurl:backup OR inurl:archive`

## SSL/TLS Certificate Analysis

Certificates reveal organizational relationships, subdomain structure, and infrastructure connections.

Via `kali_shell`:
```bash
echo | openssl s_client -connect target.com:443 -servername target.com 2>/dev/null | openssl x509 -text -noout
```

Also fetch from crt.sh for historical certificates — they show every subdomain that ever had a cert issued.
