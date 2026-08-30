# RBM Security — Telangana Manpower Platform

**Two Separate Websites** — Client + Tracker — with Real Backend, Glass Morphism, Telangana-only.

Built for **RBM Security Services** — Uppal, Hyderabad, Telangana. Contact: **99498 11742 / 88975 35830 / rbm.uppal@gmail.com**

### Live Architecture

| Website | Folder | Port | Purpose |
|---------|--------|------|---------|
| **Client** | `/client` | `3001` `/` | For **clients** (job seekers & employers) to view Telangana jobs, apply, post jobs, bulk manpower, auth, saved, etc. |
| **Tracker** | `/tracker` | `3001` `/tracker` | For **admin** to **track ALL applications** — glass morphism dashboard with charts, kanban, calendar, payroll, SOS |
| **Backend** | `/backend` | `3001` `/api` | Real Node + Express + JSON DB (`data/db.json`), JWT auth, file uploads `uploads/` |

All share `localStorage` + Real API (`/api`) when served via `http://localhost:3001` (same origin). Fallback to `localStorage` if backend down.

### Quick Start

```powershell
# Backend (serves both frontends + API)
Set-Location backend; npm install; node server.js
# → http://localhost:3001/           (Client)
# → http://localhost:3001/tracker    (Tracker Dashboard)
# → http://localhost:3001/api/health

# Or separate static (for localStorage demo, no API):
Set-Location ..; python -m http.server 8767
# → http://localhost:8767/securehire/      (Client)
# → http://localhost:8767/rbm-tracker/     (Tracker)
```

### Features — Client

- **Video Loader** `logo-animation.mp4` fullscreen auto-play muted→sound-on 200ms, `SKIP`, no yellow line, `blur 24px` fade
- **RBM Shield** `rbm-logo.png` (cropped from screenshot, transparent) in nav/footer/hero/favicon, PSARA certified
- **Telangana Only** — all 29 jobs `Hyderabad • Gachibowli/Banjara Hills/Secunderabad/HITEC City/Uppal/Warangal/Karimnagar/Nizamabad`, footer `Uppal, Hyderabad - 500039`
- **Hero** orbs `blur 50px`, particles, tilt `heroTiltCard`, kenburns, magnetic buttons, gradient `HIRE TRUSTED`, Lenis smooth scroll, `ScrollTrigger` batches
- **Guard Gallery** 8 guards `guards-gallery` lightbox `openGuardLightbox()`
- **Jobs** 29 (guards/housekeeping/ward boys/helpers/servants/manpower/bouncers/CCTV/armed) + filters `filterDistrict/Exp/Salary/sortJobs` + `searchSuggest` + voice `startVoice()` + saved `rbm_saved` `savedSection`
- **Categories** 11 cards, **Bulk Manpower** `bulkOrder` 10-100 staff quote → `wa.me`, **How it works**, **Reviews** `rbm_reviews` `renderReviews()`, **Job Alerts** `rbm_alerts`, **Refer & Earn** `copyRefer()` ₹500, **My Applications** `myApps` + doc tracker (Aadhaar/PSARA/Police/Interview)
- **Auth** `openAuth()` OTP `123456` → `JWT` `rbm_token` `rbm_user`, **Employer Post Job** `openEmployerModal()` → `POST /api/jobs` → live, **File Upload** photo/ID preview `FileReader` base64
- **Extra:** Training 3 YouTube, Blog 3, Salary Calculator `calcSalary()`, Recently Viewed `rbm_recent`, Live Chat `liveChat` + `waFloat`, Push `Notification`, Referral Leaderboard `renderLeaderboard()`, Shift Calendar `renderShiftCal()`, Doc Expiry `checkDocs()`, Theme `toggleTheme()`, QR Attendance `genQR()` `rbm_attendance`, SOS `triggerSOS()` logs SOS app, GPS Live `gpsDots` 4 guards moving 3s, Video Interview modal, Pay to Feature `payModal` Razorpay demo ₹499, PWA `manifest.json`+`sw.js`, SEO `schema.org` + OG

### Features — Tracker (Glass Morphism)

- **Glass** `blur 24px saturate 180%` `linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03))` + orbs amber/cyan/violet `C:\tracker\index.html:29`
- **Stats** Total/Today/Top City/Top Job + **Charts** `Chart.js` doughnut `cityChart/catChart` + line `trendChart` + bar `perfChart` + `conversionRate`
- **Job Management** `jobManageList` `renderJobManage()` delete/feature (pay) custom `rbm_jobs`
- **Filters** search/city/job/date, **Table** `table-glass` photo/status dropdown `updateStatus()` call/WhatsApp/delete, **Kanban** 5 cols `toggleKanban()` `renderKanban()`, **Calendar** `interviewCal` next 7 days, **Payroll** `renderPayroll()` staff×₹18k+GST, **SOS Log**
- **Export CSV** `exportCSV()`, `Seed Demo`, auto-refresh 2s + `storage` event, glass `orb-a/b/c`

### Contacts

`9949811742 / 8897535830 / rbm.uppal@gmail.com` — Uppal, Hyderabad, Telangana. PSARA licensed.

### Tech

`Tailwind CDN`, `GSAP 3.12.5 + ScrollTrigger`, `Lenis 1.1.20`, `Chart.js 4.4.2`, `Express 4.18`, `CORS`, `JWT`, `Multer`, `uuid`, `bcryptjs`. No native deps — JSON DB `data/db.json`.

### Deploy

- **Render/Railway:** `backend` `npm start` (`PORT` + `JWT_SECRET`), set root `backend`, build `npm install`
- **Vercel:** For client/tracker static, backend as serverless
- **PWA:** Installable via `manifest.json`

© 2026 RBM Security Services
