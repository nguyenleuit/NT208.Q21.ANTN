# 📐 AIRA — Kiến trúc Hệ thống & Thiết kế Chi tiết

> **AIRA** (Academic Integrity & Research Assistant) — Nền tảng hỗ trợ nghiên cứu khoa học tích hợp AI  
> Phiên bản: 1.0 | Cập nhật: 28/02/2026

---

## Mục lục

1. [Sơ đồ Kiến trúc Hệ thống (System Architecture)](#1-sơ-đồ-kiến-trúc-hệ-thống)
2. [Mô tả Module chính](#2-mô-tả-module-chính)
3. [Thiết kế Luồng dữ liệu (DFD)](#3-thiết-kế-luồng-dữ-liệu-dfd)
4. [Sơ đồ UML](#4-sơ-đồ-uml)
   - 4.1 [Use-case Diagram](#41-use-case-diagram)
   - 4.2 [Sequence Diagrams](#42-sequence-diagrams)
5. [Thiết kế Cơ sở dữ liệu (ERD)](#5-thiết-kế-cơ-sở-dữ-liệu-erd)

---

## 1. Sơ đồ Kiến trúc Hệ thống

### 1.1 Kiến trúc Tổng quan (System Architecture Overview)

```mermaid
graph TB
    subgraph CLIENT["🖥️ Client Layer"]
        Browser["Web Browser"]
    end

    subgraph FRONTEND["⚛️ Frontend — Next.js 15 + React 18"]
        direction TB
        Pages["Pages<br/>(Landing, Login, Chat, Admin)"]
        Components["Components<br/>(ChatView, ToolResults,<br/>ChatShell, AuthGuard)"]
        Hooks["Custom Hooks<br/>(useAutoScroll, useFileUpload)"]
        Store["State Management<br/>(ChatStore — useReducer)"]
        APIClient["API Client<br/>(lib/api.ts — fetch + JWT)"]
    end

    subgraph BACKEND["🐍 Backend — FastAPI"]
        direction TB

        subgraph API_LAYER["API Layer (v1)"]
            AuthEP["Auth Endpoints<br/>/auth/*"]
            SessionEP["Session Endpoints<br/>/sessions/*"]
            ChatEP["Chat Endpoints<br/>/chat/*"]
            ToolsEP["Tools Endpoints<br/>/tools/*"]
            UploadEP["Upload Endpoints<br/>/upload/*"]
            AdminEP["Admin Endpoints<br/>/admin/*"]
        end

        subgraph MIDDLEWARE["Middleware & Security"]
            RateLimit["Rate Limiter"]
            CORS["CORS"]
            SecurityHeaders["Security Headers<br/>(CSP, HSTS, X-Frame)"]
            JWTAuth["JWT Authentication<br/>(HS256, 1h TTL)"]
            RBAC["RBAC + ABAC<br/>Authorization Gateway"]
        end

        subgraph SERVICE_LAYER["Service Layer"]
            ChatSvc["ChatService"]
            FileSvc["FileService"]
            LLMSvc["LLM Service<br/>(GeminiService)"]
            StorageSvc["StorageService"]
            CryptoMgr["CryptoManager<br/>(AES-256-GCM)"]
        end

        subgraph TOOL_LAYER["ML Tool Services"]
            CitChecker["CitationChecker<br/>(PyAlex + Habanero + httpx)"]
            JournalFinder["JournalFinder<br/>(SPECTER2 + TF-IDF)"]
            RetractScan["RetractionScanner<br/>(Crossref + OpenAlex + PubPeer)"]
            AIDetector["AIWritingDetector<br/>(RoBERTa ensemble)"]
        end
    end

    subgraph DATABASE["🗄️ Database Layer"]
        SQLite["SQLite / PostgreSQL<br/>(SQLAlchemy ORM)"]
    end

    subgraph STORAGE["📦 Storage Layer"]
        LocalFS["Local Filesystem<br/>(AES-256-GCM encrypted)"]
        S3["AWS S3<br/>(Pre-signed URLs)"]
    end

    subgraph EXTERNAL["🌐 External Services"]
        Gemini["Google Gemini API<br/>(google-genai SDK)"]
        OpenAlex["OpenAlex API<br/>(Academic metadata)"]
        Crossref["Crossref API<br/>(DOI resolution)"]
        PubPeer["PubPeer API<br/>(Post-pub review)"]
        HuggingFace["HuggingFace Hub<br/>(ML model hosting)"]
    end

    Browser --> Pages
    Pages --> Components
    Components --> Hooks
    Components --> Store
    Store --> APIClient
    APIClient -->|"HTTPS + JWT Bearer"| API_LAYER

    API_LAYER --> MIDDLEWARE
    MIDDLEWARE --> SERVICE_LAYER
    SERVICE_LAYER --> TOOL_LAYER

    ChatSvc --> LLMSvc
    ChatSvc --> CitChecker
    ChatSvc --> JournalFinder
    ChatSvc --> RetractScan
    FileSvc --> StorageSvc
    StorageSvc --> CryptoMgr

    SERVICE_LAYER --> SQLite
    StorageSvc --> LocalFS
    StorageSvc --> S3

    LLMSvc --> Gemini
    CitChecker --> OpenAlex
    CitChecker --> Crossref
    RetractScan --> Crossref
    RetractScan --> OpenAlex
    RetractScan --> PubPeer
    JournalFinder --> HuggingFace
    AIDetector --> HuggingFace

    classDef frontend fill:#3b82f6,color:#fff,stroke:#1e40af
    classDef backend fill:#10b981,color:#fff,stroke:#047857
    classDef database fill:#f59e0b,color:#fff,stroke:#b45309
    classDef external fill:#8b5cf6,color:#fff,stroke:#6d28d9
    classDef storage fill:#ec4899,color:#fff,stroke:#be185d

    class Pages,Components,Hooks,Store,APIClient frontend
    class AuthEP,SessionEP,ChatEP,ToolsEP,UploadEP,AdminEP,RateLimit,CORS,SecurityHeaders,JWTAuth,RBAC,ChatSvc,FileSvc,LLMSvc,StorageSvc,CryptoMgr,CitChecker,JournalFinder,RetractScan,AIDetector backend
    class SQLite database
    class Gemini,OpenAlex,Crossref,PubPeer,HuggingFace external
    class LocalFS,S3 storage
```

### 1.2 Kiến trúc Phân tầng (Layered Architecture)

```mermaid
graph LR
    subgraph L1["Layer 1: Presentation"]
        FE["Next.js 15<br/>React 18 + Tailwind CSS v4<br/>TypeScript"]
    end

    subgraph L2["Layer 2: API Gateway"]
        GW["FastAPI Router<br/>6 endpoint modules<br/>Rate Limiting + CORS + JWT"]
    end

    subgraph L3["Layer 3: Business Logic"]
        BL["Service Layer<br/>ChatService, FileService<br/>LLMService, StorageService"]
    end

    subgraph L4["Layer 4: ML/AI Tools"]
        ML["Tool Services<br/>CitationChecker, JournalFinder<br/>RetractionScanner, AIDetector"]
    end

    subgraph L5["Layer 5: Data Access"]
        DA["SQLAlchemy ORM<br/>Encrypted columns<br/>Composite indexes"]
    end

    subgraph L6["Layer 6: Infrastructure"]
        INFRA["SQLite/PostgreSQL<br/>Local FS / AWS S3<br/>AES-256-GCM Encryption"]
    end

    L1 -->|"HTTPS/JSON"| L2
    L2 -->|"Dependency Injection"| L3
    L3 -->|"Method calls"| L4
    L3 -->|"ORM queries"| L5
    L5 -->|"SQL/Storage I/O"| L6
    L4 -->|"HTTP/SDK"| EXT["External APIs<br/>Gemini, OpenAlex,<br/>Crossref, HuggingFace"]

    classDef layer fill:#1e293b,color:#e2e8f0,stroke:#334155
    class L1,L2,L3,L4,L5,L6 layer
```

---

## 2. Mô tả Module chính

### 2.1 Frontend Modules

| Module | File(s) | Chức năng |
|--------|---------|-----------|
| **Pages** | `app/page.tsx`, `app/login/page.tsx`, `app/chat/page.tsx`, `app/admin/page.tsx` | 4 trang chính: Landing, Đăng nhập/Đăng ký, Chat AI, Admin Dashboard |
| **ChatView** | `components/chat-view.tsx` | Giao diện chat chính: hiển thị tin nhắn, input area, file attachment, Markdown rendering |
| **ToolResults** | `components/tool-results.tsx` (~515 LOC) | 6 component render kết quả tools: `JournalListCard`, `CitationReportCard`, `RetractionReportCard`, `AIDetectionCard`, `PdfSummaryCard`, `ToolResultRenderer` |
| **ChatShell** | `components/chat-shell.tsx` | Sidebar: danh sách sessions, chuyển theme, thông tin user |
| **AuthGuard** | `components/auth-guard.tsx` | HOC bảo vệ route: redirect nếu chưa đăng nhập hoặc không phải admin |
| **ChatStore** | `lib/chat-store.tsx` | State management dùng `useReducer`: quản lý sessions, messages, loading states |
| **API Client** | `lib/api.ts` | 25 API methods + error handling + JWT token injection |
| **Auth Context** | `lib/auth.tsx` | React Context cho authentication: login, register, logout, token management |
| **Hooks** | `hooks/useAutoScroll.ts`, `hooks/useFileUpload.ts` | Smart scroll (chỉ scroll khi có message mới), Drag-and-drop file upload |

### 2.2 Backend Modules

| Module | File(s) | Chức năng |
|--------|---------|-----------|
| **Auth Endpoints** | `api/v1/endpoints/auth.py` | `POST /register`, `POST /login`, `GET /me`, `POST /promote` — Đăng ký, đăng nhập, lấy user info, promote role |
| **Session Endpoints** | `api/v1/endpoints/sessions.py` | `POST/GET/PATCH/DELETE /sessions` — CRUD sessions với pagination |
| **Chat Endpoints** | `api/v1/endpoints/chat.py` | `POST /chat/completions`, `POST /chat/{session_id}` — Gửi message, nhận AI response |
| **Tools Endpoints** | `api/v1/endpoints/tools.py` | 6 tool APIs: verify-citation, journal-match, retraction-scan, summarize-pdf, detect-ai-writing, ai-detect |
| **Upload Endpoints** | `api/v1/endpoints/upload.py` | `POST /upload`, `GET /upload/{file_id}`, `GET /upload/list_files` — Upload, download, list files |
| **Admin Endpoints** | `api/v1/endpoints/admin.py` | `GET /admin/overview`, `GET /admin/users`, `GET /admin/files` — Dashboard stats, quản lý users & files |

### 2.3 Service Layer

| Service | File | Chức năng |
|---------|------|-----------|
| **ChatService** | `services/chat_service.py` | Orchestration: tạo session, lưu message, gọi LLM/tools theo mode, auto-detect title |
| **LLMService** (GeminiService) | `services/llm_service.py` | Wrapper Google Gemini: `generate_response()`, `summarize_text()` — dùng `google-genai` SDK |
| **FileService** | `services/file_service.py` | Upload workflow: validate → encrypt → store → extract text (PDF via PyMuPDF) |
| **StorageService** | `services/storage_service.py` | Dual-backend abstraction: Local FS hoặc AWS S3, AES-256-GCM encryption, pre-signed URLs |
| **CryptoManager** | `core/crypto.py` | Master key management, AES-256-GCM encrypt/decrypt cho files và DB columns |
| **Bootstrap** | `services/bootstrap.py` | Tạo admin account mặc định khi startup (skip nếu non-dev + insecure password) |

### 2.4 ML Tool Services

| Tool | File | ML Model / API | Chức năng |
|------|------|----------------|-----------|
| **CitationChecker** | `tools/citation_checker.py` | PyAlex + Habanero + httpx | Verify citations: extract DOI → query OpenAlex/Crossref → fuzzy match → confidence score |
| **JournalFinder** | `tools/journal_finder.py` | SPECTER2 (768-dim) / SciBERT / TF-IDF | Recommend journals: encode abstract → cosine similarity với 35+ journal embeddings |
| **RetractionScanner** | `tools/retraction_scan.py` | Crossref + OpenAlex + PubPeer | Scan DOIs: check retraction status, risk level, title-based detection, PubPeer comments |
| **AIWritingDetector** | `tools/ai_writing_detector.py` | RoBERTa (`roberta-base-openai-detector`) | Detect AI text: ensemble 70% ML (RoBERTa) + 30% rule-based (7 features) |

### 2.5 Security & Middleware

| Component | File | Chức năng |
|-----------|------|-----------|
| **JWT Auth** | `core/security.py` | HS256 tokens: `iat`, `jti`, `exp` claims, 1h TTL, bcrypt password hashing |
| **RBAC + ABAC** | `core/authorization.py` | Role-based (ADMIN/RESEARCHER) + Attribute-based (ownership check) access control |
| **Rate Limiter** | `core/rate_limit.py` | IP-based rate limiting, X-Forwarded-For protection, periodic memory cleanup |
| **Security Headers** | `core/middleware.py` | CSP, HSTS, X-Frame-Options, X-Content-Type-Options |
| **Encrypted Types** | `core/encrypted_types.py` | SQLAlchemy custom types: `EncryptedText`, `EncryptedJSON` — transparent AES-256-GCM |
| **Audit Logger** | `core/audit.py` | Structured audit events: login, register, admin actions, file operations |

---

## 3. Thiết kế Luồng dữ liệu (DFD)

### 3.1 DFD Level 0 — Context Diagram

```mermaid
graph LR
    User(("👤 Researcher /<br/>Admin"))

    subgraph AIRA["AIRA System"]
        System["AIRA Platform"]
    end

    Gemini[("Google Gemini<br/>AI Service")]
    AcademicDB[("OpenAlex /<br/>Crossref /<br/>PubPeer")]
    HF[("HuggingFace<br/>ML Models")]
    Storage[("File Storage<br/>Local / S3")]

    User -->|"Đăng nhập, Chat,<br/>Upload PDF, Chọn tool"| System
    System -->|"AI response, Tool results,<br/>File summaries"| User

    System <-->|"Generate text,<br/>Summarize"| Gemini
    System <-->|"Verify citations,<br/>Check retractions"| AcademicDB
    System <-->|"Load SPECTER2,<br/>RoBERTa models"| HF
    System <-->|"Store/Retrieve<br/>encrypted files"| Storage
```

### 3.2 DFD Level 1 — Main Processes

```mermaid
graph TB
    User(("👤 User"))

    P1["1.0<br/>Authentication<br/>& User Mgmt"]
    P2["2.0<br/>Session &<br/>Message Mgmt"]
    P3["3.0<br/>AI Chat<br/>Processing"]
    P4["4.0<br/>Academic<br/>Tool Execution"]
    P5["5.0<br/>File Upload<br/>& Processing"]
    P6["6.0<br/>Admin<br/>Dashboard"]

    DS1[("D1: users")]
    DS2[("D2: chat_sessions")]
    DS3[("D3: chat_messages")]
    DS4[("D4: file_attachments")]
    DS5[("D5: File Storage")]

    Gemini[("Google Gemini")]
    ExtAPIs[("OpenAlex /<br/>Crossref")]
    MLModels[("SPECTER2 /<br/>RoBERTa")]

    User -->|"email, password"| P1
    P1 -->|"JWT token"| User
    P1 <-->|"CRUD"| DS1

    User -->|"create/list sessions"| P2
    P2 <-->|"CRUD"| DS2
    P2 -->|"session list"| User

    User -->|"message + mode"| P3
    P3 <-->|"save messages"| DS3
    P3 -->|"AI response"| User
    P3 <-->|"prompt/response"| Gemini
    P3 -->|"route to tool"| P4

    User -->|"text + DOI"| P4
    P4 <-->|"persist results"| DS3
    P4 -->|"tool results"| User
    P4 <-->|"API queries"| ExtAPIs
    P4 <-->|"ML inference"| MLModels

    User -->|"upload file"| P5
    P5 <-->|"file metadata"| DS4
    P5 <-->|"encrypted file I/O"| DS5
    P5 -->|"file info"| User
    P5 -->|"extracted text"| P3

    User -->|"admin request"| P6
    P6 <-->|"aggregate queries"| DS1
    P6 <-->|"aggregate queries"| DS2
    P6 <-->|"aggregate queries"| DS3
    P6 -->|"overview stats"| User
```

### 3.3 DFD Level 2 — Chi tiết Process 4.0 (Academic Tool Execution)

```mermaid
graph TB
    User(("👤 User"))
    DS3[("D3: chat_messages")]

    P4_1["4.1<br/>Citation<br/>Verification"]
    P4_2["4.2<br/>Journal<br/>Recommendation"]
    P4_3["4.3<br/>Retraction<br/>Scanning"]
    P4_4["4.4<br/>AI Writing<br/>Detection"]

    OpenAlex[("OpenAlex API")]
    Crossref[("Crossref API")]
    PubPeer[("PubPeer API")]
    SPECTER2[("SPECTER2 Model")]
    RoBERTa[("RoBERTa Model")]

    User -->|"text with citations"| P4_1
    P4_1 <-->|"DOI lookup"| OpenAlex
    P4_1 <-->|"DOI resolve"| Crossref
    P4_1 -->|"citation report"| DS3
    P4_1 -->|"verified/hallucinated"| User

    User -->|"abstract text"| P4_2
    P4_2 <-->|"encode abstract"| SPECTER2
    P4_2 -->|"journal list"| DS3
    P4_2 -->|"ranked journals"| User

    User -->|"text with DOIs"| P4_3
    P4_3 <-->|"retraction check"| Crossref
    P4_3 <-->|"is_retracted"| OpenAlex
    P4_3 <-->|"comments"| PubPeer
    P4_3 -->|"retraction report"| DS3
    P4_3 -->|"risk assessment"| User

    User -->|"text to analyze"| P4_4
    P4_4 <-->|"ML inference"| RoBERTa
    P4_4 -->|"detection result"| DS3
    P4_4 -->|"AI score + verdict"| User
```

---

## 4. Sơ đồ UML

### 4.1 Use-case Diagram

```mermaid
graph TB
    subgraph actors["Actors"]
        Researcher(("👤 Researcher"))
        Admin(("👑 Admin"))
    end

    subgraph uc_auth["Authentication"]
        UC1["Đăng ký tài khoản"]
        UC2["Đăng nhập"]
        UC3["Xem thông tin cá nhân"]
    end

    subgraph uc_chat["Chat & AI"]
        UC4["Tạo phiên chat mới"]
        UC5["Gửi tin nhắn"]
        UC6["Nhận phản hồi AI<br/>(Gemini)"]
        UC7["Chọn chế độ chat<br/>(General QA / Verification /<br/>Journal Match)"]
    end

    subgraph uc_tools["Academic Tools"]
        UC8["Kiểm tra trích dẫn<br/>(Citation Verification)"]
        UC9["Gợi ý tạp chí<br/>(Journal Recommendation)"]
        UC10["Quét rút bỏ bài báo<br/>(Retraction Scan)"]
        UC11["Phát hiện văn bản AI<br/>(AI Writing Detection)"]
        UC12["Tóm tắt PDF"]
    end

    subgraph uc_file["File Management"]
        UC13["Upload file (PDF)"]
        UC14["Download file"]
        UC15["Xem danh sách file"]
    end

    subgraph uc_admin["Administration"]
        UC16["Xem Dashboard tổng quan"]
        UC17["Quản lý users"]
        UC18["Quản lý files hệ thống"]
        UC19["Promote user → Admin"]
    end

    Researcher --> UC1
    Researcher --> UC2
    Researcher --> UC3
    Researcher --> UC4
    Researcher --> UC5
    UC5 -->|"include"| UC6
    Researcher --> UC7
    Researcher --> UC8
    Researcher --> UC9
    Researcher --> UC10
    Researcher --> UC11
    Researcher --> UC12
    Researcher --> UC13
    Researcher --> UC14
    Researcher --> UC15

    Admin --> UC16
    Admin --> UC17
    Admin --> UC18
    Admin --> UC19

    Admin -.->|"inherits"| Researcher

    UC7 -->|"extend"| UC8
    UC7 -->|"extend"| UC9
    UC12 -->|"include"| UC13
```

### 4.2 Sequence Diagrams

#### 4.2.1 Sequence Diagram — Đăng nhập & Xác thực

```mermaid
sequenceDiagram
    actor User as 👤 User
    participant FE as Frontend<br/>(Next.js)
    participant API as FastAPI<br/>(/auth)
    participant MW as Middleware<br/>(Rate Limit + CORS)
    participant SEC as Security<br/>(JWT + bcrypt)
    participant DB as Database<br/>(SQLAlchemy)

    User->>FE: Nhập email + password
    FE->>API: POST /api/v1/auth/login<br/>(OAuth2 form)
    API->>MW: Check rate limit
    MW-->>API: OK (within limit)
    API->>SEC: authenticate_user(email, password)
    SEC->>DB: SELECT * FROM users WHERE email=?
    DB-->>SEC: User record
    SEC->>SEC: bcrypt.checkpw(password, hashed)
    SEC-->>API: User object (authenticated)
    API->>SEC: create_access_token(sub=user_id,<br/>iat, jti, exp=1h)
    SEC-->>API: JWT token (HS256)
    API->>DB: log_audit_event("auth.login")
    API-->>FE: 200 OK {access_token, token_type}
    FE->>FE: localStorage.setItem("token", jwt)
    FE-->>User: Redirect → /chat
```

#### 4.2.2 Sequence Diagram — Chat AI (General QA Mode)

```mermaid
sequenceDiagram
    actor User as 👤 User
    participant FE as Frontend<br/>(ChatView)
    participant Store as ChatStore<br/>(useReducer)
    participant API as FastAPI<br/>(/chat)
    participant Auth as Auth<br/>(JWT + RBAC)
    participant ChatSvc as ChatService
    participant LLM as GeminiService
    participant Gemini as Google Gemini<br/>API
    participant DB as Database

    User->>FE: Gõ tin nhắn + Enter
    FE->>Store: dispatch(SEND_MESSAGE)
    Store->>API: POST /api/v1/chat/completions<br/>{session_id, user_message, mode}
    API->>Auth: verify JWT + check Permission.MESSAGE_WRITE
    Auth-->>API: ✅ Authorized
    API->>ChatSvc: complete_chat(db, user, session_id, message, mode)

    ChatSvc->>DB: INSERT chat_messages (role=USER)
    ChatSvc->>DB: SELECT recent messages (context)

    alt mode == GENERAL_QA
        ChatSvc->>LLM: generate_response(history, user_text)
        LLM->>LLM: _build_prompt(history + system_instruction)
        LLM->>Gemini: models.generate_content(model, contents, config)
        Gemini-->>LLM: Generated text
        LLM-->>ChatSvc: AI response text
    end

    ChatSvc->>DB: INSERT chat_messages (role=ASSISTANT)
    ChatSvc->>DB: UPDATE chat_sessions.updated_at
    ChatSvc-->>API: (user_msg, assistant_msg)
    API-->>FE: 200 OK {session_id, user_message, assistant_message}
    FE->>Store: dispatch(RECEIVE_MESSAGE)
    Store-->>FE: Re-render với message mới
    FE-->>User: Hiển thị AI response
```

#### 4.2.3 Sequence Diagram — Citation Verification Tool

```mermaid
sequenceDiagram
    actor User as 👤 User
    participant FE as Frontend
    participant API as FastAPI<br/>(/tools)
    participant CitChk as CitationChecker
    participant PyAlex as PyAlex<br/>(OpenAlex SDK)
    participant Hab as Habanero<br/>(Crossref SDK)
    participant HTTPX as httpx<br/>(Direct API)
    participant DB as Database

    User->>FE: Nhập text chứa citations
    FE->>API: POST /api/v1/tools/verify-citation<br/>{session_id, text}

    API->>CitChk: verify(text)
    CitChk->>CitChk: _extract_citations(text)<br/>6 regex patterns (DOI, author-year,<br/>numbered, parenthetical, etc.)

    loop For each citation found
        alt Has DOI
            CitChk->>Hab: cr.works(ids=doi)
            Hab-->>CitChk: Crossref metadata
            CitChk->>CitChk: status = DOI_VERIFIED, confidence = 1.0
        else Author-year pattern
            CitChk->>PyAlex: Works().search_filter(author=X, year=Y)
            PyAlex-->>CitChk: OpenAlex results
            alt Exact match found
                CitChk->>CitChk: status = VALID, confidence = 0.9
            else Fuzzy match
                CitChk->>CitChk: status = PARTIAL_MATCH, confidence = 0.5
            else No match
                CitChk->>HTTPX: GET openalex.org/works?search=...
                HTTPX-->>CitChk: Fallback results
                CitChk->>CitChk: status = UNVERIFIED / HALLUCINATED
            end
        end
    end

    CitChk-->>API: List[CitationCheckResult]
    API->>API: Convert to CitationItem schemas
    API->>DB: persist_tool_interaction(CITATION_REPORT)
    API-->>FE: {type: "citation_report", data: [...], text: summary}
    FE->>FE: Render CitationReportCard<br/>(verified badges, DOI links, confidence)
    FE-->>User: Hiển thị kết quả
```

#### 4.2.4 Sequence Diagram — Journal Recommendation Tool

```mermaid
sequenceDiagram
    actor User as 👤 User
    participant FE as Frontend
    participant API as FastAPI<br/>(/tools)
    participant JF as JournalFinder
    participant Model as SPECTER2<br/>(sentence-transformers)
    participant DB as Database

    User->>FE: Nhập abstract bài báo
    FE->>API: POST /api/v1/tools/journal-match<br/>{session_id, abstract}

    API->>JF: recommend(abstract, top_k=5)
    JF->>JF: _detect_domains(text)<br/>(keyword matching → domain categories)

    alt ML Model loaded (use_ml=True)
        JF->>Model: encode([abstract])
        Model-->>JF: 768-dim embedding vector
        JF->>JF: cosine_similarity(abstract_emb,<br/>journal_embeddings)
    else Fallback (use_ml=False)
        JF->>JF: TF-IDF vectorize + cosine_similarity
    end

    JF->>JF: Sort by score, filter by domain
    JF-->>API: List[dict] (journal, score, reason, url, ...)

    API->>API: Convert to JournalItem schemas
    API->>DB: persist_tool_interaction(JOURNAL_LIST)
    API-->>FE: {type: "journal_list", data: [...], text: summary}
    FE->>FE: Render JournalListCard<br/>(IF, h-index, review time, Open Access)
    FE-->>User: Hiển thị danh sách tạp chí
```

#### 4.2.5 Sequence Diagram — File Upload & PDF Summary

```mermaid
sequenceDiagram
    actor User as 👤 User
    participant FE as Frontend<br/>(useFileUpload)
    participant API as FastAPI<br/>(/upload + /tools)
    participant FileSvc as FileService
    participant Storage as StorageService
    participant Crypto as CryptoManager
    participant LLM as GeminiService
    participant Gemini as Google Gemini
    participant DB as Database

    User->>FE: Kéo thả file PDF
    FE->>FE: Validate (size, type)
    FE->>API: POST /api/v1/upload<br/>(multipart/form-data)

    API->>FileSvc: save_upload(db, user, session_id, file)
    FileSvc->>FileSvc: Validate file type + size
    FileSvc->>Crypto: encrypt(file_bytes)
    Crypto->>Crypto: AES-256-GCM<br/>(random IV + auth tag)
    Crypto-->>FileSvc: encrypted_bytes
    FileSvc->>Storage: store(key, encrypted_bytes)
    Storage-->>FileSvc: storage_url
    FileSvc->>FileSvc: extract_text(PyMuPDF)
    FileSvc->>DB: INSERT file_attachments<br/>(encrypted storage_key, extracted_text)
    FileSvc-->>API: FileAttachment record
    API-->>FE: {file_id, file_name, size_bytes}
    FE-->>User: Hiển thị file đã upload

    User->>FE: Click "Tóm tắt PDF"
    FE->>API: POST /api/v1/tools/summarize-pdf<br/>{session_id, file_id}
    API->>DB: SELECT file_attachments WHERE id=file_id
    DB-->>API: attachment (with extracted_text)
    API->>LLM: summarize_text(extracted_text)
    LLM->>Gemini: generate_content(summary_prompt)
    Gemini-->>LLM: Summary text
    LLM-->>API: summary
    API->>DB: persist_tool_interaction(PDF_SUMMARY)
    API-->>FE: {file_id, file_name, text: summary}
    FE-->>User: Hiển thị bản tóm tắt PDF
```

#### 4.2.6 Sequence Diagram — Retraction Scan

```mermaid
sequenceDiagram
    actor User as 👤 User
    participant FE as Frontend
    participant API as FastAPI<br/>(/tools)
    participant RS as RetractionScanner
    participant CR as Crossref API
    participant OA as OpenAlex API
    participant PP as PubPeer API
    participant DB as Database

    User->>FE: Nhập text chứa DOIs
    FE->>API: POST /api/v1/tools/retraction-scan<br/>{session_id, text}
    API->>RS: scan(text)
    RS->>RS: _extract_dois(text)<br/>(regex: 10.XXXX/...)

    loop For each DOI
        RS->>RS: scan_doi(doi)

        RS->>CR: GET api.crossref.org/works/{doi}
        CR-->>RS: Crossref metadata<br/>(title, journal, year, update-to)
        RS->>RS: Check title.startswith("RETRACTED:")
        RS->>RS: Check update-to field for retractions

        RS->>OA: GET api.openalex.org/works/doi:{doi}
        OA-->>RS: OpenAlex data<br/>(is_retracted flag)

        RS->>PP: GET pubpeer.com/search?q={doi}
        PP-->>RS: ⚠️ 404 (API dead)<br/>→ graceful fallback

        RS->>RS: Compute risk_level<br/>(CRITICAL/HIGH/MEDIUM/LOW/NONE)
        RS->>RS: Collect risk_factors[]
    end

    RS-->>API: List[RetractionResult]
    API->>API: Convert to RetractionItem schemas
    API->>DB: persist_tool_interaction(RETRACTION_REPORT)
    API-->>FE: {type: "retraction_report", data: [...], text: summary}
    FE->>FE: Render RetractionReportCard<br/>(risk colors, retraction details)
    FE-->>User: Hiển thị báo cáo retraction
```

---

## 5. Thiết kế Cơ sở dữ liệu (ERD)

### 5.1 Lược đồ Quan hệ Thực thể (Entity Relationship Diagram)

```mermaid
erDiagram
    users {
        VARCHAR_36 id PK "UUID primary key"
        VARCHAR_255 email UK "Unique, indexed"
        VARCHAR_255 full_name "Nullable"
        VARCHAR_255 hashed_password "bcrypt hash"
        ENUM role "admin | researcher"
        DATETIME created_at "UTC timestamp"
    }

    chat_sessions {
        VARCHAR_36 id PK "UUID primary key"
        VARCHAR_36 user_id FK "→ users.id (CASCADE)"
        VARCHAR_255 title "Auto-derived from first message"
        ENUM mode "general_qa | verification | journal_match"
        DATETIME created_at "UTC timestamp"
        DATETIME updated_at "Auto-update on change"
    }

    chat_messages {
        VARCHAR_36 id PK "UUID primary key"
        VARCHAR_36 session_id FK "→ chat_sessions.id (CASCADE)"
        ENUM role "user | assistant | system | tool"
        ENUM message_type "text | citation_report | journal_list | retraction_report | file_upload | pdf_summary | ai_writing_detection"
        TEXT content "AES-256-GCM encrypted (EncryptedText)"
        JSON tool_results "AES-256-GCM encrypted (EncryptedJSON)"
        DATETIME created_at "UTC timestamp"
    }

    file_attachments {
        VARCHAR_36 id PK "UUID primary key"
        VARCHAR_36 session_id FK "→ chat_sessions.id (CASCADE)"
        VARCHAR_36 message_id FK "→ chat_messages.id (SET NULL), nullable"
        VARCHAR_36 user_id FK "→ users.id (CASCADE)"
        VARCHAR_255 file_name "Original filename"
        VARCHAR_128 mime_type "e.g. application/pdf"
        BIGINT size_bytes "File size"
        TEXT storage_key "AES-256-GCM encrypted"
        TEXT storage_url "AES-256-GCM encrypted"
        BOOLEAN storage_encrypted "Default true"
        VARCHAR_64 storage_encryption_alg "Default AES-256-GCM"
        TEXT extracted_text "AES-256-GCM encrypted, nullable"
        DATETIME created_at "UTC timestamp"
    }

    users ||--o{ chat_sessions : "1 user → N sessions"
    chat_sessions ||--o{ chat_messages : "1 session → N messages"
    chat_sessions ||--o{ file_attachments : "1 session → N files"
    chat_messages ||--o{ file_attachments : "1 message → N files (optional)"
    users ||--o{ file_attachments : "1 user → N files"
```

### 5.2 Chi tiết Bảng & Ràng buộc

#### Bảng `users`

| Column | Type | Constraints | Mô tả |
|--------|------|-------------|-------|
| `id` | VARCHAR(36) | PK, DEFAULT uuid4() | UUID định danh |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | Email đăng nhập |
| `full_name` | VARCHAR(255) | NULLABLE | Tên đầy đủ |
| `hashed_password` | VARCHAR(255) | NOT NULL | bcrypt hash ($2b$12$...) |
| `role` | ENUM('admin','researcher') | NOT NULL, DEFAULT 'researcher' | Vai trò trong hệ thống |
| `created_at` | DATETIME(tz) | NOT NULL, DEFAULT now(UTC) | Thời gian tạo |

#### Bảng `chat_sessions`

| Column | Type | Constraints | Mô tả |
|--------|------|-------------|-------|
| `id` | VARCHAR(36) | PK, DEFAULT uuid4() | UUID phiên chat |
| `user_id` | VARCHAR(36) | FK → users.id, ON DELETE CASCADE, INDEX | Chủ sở hữu |
| `title` | VARCHAR(255) | DEFAULT 'New Chat' | Tiêu đề (auto-derived) |
| `mode` | ENUM('general_qa','verification','journal_match') | NOT NULL, DEFAULT 'general_qa' | Chế độ hoạt động |
| `created_at` | DATETIME(tz) | NOT NULL | Thời gian tạo |
| `updated_at` | DATETIME(tz) | NOT NULL, ON UPDATE now(UTC) | Thời gian cập nhật |

#### Bảng `chat_messages`

| Column | Type | Constraints | Mô tả |
|--------|------|-------------|-------|
| `id` | VARCHAR(36) | PK, DEFAULT uuid4() | UUID tin nhắn |
| `session_id` | VARCHAR(36) | FK → chat_sessions.id, ON DELETE CASCADE, INDEX | Phiên chat chứa message |
| `role` | ENUM('user','assistant','system','tool') | NOT NULL | Vai trò gửi message |
| `message_type` | ENUM(7 types) | NOT NULL, DEFAULT 'text' | Loại nội dung |
| `content` | TEXT (EncryptedText) | NULLABLE | Nội dung — mã hóa AES-256-GCM |
| `tool_results` | JSON (EncryptedJSON) | NULLABLE | Kết quả tool — mã hóa AES-256-GCM |
| `created_at` | DATETIME(tz) | NOT NULL | Thời gian tạo |

**Composite Index**: `ix_chatmsg_session_created(session_id, created_at)` — tối ưu query lấy messages theo session, sắp xếp theo thời gian.

#### Bảng `file_attachments`

| Column | Type | Constraints | Mô tả |
|--------|------|-------------|-------|
| `id` | VARCHAR(36) | PK, DEFAULT uuid4() | UUID file |
| `session_id` | VARCHAR(36) | FK → chat_sessions.id, ON DELETE CASCADE, INDEX | Phiên chat chứa file |
| `message_id` | VARCHAR(36) | FK → chat_messages.id, ON DELETE SET NULL, INDEX, NULLABLE | Message liên kết (optional) |
| `user_id` | VARCHAR(36) | FK → users.id, ON DELETE CASCADE, INDEX | Người upload |
| `file_name` | VARCHAR(255) | NOT NULL | Tên file gốc |
| `mime_type` | VARCHAR(128) | NOT NULL | MIME type (application/pdf, ...) |
| `size_bytes` | BIGINT | NOT NULL | Kích thước file (bytes) |
| `storage_key` | TEXT (EncryptedText) | NOT NULL | Đường dẫn lưu trữ — mã hóa |
| `storage_url` | TEXT (EncryptedText) | NOT NULL | URL truy cập — mã hóa |
| `storage_encrypted` | BOOLEAN | DEFAULT TRUE | File có mã hóa at-rest |
| `storage_encryption_alg` | VARCHAR(64) | DEFAULT 'AES-256-GCM' | Thuật toán mã hóa |
| `extracted_text` | TEXT (EncryptedText) | NULLABLE | Text trích xuất từ PDF — mã hóa |
| `created_at` | DATETIME(tz) | NOT NULL | Thời gian upload |

**Composite Indexes**:
- `ix_fileatt_session_created(session_id, created_at)` — truy vấn files theo session
- `ix_fileatt_user_created(user_id, created_at)` — truy vấn files theo user

### 5.3 Mối quan hệ (Relationships)

| Quan hệ | Loại | ON DELETE | Mô tả |
|----------|------|-----------|-------|
| `users` → `chat_sessions` | 1:N | CASCADE | Xóa user → xóa tất cả sessions |
| `chat_sessions` → `chat_messages` | 1:N | CASCADE | Xóa session → xóa tất cả messages |
| `chat_sessions` → `file_attachments` | 1:N | CASCADE | Xóa session → xóa metadata files |
| `chat_messages` → `file_attachments` | 1:N | SET NULL | Xóa message → giữ file, set message_id = NULL |
| `users` → `file_attachments` | 1:N | CASCADE | Xóa user → xóa tất cả files |

### 5.4 Encryption Schema

Các cột được đánh dấu `EncryptedText` / `EncryptedJSON` sử dụng SQLAlchemy custom types trong `core/encrypted_types.py`:

```
Plaintext → AES-256-GCM encrypt(master_key, random_iv) → Base64 encode → Store in DB
DB read → Base64 decode → AES-256-GCM decrypt(master_key, iv, tag) → Plaintext
```

| Bảng | Cột được mã hóa | Type |
|------|-----------------|------|
| `chat_messages` | `content` | EncryptedText |
| `chat_messages` | `tool_results` | EncryptedJSON |
| `file_attachments` | `storage_key` | EncryptedText |
| `file_attachments` | `storage_url` | EncryptedText |
| `file_attachments` | `extracted_text` | EncryptedText |

### 5.5 Sample Data (JSON Demo)

#### User record
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "researcher@university.edu",
  "full_name": "Nguyễn Văn A",
  "hashed_password": "$2b$12$LJ4kAePz6qG2...",
  "role": "researcher",
  "created_at": "2026-02-28T10:00:00+00:00"
}
```

#### Chat Session record
```json
{
  "id": "s1234567-abcd-ef01-2345-678901234567",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Deep learning NLP research",
  "mode": "general_qa",
  "created_at": "2026-02-28T10:05:00+00:00",
  "updated_at": "2026-02-28T10:30:00+00:00"
}
```

#### Chat Message record (tool result)
```json
{
  "id": "m9876543-dcba-0fed-5432-109876543210",
  "session_id": "s1234567-abcd-ef01-2345-678901234567",
  "role": "assistant",
  "message_type": "citation_report",
  "content": "ENC:AES256GCM:base64(iv+ciphertext+tag)...",
  "tool_results": "ENC:AES256GCM:base64({\"type\":\"citation_report\",\"data\":[{\"citation\":\"10.1038/nature12373\",\"status\":\"DOI_VERIFIED\",\"confidence\":1.0,\"doi\":\"10.1038/nature12373\",\"title\":\"Nanometre-scale thermometry in a living cell\",\"authors\":[\"Kucsko G.\",\"Maurer P. C.\"],\"year\":2013,\"source\":\"crossref\"}]})...",
  "created_at": "2026-02-28T10:10:00+00:00"
}
```

#### File Attachment record
```json
{
  "id": "f5678901-2345-6789-0abc-def012345678",
  "session_id": "s1234567-abcd-ef01-2345-678901234567",
  "message_id": null,
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "file_name": "research_paper.pdf",
  "mime_type": "application/pdf",
  "size_bytes": 2458624,
  "storage_key": "ENC:AES256GCM:base64(...)...",
  "storage_url": "ENC:AES256GCM:base64(...)...",
  "storage_encrypted": true,
  "storage_encryption_alg": "AES-256-GCM",
  "extracted_text": "ENC:AES256GCM:base64(Introduction: This paper presents...)...",
  "created_at": "2026-02-28T10:08:00+00:00"
}
```

---

## Phụ lục: Tổng hợp API Endpoints

| Method | Endpoint | Auth | Chức năng |
|--------|----------|------|-----------|
| POST | `/api/v1/auth/register` | ❌ | Đăng ký tài khoản mới |
| POST | `/api/v1/auth/login` | ❌ | Đăng nhập (OAuth2 form) |
| GET | `/api/v1/auth/me` | ✅ JWT | Lấy thông tin user hiện tại |
| POST | `/api/v1/auth/promote` | ✅ Admin | Promote user → admin |
| POST | `/api/v1/sessions` | ✅ JWT | Tạo phiên chat mới |
| GET | `/api/v1/sessions` | ✅ JWT | Liệt kê sessions (pagination) |
| GET | `/api/v1/sessions/{id}` | ✅ JWT | Chi tiết 1 session |
| PATCH | `/api/v1/sessions/{id}` | ✅ JWT | Cập nhật title/mode |
| DELETE | `/api/v1/sessions/{id}` | ✅ JWT | Xóa session |
| POST | `/api/v1/chat/completions` | ✅ JWT | Gửi message → nhận AI response |
| POST | `/api/v1/chat/{session_id}` | ✅ JWT | Chat theo session cụ thể |
| GET | `/api/v1/chat/{session_id}/messages` | ✅ JWT | Lấy lịch sử messages |
| POST | `/api/v1/tools/verify-citation` | ✅ JWT | Kiểm tra trích dẫn |
| POST | `/api/v1/tools/journal-match` | ✅ JWT | Gợi ý tạp chí |
| POST | `/api/v1/tools/retraction-scan` | ✅ JWT | Quét retraction |
| POST | `/api/v1/tools/summarize-pdf` | ✅ JWT | Tóm tắt PDF |
| POST | `/api/v1/tools/detect-ai-writing` | ✅ JWT | Phát hiện văn bản AI |
| POST | `/api/v1/tools/ai-detect` | ✅ JWT | Alias detect-ai-writing |
| POST | `/api/v1/upload` | ✅ JWT | Upload file |
| GET | `/api/v1/upload/{file_id}` | ✅ JWT | Download file |
| GET | `/api/v1/upload/list_files` | ✅ JWT | Liệt kê files (pagination) |
| GET | `/api/v1/admin/overview` | ✅ Admin | Dashboard tổng quan |
| GET | `/api/v1/admin/users` | ✅ Admin | Liệt kê users |
| GET | `/api/v1/admin/files` | ✅ Admin | Liệt kê files hệ thống |
