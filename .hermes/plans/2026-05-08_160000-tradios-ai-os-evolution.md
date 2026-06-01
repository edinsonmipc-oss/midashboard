# TRADIOS AI OS Evolution — Build Plan

## Goal
Transform TRADIOS from a dashboard into a true AI Operating System for tradies — offline-first, photo-centric, AI-assisted, field-worker optimized.

## Priority Features (In Build Order)

### Phase 1: PWA + AI Assistant Foundation
**Files affected:** `index.html`

1. **Service Worker** — Inline registration for offline support
   - Cache app shell (HTML, CSS, JS)
   - Cache fonts.googleapis.com
   - Offline fallback page
   
2. **manifest.json** — Inline via `<link rel="manifest">`
   - Name: "TRADIOS"
   - Theme color: #060608 (dark)
   - Icons: generated from SVG
   - Display: standalone (fullscreen app)
   - Orientation: any (portrait/landscape)

3. **Floating AI Assistant**
   - Chat bubble (fixed bottom-right)
   - Slide-out panel with conversation history
   - OpenRouter API calls with Gemini Flash (free)
   - Smart actions: /quote, /job, /photo, /help
   - Markdown rendering for responses
   - localStorage conversation persistence

### Phase 2: AI Quote Generator
**New panel:** `pn-quotes`

1. **Quote Form:**
   - Client name/company dropdown (from leads data)
   - Service selection (paving, decking, fencing, etc.)
   - Scope of work (textarea)
   - Estimated hours/days
   - Material costs
   - Labor rate ($/hr)
   
2. **AI Generation:**
   - "Generate Quote" button → calls OpenRouter API
   - AI creates professional quote with: header, scope, pricing table, terms, total
   - Rendered inline with premium styling
   
3. **Management:**
   - Save to localStorage quote history
   - Status: Draft → Sent → Accepted → Rejected
   - List view of all quotes
   - Copy to clipboard / email draft

### Phase 3: Job CRM (Drag & Drop)
**Replace:** `pn-tasks` with full Job CRM

1. **Kanban board:**
   - New Lead → Quote Sent → Booked → In Progress → Completed → Archived
   - Drag & drop cards between columns (HTML5 Drag API)
   - Card shows: client name, job type, amount, status badge, date
   
2. **Job Details:**
   - Click card → detail modal
   - Full info: client, address, service, scope, amount, dates, photos
   - Status changer
   - Notes/updates field
   
3. **Data:**
   - localStorage persistence
   - Sample data pre-populated from existing leads

### Phase 4: Photo Workflow
**New panel:** `pn-photos`

1. **Camera Capture:**
   - WebRTC camera access (mobile optimized)
   - Capture button → thumbnail preview
   - Flip camera (front/back)
   
2. **Before/After Gallery:**
   - Upload from camera or file picker
   - Side-by-side or slider comparison
   - Thumbnail grid view
   - Attach to specific job
   
3. **Storage:**
   - Base64 encoded images in localStorage (compressed)
   - IndexedDB for larger images (future)

## Architecture Decisions

- **Single HTML file SPA** — maintains existing deploy pipeline (Render + GitHub Pages)
- **All CSS inlined** — for PWA offline reliability
- **All JS vanilla** — no framework overhead
- **OpenRouter directly from browser** — using user's OpenRouter key (gemini-2.0-flash-lite for speed, gemini-2.5-flash-img for photos)
- **localStorage for PERSISTENCE** — no backend needed for MVP
- **SVG icons throughout** — lightweight, scalable

## Projected File Size
- Current: 826 lines (72KB)
- Target: ~1800 lines (~85KB with compression)
- CSS: 300→450 lines (new components)
- HTML: 50→90 lines (new panels)
- JS: 250→800 lines (new features)

## Testing
- Open locally with Python HTTP server
- Test CMD+K with all new panels
- Test PWA install prompt (Chrome DevTools)
- Test AI chat (requires working OpenRouter key)
- Test drag & drop across columns
- Test photo capture (mobile emulation)
- Test offline mode (DevTools offline toggle)

## Risks
- OpenRouter key in client-side JS (exposed) — OK for now, private app
- localStorage size limit (~5-10MB) — large photos may fail
- Browser camera API requires HTTPS (Render serves HTTPS ✅)
- Service worker scope issues with GitHub Pages subdirectory
