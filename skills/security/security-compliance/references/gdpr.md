# GDPR Technical Controls Reference

## Key GDPR Articles → Technical Implementation

| Article | Requirement | Technical Control |
|---------|------------|------------------|
| **Art. 5** | Data minimization | Collect only needed fields, auto-delete after purpose |
| **Art. 6** | Lawful basis | Consent management system, legitimate interest records |
| **Art. 7** | Consent | Granular consent UI, audit log, easy withdrawal |
| **Art. 15** | Right of access (SAR) | Data export API, automated SAR workflow |
| **Art. 17** | Right to erasure | Deletion API, cascade delete across services, crypto-shredding |
| **Art. 20** | Data portability | JSON/CSV export endpoint |
| **Art. 25** | Privacy by design | PIA process, defaults to private, data minimization |
| **Art. 30** | Processing records | Automated data flow mapping, processing registry |
| **Art. 32** | Security measures | Encryption, access control, pseudonymization |
| **Art. 33** | Breach notification | 72-hour notification process, incident response plan |
| **Art. 35** | DPIA | Impact assessment template, risk scoring |

## Technical Implementation

### Data Subject Rights API
```python
# Right to Access (SAR)
@app.route("/api/privacy/export", methods=["POST"])
@login_required
def export_data():
    user_id = current_user.id
    data = {
        "profile": UserService.get_profile(user_id),
        "orders": OrderService.get_orders(user_id),
        "activity_log": ActivityService.get_logs(user_id),
        "consent_records": ConsentService.get_records(user_id),
    }
    # Queue async export for large datasets
    ExportJob.create(user_id=user_id, data=data, format="json")
    return {"status": "processing", "message": "Export will be emailed within 24 hours"}

# Right to Erasure
@app.route("/api/privacy/delete", methods=["POST"])
@login_required
def delete_data():
    user_id = current_user.id
    # Soft-delete with 30-day grace period
    DeletionJob.create(user_id=user_id, execute_after=datetime.utcnow() + timedelta(days=30))
    # Immediately anonymize PII
    UserService.anonymize(user_id)
    return {"status": "scheduled", "message": "Data will be permanently deleted in 30 days"}
```

### Data Encryption & Pseudonymization
```python
# Field-level encryption for PII
from cryptography.fernet import Fernet

class EncryptedField:
    def __init__(self, key):
        self.cipher = Fernet(key)

    def encrypt(self, value: str) -> str:
        return self.cipher.encrypt(value.encode()).decode()

    def decrypt(self, token: str) -> str:
        return self.cipher.decrypt(token.encode()).decode()

# Pseudonymization (reversible with key)
import hashlib, hmac
def pseudonymize(value: str, key: bytes) -> str:
    return hmac.new(key, value.encode(), hashlib.sha256).hexdigest()[:16]

# Anonymization (irreversible)
def anonymize_email(email: str) -> str:
    return f"deleted-{uuid.uuid4().hex[:8]}@anonymized.invalid"
```

### Consent Management
```python
class ConsentRecord(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String, nullable=False)
    purpose = db.Column(db.String, nullable=False)  # "marketing", "analytics", "essential"
    granted = db.Column(db.Boolean, nullable=False)
    granted_at = db.Column(db.DateTime)
    withdrawn_at = db.Column(db.DateTime)
    ip_address = db.Column(db.String)
    user_agent = db.Column(db.String)
    consent_text_version = db.Column(db.String)  # Track which version they agreed to
```

### Breach Notification Workflow
```
Detection (automated/manual)
  → Assess severity (within 1 hour)
    → If personal data affected:
      → Notify DPO (immediately)
      → Document: what data, how many subjects, likely impact
      → Notify supervisory authority (within 72 hours)
      → If high risk to individuals: notify data subjects
      → Post-incident review, update controls
```

### Data Retention Policy Template

| Data Category | Retention Period | Legal Basis | Deletion Method |
|-------------|-----------------|-------------|----------------|
| User account data | Account lifetime + 30 days | Contract | Soft delete → hard delete |
| Transaction records | 7 years | Legal obligation (tax) | Archive → delete |
| Support tickets | 3 years after resolution | Legitimate interest | Anonymize |
| Marketing consent | Until withdrawn + 1 year | Consent | Delete |
| Access logs | 90 days | Legitimate interest | Auto-purge |
| Analytics data | 26 months | Consent | Anonymize |

### DPIA (Data Protection Impact Assessment) Checklist
- [ ] What personal data is processed?
- [ ] What is the lawful basis?
- [ ] Is the processing necessary and proportionate?
- [ ] What are the risks to data subjects?
- [ ] What measures mitigate those risks?
- [ ] Have data subjects been consulted?
- [ ] Has the DPO reviewed this assessment?



---
