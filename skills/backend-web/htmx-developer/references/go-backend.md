# Go Backend Patterns for HTMX

## Table of Contents
1. [Standard Library (net/http)](#standard-library)
2. [Chi Router](#chi-router)
3. [Echo Framework](#echo-framework)
4. [Templating Patterns](#templating-patterns)
5. [Common Patterns](#common-patterns)

---

## Standard Library

### Detecting HTMX Requests
```go
package main

import (
    "net/http"
    "html/template"
)

func isHTMX(r *http.Request) bool {
    return r.Header.Get("HX-Request") == "true"
}
```

### Returning Fragments vs Full Pages
```go
var (
    baseTmpl    = template.Must(template.ParseFiles("templates/base.html", "templates/contacts.html"))
    partialTmpl = template.Must(template.ParseFiles("templates/partials/contact_list.html"))
)

func contactsHandler(w http.ResponseWriter, r *http.Request) {
    q := r.URL.Query().Get("q")
    contacts := searchContacts(q)

    data := map[string]any{"Contacts": contacts}

    if isHTMX(r) {
        partialTmpl.Execute(w, data)
        return
    }
    baseTmpl.ExecuteTemplate(w, "base.html", data)
}
```

### Response Headers
```go
func createItemHandler(w http.ResponseWriter, r *http.Request) {
    r.ParseForm()
    item := saveItem(r.Form)

    // Set HTMX response headers
    w.Header().Set("HX-Trigger", "itemAdded")
    w.Header().Set("HX-Push-Url", fmt.Sprintf("/items/%d", item.ID))

    partialTmpl.ExecuteTemplate(w, "item_row.html", item)
}
```

### Validation Errors (422)
```go
func registerHandler(w http.ResponseWriter, r *http.Request) {
    r.ParseForm()
    errors := validateRegistration(r.Form)

    if len(errors) > 0 {
        w.WriteHeader(422)
        errorsTmpl.Execute(w, map[string]any{"Errors": errors})
        return
    }

    user := createUser(r.Form)
    successTmpl.Execute(w, map[string]any{"User": user})
}
```

### Simple Server Setup
```go
func main() {
    mux := http.NewServeMux()

    // Serve static files
    mux.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir("static"))))

    // Routes
    mux.HandleFunc("GET /contacts", contactsHandler)
    mux.HandleFunc("POST /contacts", createContactHandler)
    mux.HandleFunc("PUT /contacts/{id}", updateContactHandler)
    mux.HandleFunc("DELETE /contacts/{id}", deleteContactHandler)

    http.ListenAndServe(":8080", mux)
}
```

---

## Chi Router

```go
package main

import (
    "net/http"
    "github.com/go-chi/chi/v5"
    "github.com/go-chi/chi/v5/middleware"
)

func main() {
    r := chi.NewRouter()
    r.Use(middleware.Logger)

    r.Get("/contacts", contactsHandler)
    r.Post("/contacts", createContactHandler)

    r.Route("/contacts/{contactID}", func(r chi.Router) {
        r.Get("/", getContactHandler)
        r.Get("/edit", editContactHandler)
        r.Put("/", updateContactHandler)
        r.Delete("/", deleteContactHandler)
    })

    http.ListenAndServe(":8080", r)
}

func getContactHandler(w http.ResponseWriter, r *http.Request) {
    id := chi.URLParam(r, "contactID")
    contact := findContact(id)

    if isHTMX(r) {
        renderPartial(w, "contact_detail.html", contact)
        return
    }
    renderPage(w, "contact.html", contact)
}
```

---

## Echo Framework

```go
package main

import (
    "net/http"
    "github.com/labstack/echo/v4"
)

func main() {
    e := echo.New()

    e.GET("/contacts", contactsHandler)
    e.POST("/contacts", createContactHandler)
    e.PUT("/contacts/:id", updateContactHandler)
    e.DELETE("/contacts/:id", deleteContactHandler)

    e.Start(":8080")
}

func contactsHandler(c echo.Context) error {
    q := c.QueryParam("q")
    contacts := searchContacts(q)

    if c.Request().Header.Get("HX-Request") == "true" {
        return c.Render(http.StatusOK, "partials/contact_list.html", contacts)
    }
    return c.Render(http.StatusOK, "contacts.html", contacts)
}

func createContactHandler(c echo.Context) error {
    contact := new(Contact)
    if err := c.Bind(contact); err != nil {
        c.Response().WriteHeader(422)
        return c.Render(422, "partials/errors.html", map[string]any{"Error": err.Error()})
    }
    saved := saveContact(contact)

    c.Response().Header().Set("HX-Trigger", "contactAdded")
    return c.Render(http.StatusOK, "partials/contact_row.html", saved)
}
```

---

## Templating Patterns

### Template Organization
```
templates/
├── base.html              # Full page layout with {{ block "content" . }}
├── contacts.html           # Full page (extends base)
└── partials/
    ├── contact_list.html   # Fragment: list of contacts
    ├── contact_row.html    # Fragment: single row
    ├── contact_form.html   # Fragment: edit form
    └── errors.html         # Fragment: validation errors
```

### Template Helper with Partials
```go
type Templates struct {
    pages    *template.Template
    partials *template.Template
}

func NewTemplates() *Templates {
    funcMap := template.FuncMap{
        "upper": strings.ToUpper,
    }

    return &Templates{
        pages: template.Must(
            template.New("").Funcs(funcMap).ParseGlob("templates/*.html"),
        ),
        partials: template.Must(
            template.New("").Funcs(funcMap).ParseGlob("templates/partials/*.html"),
        ),
    }
}

func (t *Templates) RenderPage(w http.ResponseWriter, name string, data any) {
    t.pages.ExecuteTemplate(w, name, data)
}

func (t *Templates) RenderPartial(w http.ResponseWriter, name string, data any) {
    t.partials.ExecuteTemplate(w, name, data)
}

func (t *Templates) Render(w http.ResponseWriter, r *http.Request, page, partial string, data any) {
    if isHTMX(r) {
        t.RenderPartial(w, partial, data)
        return
    }
    t.RenderPage(w, page, data)
}
```

### Using templ (Type-Safe Templates)

[templ](https://templ.guide/) is popular in the Go + HTMX community for type-safe HTML templates:

```go
// components/contact.templ
package components

templ ContactRow(contact Contact) {
    <tr id={ fmt.Sprintf("contact-%d", contact.ID) }>
        <td>{ contact.Name }</td>
        <td>{ contact.Email }</td>
        <td>
            <button hx-get={ fmt.Sprintf("/contacts/%d/edit", contact.ID) }
                    hx-target={ fmt.Sprintf("#contact-%d", contact.ID) }
                    hx-swap="outerHTML">
                Edit
            </button>
            <button hx-delete={ fmt.Sprintf("/contacts/%d", contact.ID) }
                    hx-confirm="Delete this contact?"
                    hx-target={ fmt.Sprintf("#contact-%d", contact.ID) }
                    hx-swap="outerHTML swap:500ms">
                Delete
            </button>
        </td>
    </tr>
}

templ ContactList(contacts []Contact) {
    for _, c := range contacts {
        @ContactRow(c)
    }
}
```

Usage in handler:
```go
func contactsHandler(w http.ResponseWriter, r *http.Request) {
    contacts := getContacts()
    if isHTMX(r) {
        components.ContactList(contacts).Render(r.Context(), w)
        return
    }
    components.ContactsPage(contacts).Render(r.Context(), w)
}
```

---

## Common Patterns

### HTMX Middleware
```go
// Middleware that adds HTMX-awareness to the request context
type HTMXInfo struct {
    IsHTMX     bool
    Target     string
    TriggerID  string
    TriggerName string
    CurrentURL string
    Boosted    bool
}

func HTMXMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        info := HTMXInfo{
            IsHTMX:      r.Header.Get("HX-Request") == "true",
            Target:      r.Header.Get("HX-Target"),
            TriggerID:   r.Header.Get("HX-Trigger"),
            TriggerName: r.Header.Get("HX-Trigger-Name"),
            CurrentURL:  r.Header.Get("HX-Current-URL"),
            Boosted:     r.Header.Get("HX-Boosted") == "true",
        }
        ctx := context.WithValue(r.Context(), "htmx", info)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

### SSE with Go
```go
func sseHandler(w http.ResponseWriter, r *http.Request) {
    flusher, ok := w.(http.Flusher)
    if !ok {
        http.Error(w, "Streaming not supported", http.StatusInternalServerError)
        return
    }

    w.Header().Set("Content-Type", "text/event-stream")
    w.Header().Set("Cache-Control", "no-cache")
    w.Header().Set("Connection", "keep-alive")

    for {
        select {
        case <-r.Context().Done():
            return
        case msg := <-messageChan:
            fmt.Fprintf(w, "event: message\ndata: %s\n\n", msg)
            flusher.Flush()
        }
    }
}
```

### WebSocket with Gorilla
```go
import "github.com/gorilla/websocket"

var upgrader = websocket.Upgrader{
    CheckOrigin: func(r *http.Request) bool { return true },
}

func wsHandler(w http.ResponseWriter, r *http.Request) {
    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil { return }
    defer conn.Close()

    for {
        _, msg, err := conn.ReadMessage()
        if err != nil { break }

        // Return HTML fragment
        html := fmt.Sprintf(`<div id="messages" hx-swap-oob="beforeend"><p>%s</p></div>`,
            template.HTMLEscapeString(string(msg)))
        conn.WriteMessage(websocket.TextMessage, []byte(html))
    }
}
```

### Out-of-Band Response Helper
```go
func renderWithOOB(w http.ResponseWriter, r *http.Request, main string, mainData any, oob ...OOBSwap) {
    // Render main content
    tmpl.RenderPartial(w, main, mainData)

    // Render each OOB element
    for _, swap := range oob {
        tmpl.RenderPartial(w, swap.Template, swap.Data)
    }
}

type OOBSwap struct {
    Template string
    Data     any
}

// Usage
func addToCartHandler(w http.ResponseWriter, r *http.Request) {
    cart := addToCart(r)
    renderWithOOB(w, r,
        "cart_items.html", cart,
        OOBSwap{"cart_badge_oob.html", map[string]int{"Count": cart.ItemCount}},
    )
}
```

### Trigger Events with JSON Data
```go
import "encoding/json"

func triggerEvent(w http.ResponseWriter, events map[string]any) {
    data, _ := json.Marshal(events)
    w.Header().Set("HX-Trigger", string(data))
}

// Usage
triggerEvent(w, map[string]any{
    "showToast": map[string]string{
        "message": "Contact saved!",
        "level":   "success",
    },
})
```

### Polling with Stop (286)
```go
func jobStatusHandler(w http.ResponseWriter, r *http.Request) {
    jobID := r.PathValue("id") // Go 1.22+
    job := getJob(jobID)

    if job.Completed {
        w.WriteHeader(286) // HTMX stops polling on 286
        tmpl.RenderPartial(w, "job_complete.html", job)
        return
    }
    tmpl.RenderPartial(w, "job_progress.html", job)
}
```
