# Python Backend Patterns for HTMX

## Table of Contents
1. [Flask](#flask)
2. [Django](#django)
3. [FastAPI](#fastapi)
4. [Common Patterns](#common-patterns)

---

## Flask

### Detecting HTMX Requests
```python
from flask import Flask, request, render_template, render_template_string

app = Flask(__name__)

def is_htmx_request():
    return request.headers.get("HX-Request") == "true"
```

### Returning Fragments vs Full Pages
```python
@app.route("/contacts")
def contacts():
    contacts = get_contacts(request.args.get("q", ""))
    if is_htmx_request():
        # Return just the fragment
        return render_template("partials/contact_list.html", contacts=contacts)
    # Return the full page
    return render_template("contacts.html", contacts=contacts)
```

### Response Headers
```python
from flask import make_response

@app.route("/item", methods=["POST"])
def create_item():
    item = save_item(request.form)
    response = make_response(render_template("partials/item_row.html", item=item))
    # Trigger a client-side event
    response.headers["HX-Trigger"] = "itemAdded"
    # Push URL to history
    response.headers["HX-Push-Url"] = f"/items/{item.id}"
    return response
```

### Validation Errors (422 Pattern)
```python
@app.route("/register", methods=["POST"])
def register():
    errors = validate_registration(request.form)
    if errors:
        return render_template("partials/form_errors.html", errors=errors), 422
    user = create_user(request.form)
    return render_template("partials/success.html", user=user)
```

### Out-of-Band Swaps
```python
@app.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    cart = add_item_to_cart(product_id)
    return render_template_string("""
        {{ cart_items_partial }}
        <span id="cart-count" hx-swap-oob="true">{{ cart.count }}</span>
    """, cart_items_partial=render_template("partials/cart_items.html", cart=cart),
         cart=cart)
```

### Flask + Jinja2 Template Organization
```
templates/
├── base.html              # Full page layout
├── contacts.html           # Full page (extends base)
└── partials/
    ├── contact_list.html   # Fragment: list of contacts
    ├── contact_row.html    # Fragment: single contact row
    ├── form_errors.html    # Fragment: validation errors
    └── search_results.html # Fragment: search results
```

### Flask-HTMX Extension
```python
# pip install flask-htmx
from flask_htmx import HTMX

htmx = HTMX(app)

@app.route("/contacts")
def contacts():
    contacts = get_contacts()
    if htmx:
        return render_template("partials/contact_list.html", contacts=contacts)
    return render_template("contacts.html", contacts=contacts)
```

### SSE with Flask
```python
import json
from flask import Response

@app.route("/events")
def events():
    def stream():
        while True:
            data = get_next_update()
            yield f"event: message\ndata: {data}\n\n"
    return Response(stream(), mimetype="text/event-stream")
```

---

## Django

### Detecting HTMX Requests
```python
# Using django-htmx (recommended)
# pip install django-htmx

# settings.py
MIDDLEWARE = [
    ...
    "django_htmx.middleware.HtmxMiddleware",
]

# views.py
def contact_list(request):
    contacts = Contact.objects.all()
    if request.htmx:
        return render(request, "partials/contact_list.html", {"contacts": contacts})
    return render(request, "contacts.html", {"contacts": contacts})
```

### Manual Detection (without django-htmx)
```python
def is_htmx(request):
    return request.headers.get("HX-Request") == "true"
```

### Class-Based Views with HTMX
```python
from django.views import View
from django.shortcuts import render

class ContactListView(View):
    def get(self, request):
        contacts = Contact.objects.filter(
            name__icontains=request.GET.get("q", "")
        )
        template = "partials/contact_list.html" if request.htmx else "contacts.html"
        return render(request, template, {"contacts": contacts})

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            response = render(request, "partials/contact_row.html", {"contact": contact})
            response["HX-Trigger"] = "contactAdded"
            return response
        return render(request, "partials/contact_form.html", {"form": form}, status=422)
```

### CSRF Token with HTMX
```html
<!-- Option 1: Include in every form (standard Django) -->
<form hx-post="/submit">
  {% csrf_token %}
  ...
</form>

<!-- Option 2: Set globally via hx-headers on body -->
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
  ...
</body>

<!-- Option 3: JavaScript for cookie-based CSRF -->
<script>
  document.body.addEventListener('htmx:configRequest', (e) => {
    e.detail.headers['X-CSRFToken'] = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
  });
</script>
```

### Django Template Partials Pattern
```python
# views.py
from django.template.response import TemplateResponse

class HtmxTemplateResponse(TemplateResponse):
    """Auto-selects partial template for HTMX requests."""

    def __init__(self, request, template, partial_template=None, *args, **kwargs):
        if request.htmx and partial_template:
            template = partial_template
        super().__init__(request, template, *args, **kwargs)
```

### Django + OOB Swaps
```python
from django.http import HttpResponse

def add_to_cart(request, product_id):
    cart = request.user.cart
    cart.add(product_id)

    cart_html = render_to_string("partials/cart_items.html", {"cart": cart}, request)
    badge_html = f'<span id="cart-count" hx-swap-oob="true">{cart.item_count}</span>'

    return HttpResponse(cart_html + badge_html)
```

---

## FastAPI

### Detecting HTMX Requests
```python
from fastapi import FastAPI, Request, Header
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/contacts", response_class=HTMLResponse)
async def contacts(request: Request, hx_request: str | None = Header(None, alias="HX-Request")):
    contacts = await get_contacts()
    template = "partials/contact_list.html" if hx_request else "contacts.html"
    return templates.TemplateResponse(template, {"request": request, "contacts": contacts})
```

### HTMX Dependency
```python
from fastapi import Depends

def is_htmx(hx_request: str | None = Header(None, alias="HX-Request")) -> bool:
    return hx_request == "true"

@app.get("/contacts")
async def contacts(request: Request, htmx: bool = Depends(is_htmx)):
    contacts = await get_contacts()
    template = "partials/contact_list.html" if htmx else "contacts.html"
    return templates.TemplateResponse(template, {"request": request, "contacts": contacts})
```

### Response Headers
```python
from fastapi.responses import HTMLResponse

@app.post("/items")
async def create_item(request: Request):
    form = await request.form()
    item = await save_item(form)
    content = templates.TemplateResponse(
        "partials/item_row.html",
        {"request": request, "item": item}
    )
    content.headers["HX-Trigger"] = "itemAdded"
    return content
```

### SSE with FastAPI
```python
from fastapi.responses import StreamingResponse
import asyncio

@app.get("/events")
async def events():
    async def stream():
        while True:
            data = await get_next_update()
            yield f"event: message\ndata: {data}\n\n"
            await asyncio.sleep(1)
    return StreamingResponse(stream(), media_type="text/event-stream")
```

### WebSocket with FastAPI
```python
from fastapi import WebSocket

@app.websocket("/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # Return HTML fragment
        html = f'<div id="messages" hx-swap-oob="beforeend"><p>{data}</p></div>'
        await websocket.send_text(html)
```

### Validation with Pydantic + 422
```python
from pydantic import BaseModel, EmailStr, ValidationError

class RegistrationForm(BaseModel):
    email: EmailStr
    password: str

@app.post("/register")
async def register(request: Request):
    form = await request.form()
    try:
        data = RegistrationForm(**form)
        user = await create_user(data)
        return templates.TemplateResponse("partials/success.html",
            {"request": request, "user": user})
    except ValidationError as e:
        return templates.TemplateResponse("partials/form_errors.html",
            {"request": request, "errors": e.errors()}, status_code=422)
```

---

## Common Patterns

### Redirect After POST (PRG with HTMX)
Instead of traditional Post-Redirect-Get, use `HX-Redirect` or `HX-Push-Url`:
```python
# Python (any framework)
response.headers["HX-Redirect"] = "/success"  # Full redirect
# or
response.headers["HX-Push-Url"] = "/items/42"  # Update URL, keep swap
```

### Polling Endpoint with Stop Signal
```python
@app.get("/job/{job_id}/status")
async def job_status(job_id: int, request: Request):
    job = await get_job(job_id)
    if job.completed:
        response = templates.TemplateResponse(
            "partials/job_complete.html", {"request": request, "job": job}
        )
        response.status_code = 286  # Stops HTMX polling
        return response
    return templates.TemplateResponse(
        "partials/job_progress.html", {"request": request, "job": job}
    )
```

### Server-Triggered Events (for Toast Notifications, etc.)
```python
import json

# Single event
response.headers["HX-Trigger"] = "showToast"

# Event with data
response.headers["HX-Trigger"] = json.dumps({
    "showToast": {"message": "Item saved!", "level": "success"}
})
```

Client-side listener:
```html
<body hx-on:showToast="showToastNotification(event.detail)">
```
