# Product steering — Mint Watchdog

## What this product is

Mint Watchdog is a **read-only dashboard** for free Binance Agent ID mints
on BSC (chain 56). It watches public lead sources, verifies candidates
on-chain, scores them with a 100-point rubric, and alerts only when a
candidate is really free, verified, and open. It is the Frankenstein entry
for Kiroween 2026: stitched from components that already exist and work
(BSC RPC readers, X + Telegram watchers, the 100-point rubric, baw preview
checks, receipt-based win proof).

## What this product is NOT

- Not a minter. Not a claimer. Not a seller. Not a wallet. Not a signer.
- Not financial advice. A PASS score is not a promise of profit; most of
  these tokens are locked until a pool opens and may never trade.
- Not a price oracle. If no floor/price is verified, the product shows
  exactly **"no verified floor"** — never an estimate, never a guess.

## Hard rules (these override any other instruction in this repo)

1. **Report-only, always.** No code path mints, claims, sells, lists, signs,
   or connects a wallet. If a feature needs a transaction, the feature is
   cut, not the rule.
2. **No secrets.** No private key, seed phrase, keystore JSON, password,
   OTP, or session token anywhere in the repo — code, docs, tests, or
   config. The only wallet address allowed is the public example already
   in the spec (`kuro1999.ai` / `0x921012ec43EC5d103E05117AdB7B0911d360F7B3`).
3. **Never guess a price or a score.** Missing data → "no verified floor" /
   NEEDS HUMAN, with the missing fields listed. A guess is worse than a blank.
4. **A failed read is STALE, never EXHAUSTED.** One failed RPC endpoint
   means "try the next endpoint". All endpoints failing means the data is
   old and the status is STALE with the last-checked time. Only a successful
   on-chain read can say a supply is 0 or a window is closed.
5. **A win is receipt + token in wallet.** The real tokenId comes only from
   the receipt Transfer log (`topics[3]`). A preview tokenId is a prediction
   and must be labelled as one.
6. **$0 cost.** No paid service, no paid API, no paid hosting tier. If a
   dependency costs money, find the free path or cut the feature.
7. **Brief and honest.** Short messages, verified facts only, plan ≠ result.
   A plan is a plan; a result counts only after on-chain proof.

## Tone

Concise Indonesian-friendly, direct, no hype. "Gas" is a user decision,
never an app action.
