═══════════════════════════════════════════════════════════
  MI LOGISTICS — LOGO REVIEW APP
  Setup & Sharing Guide
═══════════════════════════════════════════════════════════

FOLDER STRUCTURE
────────────────
mi_logos/
├── app.py                ← Flask server + database logic
├── README.txt            ← This file
├── templates/
│   ├── index.html        ← Home page (intro + video)
│   ├── logos.html        ← Logo voting page
│   └── results.html      ← Results dashboard
└── static/
    ├── logo.png          ← Already copied in ✓
    ├── intro_video.mp4   ← *** COPY YOUR VIDEO HERE ***
    └── (any extra logo files go here too)


STEP 1 — COPY YOUR VIDEO
─────────────────────────
Copy your video file into the static/ folder and rename it:

    intro_video.mp4

Or open templates/index.html and change line:
    src="/static/intro_video.mp4"
to whatever filename you used.


STEP 2 — INSTALL FLASK (one time only)
───────────────────────────────────────
Open Terminal (or Command Prompt on Windows) and run:

    pip install flask

If you get a permission error on Mac/Linux:
    pip3 install flask


STEP 3 — RUN THE APP
──────────────────────
Navigate into the mi_logos folder:

    cd path/to/mi_logos

Then start the server:

    python app.py

You'll see:
    MI LOGOS — running at http://localhost:5000

Open your browser and go to:    http://localhost:5000


PAGES
──────
  http://localhost:5000          ← Home page (intro sequence)
  http://localhost:5000/logos    ← Logo voting
  http://localhost:5000/results  ← Live results dashboard


═══════════════════════════════════════════════════════════
  SHARING OPTIONS (so your boss can access it)
═══════════════════════════════════════════════════════════

OPTION A — Same WiFi network (easiest)
────────────────────────────────────────
If you and your boss are on the same WiFi:
1. Find your laptop's local IP address:
   • Mac/Linux: run  ifconfig  in Terminal → look for "inet" under en0
   • Windows:   run  ipconfig  → look for "IPv4 Address"
   Example: 192.168.1.45

2. Your boss opens:  http://192.168.1.45:5000
   (app.py already runs on 0.0.0.0 so this works automatically)


OPTION B — Share over the internet with ngrok (free, easy)
───────────────────────────────────────────────────────────
1. Download ngrok: https://ngrok.com/download
2. Run your Flask app (python app.py)
3. In a NEW terminal window run:
       ngrok http 5000
4. ngrok gives you a public URL like:
       https://abc123.ngrok-free.app
5. Send that URL to your boss — works from anywhere!
   (Free tier: URL changes each session, that's fine for testing)


OPTION C — Email/USB (offline, no server needed)
─────────────────────────────────────────────────
For a quick offline preview WITHOUT the database:
Zip the whole mi_logos folder and send it.
Your boss opens templates/index.html directly in a browser.
Note: voting won't save (needs Flask), but the visual/video works.


═══════════════════════════════════════════════════════════
  ADDING MORE LOGO CONCEPTS
═══════════════════════════════════════════════════════════
Open templates/logos.html and find the LOGOS array near the top.
Copy one of the existing objects and change:
  - id:    unique name  e.g. 'concept-e'
  - name:  display name
  - src:   '/static/your_new_logo.png'
  - bg:    background class (bg-dark / bg-light / bg-mid / bg-slate)
  - blurb: short research note for your boss to read


═══════════════════════════════════════════════════════════
  ADJUSTING TIMING
═══════════════════════════════════════════════════════════
Open templates/index.html and find near the top of <script>:

  const LOGO_HOLD   = 3.0;   // seconds each logo is shown
  const FLASH_TIME  = 0.35;  // seconds for black/white flash
  const INTRO_TOTAL = 17;    // total intro length in seconds
  const FREEZE_SECS = 20;    // seconds video is frozen before playing

Change these numbers and save — no restart needed (just refresh browser).


═══════════════════════════════════════════════════════════
  DATABASE
═══════════════════════════════════════════════════════════
Votes are stored in  logos.db  (auto-created on first run).
To view raw data, install DB Browser for SQLite (free):
    https://sqlitebrowser.org
Or use the built-in results page at /results.


To reset all votes (start fresh):
  Delete  logos.db  — it will be recreated on next run.
═══════════════════════════════════════════════════════════
