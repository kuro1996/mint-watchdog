# Structure steering — Mint Watchdog

Repo layout (spec §5). Week 1 builds everything except `app/` (Week 2).

```
mint-watchdog/
├── .kiro/
│   ├── specs/
│   │   ├── mint-watchdog/        # requirements.md, design.md, tasks.md
│   │   └── rubric-scorer/        # requirements.md, design.md, tasks.md
│   ├── steering/                 # product.md, tech.md, structure.md
│   ├── hooks/                    # on-save-run-tests.json, before-commit-verify.json
│   ├── agents/                   # verifier.md, rubric-reviewer.md
│   └── settings/mcp.json         # github, filesystem, fetch — config only, no credentials
├── app/                          # Week 2: Next.js dashboard (placeholder README in Week 1)
├── server/
│   ├── main.py                   # one pipeline pass: ingest → verify → score → store
│   ├── api.py                    # stdlib read-only HTTP API (GET /health, /leads, /scores)
│   ├── requirements.txt          # stdlib + pycryptodome (Keccak only)
│   ├── ingest/                   # x_watch.py, telegram_watch.py, extract.py
│   ├── verify/                   # rpc.py (multi-endpoint), sourcify.py, probe.py
│   ├── score/                    # rubric.py (pure), preview.py (baw rules as code)
│   └── store/                    # db.py (SQLite mintwatch.db — gitignored)
├── tests/                        # test_scorer.py, test_rpc_fallback.py,
│                                 # test_preview.py, test_store.py, test_ingest.py
├── docs/
│   ├── DEMO.md                   # demo script outline (spec §6)
│   └── KIRO-USAGE.md             # Kiro-usage write-up outline (spec §5)
├── LICENSE                       # MIT
├── README.md
└── .gitignore                    # MUST NOT ignore .kiro; MUST ignore *.db, __pycache__
```

## Conventions

- One responsibility per module; small files; docstrings state the rule
  the code enforces, not just what it does.
- All on-chain reads go through `server/verify/rpc.py`. Nothing else
  touches an RPC endpoint directly.
- All scoring goes through `server/score/rubric.py`. Nothing else computes
  a score.
- All persistence goes through `server/store/db.py`. Nothing else opens
  the database file.
- Ingest functions take an injectable `fetcher` so tests never hit the
  network.
- `.gitignore` never ignores `.kiro/` — the whole point of Kiroween is that
  `/.kiro` is in the repo. It DOES ignore `*.db`, `__pycache__/`, `.env`.
- No file may contain a secret, seed, private key, or wallet address beyond
  the one public example wallet in the spec.
