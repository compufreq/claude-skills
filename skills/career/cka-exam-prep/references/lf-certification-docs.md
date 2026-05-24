# Linux Foundation CKA Certification — Official Docs Snapshot

> **Source:** https://docs.linuxfoundation.org/tc-docs/certification
> **Key pages:**
> - Important Instructions CKA/CKAD: https://docs.linuxfoundation.org/tc-docs/certification/tips-cka-and-ckad
> - Resources Allowed: https://docs.linuxfoundation.org/tc-docs/certification/certification-resources-allowed
> - FAQ CKA/CKAD/CKS: https://docs.linuxfoundation.org/tc-docs/certification/faq-cka-ckad-cks
> - Candidate Handbook: https://docs.linuxfoundation.org/tc-docs/certification/lf-handbook2
> **Snapshot date:** March 2026
> **Note:** Always fetch the latest from the LF docs before relying on this file. This is a fallback only.

## Exam Details

- Online, performance-based tasks solved on the command line running Linux
- 15-20 performance-based tasks
- 2 hours to complete
- Proctored remotely via streaming audio, video, and screen sharing
- Results emailed within 24 hours of exam completion
- Zero-tolerance policy for exam misconduct — sessions are recorded and reviewed

## System Requirements

- Run the PSI Online Proctoring System Check before exam day: https://syscheck.bridge.psiexams.com/
- PSI Secure Browser is downloaded at exam launch time (not before)
- Supported OS: check PSI system requirements page
- Recommended: latest version of Google Chrome for scheduling
- ONE active monitor only (dual monitors NOT supported)
- Recommended: 15" or larger screen, 1080p resolution
- Reliable internet (wired preferred over wireless)
- HTTPS connectivity to AWS S3 endpoints required (https://*.s3.amazonaws.com/*)
- Working microphone and moveable webcam
- No other applications or browser windows allowed during exam
- Cannot use a virtual machine to take the exam

## Important Considerations

- Disable firewalls or use a computer without corporate firewall
- Must have admin privileges to install applications and end system processes
- Stop antivirus software during exam
- Plug in laptop to power (don't rely on battery)

## Acceptable Testing Location

- Clutter-free work area (nothing on desk surface except computer)
- Nothing below the testing surface (no paper, trash bins)
- Clear walls (paintings OK, no paper/printouts)
- Well-lit space (proctor must see face, hands, and work area)
- No bright lights or windows behind the candidate
- Candidate must remain within camera frame
- Private space with no excessive noise (no coffee shops, open offices)

## ID Requirements

- Valid (unexpired) government-issued original physical document
- Must include name, photo, and signature (biometric IDs without signature accepted)
- First and last name on ID must exactly match the verified name on exam checklist
- Acceptable: international passport, driver's license, national ID card, green card
- For Germany specifically: Personalausweis (national ID card) is accepted

## Resources Allowed During CKA Exam

Candidates may use the browser within the exam VM to access:

- **Kubernetes Documentation:** https://kubernetes.io/docs/
  (Search on kubernetes.io/docs is allowed, but must NOT follow external search results)
- **Kubernetes Blog:** https://kubernetes.io/blog/
- **Helm Documentation:** https://helm.sh/docs/
- **Gateway API Documentation:** https://gateway-api.sigs.k8s.io/ (CKA only)
- **Task-specific documentation** provided in the Quick Reference box within each question
- All available language translations of kubernetes.io (but English recommended as most up-to-date)
- Documents installed by the distribution (e.g., /usr/share and subdirectories)
- Packages that are part of the distribution (may install additional if needed)

**NOT allowed:**
- Any other websites or external resources
- External search engines
- Personal notes or bookmarks
- Multiple browser windows or applications

## Exam Environment Technical Instructions

1. Do NOT reboot the base node (hostname `base`) — it will NOT restart the exam environment
2. Use `Ctrl+Alt+W` instead of `Ctrl+W` (which closes the Chrome tab!)
3. Terminal copy/paste (Linux keyboard shortcuts):
   - Copy: `Ctrl+Shift+C`
   - Paste: `Ctrl+Shift+V`
   - Or use right-click context menu
4. Other applications on the Remote Desktop:
   - Copy: `Ctrl+C`
   - Paste: `Ctrl+V`
5. Locate cursor: `Ctrl+Alt+K`
6. Mouse, keyboard, accessibility settings can be customized via desktop icons
7. INSERT key is disabled — use `i` for vim insert mode, `Esc` to exit
8. International keyboard users: on-screen virtual keyboard available via desktop icon
9. Some system security policies may need modification to complete tasks

## CKA/CKAD Exam Environment Structure

- Must complete each task on a designated host
- An infobox at each task start provides SSH instructions to the designated host
- After completing a task: `exit` the SSH session to return to base
- Nested SSH is NOT supported
- SSH to hosts via: `ssh <nodename>`
- Elevated privileges: `sudo -i` or use `sudo` before commands
- Pre-installed tools on SSH hosts:
  - `kubectl` with `k` alias and Bash autocompletion already configured
  - `yq` for YAML processing
  - `curl` and `wget` for testing web services
  - `man` and man pages
- The base system does NOT have these tools — all tasks must be done on designated SSH hosts
- Exam environment runs the latest Kubernetes version (aligned within 4-8 weeks of K8s release)

## ExamUI Tips

- Use "+" / "-" buttons on PSI Secure Browser toolbar to zoom in/out
- Firefox browser window can be maximized/minimized
- Content Panel (left side with exam items) can be resized by dragging the border
- Use `Ctrl+F` in Firefox to search within the documentation page
- Resize Firefox so you can see the full browser window before using Find
- PSI Secure Browser can be maximized to full screen
- Use the toggle to shrink the toolbar for more screen real estate

## KillerKoda Resources

### CKA Scenarios (https://killercoda.com/cka)

Known scenario challenges mapped to CKA domains:

**Storage (10%):**
- Challenge 01: Persistent Volume
- Challenge 06: Storage Class & Persistent Volume
- Challenge 13: PV Troubleshooting

**Troubleshooting (30%):**
- Challenge 07: Deployment & Troubleshooting
- Challenge 10: ConfigMap and Deployment Troubleshooting
- Challenge 16: Node Troubleshooting

**Workloads & Scheduling (15%):**
- Challenge 09: Deployment Scaling & Update
- Challenge 15: Rollout and Rollback
- Challenge 19: Deployment Strategy

**Cluster Architecture (25%):**
- Challenge 04: ETCD Backup & Restore
- Challenge 05: Service Account & RBAC
- Challenge 08: Kubernetes Upgrade
- Challenge 20: RBAC
- Challenge 21: Install Redis Using Helm

**Services & Networking (20%):**
- Challenge 02: Drain Nodes
- Challenge 03: Service
- Challenge 11: Troubleshoot Network Policy
- Challenge 12: Ingress
- Challenge 14: Pod Deployment
- Challenge 17: Service
- Challenge 18: Network Policy

### Additional KillerKoda Resources

- **Killer Shell CKA:** https://killercoda.com/killer-shell-cka — standalone scenarios from killer.sh
- **CKA Playground:** https://killercoda.com/playgrounds/scenario/cka — open-ended practice environment
- **Exam Remote Desktop:** https://killercoda.com/linux-foundation-exam-remote-desktop — practice in
  an environment that mimics the real exam's remote desktop setup (very useful for getting comfortable
  with the exam UI before exam day)
