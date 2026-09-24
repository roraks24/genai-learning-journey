# Rorak V2 Roadmap

> **V2** will remain focused on making Rorak a durable, reliable knowledge product.
> **V3** will introduce the interactive/agentic layer.

## V2.1 — Foundation & Data Architecture

* Production database architecture
* PostgreSQL schema
* Users/workspaces data model
* Documents/conversations/memory models
* Ingestion-job model
* Strong API contracts
* Clean service/repository boundaries
* Preserve V1 compatibility

## V2.2 — Real Document Management

* Document library
* List/view documents
* Rename
* Delete
* Metadata
* File size/page count
* Chunk statistics
* Indexing status
* Processing status
* Failed ingestion + retry
* Correct document → chunks → vectors deletion
* Upload UX improvements
* Thick/comfortable scrollbar

## V2.3 — Conversational Memory & User Context

* Conversation sessions
* Persistent chat history
* Multi-turn context
* Reopen conversations
* Rename/delete conversations
* Thread-scoped memory
* Persistent memory
* User context
* User-scoped memory
* Workspace-scoped memory

## V2.4 — Trustworthy RAG

* Citation-aware RAG
* ChatGPT-style source references
* Document/page/chunk citations
* Source traceability
* Better grounding behavior
* Explicit General vs Grounded behavior
* No silent general-knowledge fallback in grounded mode
* Stronger context boundaries
* Citation correctness
* RAG stability

## V2.5 — Ingestion & Retrieval Expansion

* More document formats
* Larger file intake
* Increased document-count capacity
* Better chunking
* Improved ingestion pipeline
* Async ingestion
* Background processing
* Upload progress
* Processing jobs/status
* Retryable ingestion
* OCR/scanned-document support as appropriate

## V2.6 — Security & Multi-User Isolation

* Authentication
* Authorization
* User/workspace isolation
* Document isolation
* Conversation isolation
* Memory isolation
* Rate limiting
* Upload validation
* File-size limits
* MIME/type validation
* Filename/path safety
* Prompt-injection resistance
* Secret protection
* Abuse protection

## V2.7 — Reliability & Production Hardening

* Structured logging
* Request IDs
* Conversation/document/job IDs
* Health/readiness checks
* Error handling
* Retry/recovery mechanisms
* Database migrations
* Backup/restore
* Regression testing
* RAG evaluation dataset
* Performance monitoring
* Reproducible deployment
* Deployment automation

---

## V2 Completion Goal

**Rorak V2 = a durable, trustworthy, production-ready knowledge system.**

The focus is **reliability, persistence, document intelligence, memory, grounding, security, and operational stability**.

**V3 = Interactive + Agentic Rorak**
