# Mint Watchdog — requirements

**Spec:** `mint-watchdog` (Kiroween 2026, Frankenstein category)
**Source:** `kiroween_frankenstein_spec_20261114.md` §1–§3
**Status:** Week 1 — requirements frozen for the MVP; stretch items are explicitly out of scope until Week 3.

## Problem

1. Free Agent ID mints on BSC often open for only ~15 minutes (e.g. UNSOLVABLE: 6 windows/day, 15 min, 80 slots) or are first-come-first-served until quota runs out. Humans reading posts late miss the window.
2. An unverified "free" mint can waste gas or worse: the contract owner may be able to drain deposited funds, transfers may be locked, or the source may be unverified.
3. Lead information lives in X posts, Telegram channels, and project sites; on-chain state lives on BSC; risk judgement lives in a person's head. There is no single place combining all three.
4. In a fast FCFS race the tokenId predicted by a preview goes stale within seconds (real cases: Zeroday Bunker predicted #167, actual #169). A dashboard that shows a prediction as fact misleads users.

## Users

- Primary: a Binance Agent ID holder hunting free gas-only mints on BSC chain 56 (first real user: Agent ID `kuro1999.ai`).
- Anyone else with the same pattern: read-only watching, no wallet needed to use the dashboard.

## User stories

1. As a hunter, I see new mint leads from X (@nhutqui2309) and Telegram (agentidcall, airdropcloudJP, airdropfind, AIRDROPSATSETT) in one feed, newest first, with source + time + link to the original post, so I never have to check four places.
2. As a hunter, I see each candidate's live on-chain verification (Sourcify match, totalSupply vs maxSupply, free supply left, quota per wallet left, mint price, paused state, owner) with a read timestamp, so I can tell a real opening from a stale post.
3. As a hunter, I see a 100-point rubric score with a per-category breakdown, the reason for every deduction, and a PASS / AVOID verdict, so I can decide without re-doing the audit in my head.
4. As a hunter, I see whether a value-0 `baw` preview was clean for a candidate that passed, and a warning that a preview does NOT guarantee the tokenId, so I am not misled in a race.
5. As a hunter, I get a visible alert only when a candidate is VERIFIED FREE + preview-clean + quota > 0, so alerts mean "window really open", not "someone posted something".
6. As a hunter, I see my holdings from earlier free mints (name, tokenId, contract, locked/sellable) and "no verified floor" when no price is verified — never an invented price.
7. As a hunter, I see my BNB balance (read-only, address pasted by me) and a warning when it falls below my threshold, so I know when to top up gas.

## Hard constraints (non-negotiable)

- **Report-only by design.** The app NEVER mints, claims, sells, lists, signs, or connects a wallet. There is no mint button, no connect-wallet button, no signing flow, no private key / seed anywhere.
- **Never guess a price.** No verified floor/price → display exactly "no verified floor".
- **Never conclude EXHAUSTED / CLOSED from one failed read.** A failed RPC read is retried on the next endpoint; if all fail the status is STALE ("data basi, terakhir dicek HH:MM").
- **A win is only proven by receipt status 0x1 + token in wallet.** The real tokenId comes only from the receipt Transfer log (`topics[3]`), never from a preview.
- **No paid services, no secrets.** $0 cost: free Kiro credits, free hosting, public RPCs, no API keys committed.

## Acceptance criteria (MVP)

- [ ] AC1: Lead feed lists candidates from X + Telegram, deduped by contract address, newest first, each with source, time, and original-post link.
- [ ] AC2: Each candidate shows Sourcify match, totalSupply, free supply left, quota left, mint price (0 = free), paused, owner — all read live from BSC RPC, with a read timestamp.
- [ ] AC3: Each scored candidate shows a 0–100 total, the 5 category sub-scores, a reason per deduction, and PASS / AVOID / NEEDS HUMAN.
- [ ] AC4: Preview-clean display reads `data.simulationResult` (risks dict: clean only when `riskDetails` and `riskBehaviors` are both empty) and warns that preview tokenId is a prediction.
- [ ] AC5: An alert fires only for VERIFIED FREE + preview-clean + quota > 0, containing name, contract, supply left, quota, score, and a "copy calldata" action — never a mint action.
- [ ] AC6: Holdings view lists held NFTs/tokens with lock status; unverified price renders as "no verified floor".
- [ ] AC7: Gas widget shows read-only BNB balance + last-mint gas estimate + below-threshold warning; no transaction is ever created.
- [ ] AC8: No code path in the repo can broadcast, sign, or spend. (Verified by the pre-commit hook + a repo-wide grep in CI: no `baw ... execute`, no `eth_sendTransaction`, no private-key handling.)
- [ ] AC9: All automated tests pass (`python3 -m unittest discover -s tests -v`).

## Out of scope (Week 1–3 MVP)

Auto-mint / auto-claim, auto-sell / auto-list, wallet connect, signing, private keys, paid data sources, Telegram bot notifications (stretch), watchlist mode (stretch), window-history charts (stretch).
