/** Demo fixtures — three REAL mints from the spec (§2), used so the
 * dashboard is demonstrable while the live lead feed is empty.
 * Every value below is a verified on-chain fact from 2026-11-13/14
 * (receipt 0x1 + token proven in the wallet). They are labelled
 * "Demo example" in the UI and kept separate from live API data.
 * No price is invented: every fixture says "no verified floor". */

import type { Holding, LeadDetail } from "./api";

export interface PreviewFixture {
  clean: boolean;
  requestId: string;
  simulatedAt: string;
  predictedTokenId: string | null;
  actualTokenId: string | null;
  balanceChanges: string;
  risks: string;
  txHash: string;
  gasUsed: number;
}

export interface DemoCandidate extends LeadDetail {
  preview: PreviewFixture;
}

export const DEMO_CANDIDATES: DemoCandidate[] = [
  {
    id: 9001,
    contract: "0x4158B701EaA30E8FaDBaA526F70780A38318c1C4",
    name: "Lumen Findings — Case 6",
    source: "x",
    source_url: "https://x.com/nhutqui2309",
    first_seen: "2026-11-13",
    status: "VERIFIED_FREE",
    free_left: 1,
    quota_left: 1,
    verification: {
      checked_at: "2026-11-13T23:46:47+07:00",
      sourcify: "exact_match",
      total_supply: 1499,
      free_left: 1,
      quota_left: 1,
      mint_price: "0",
      paused: false,
      owner: "0x0000000000000000000000000000000000000000",
      status: "VERIFIED_FREE",
    },
    score: {
      scored_at: "2026-11-13T23:46:47+07:00",
      // Exact output of server/score/rubric.py for the evidence on file
      // (see the seeded live DB / tests/test_api.py) — not a remembered number.
      total: 48,
      categories: {
        security: 28,
        investor_protection: 17,
        anti_manipulation: 3,
        transparency: 0,
        market_viability: 0,
      },
      verdict: "PASS",
      hard_cap_applied: false,
      note: "Exact output of server/score/rubric.py for the evidence on file (see tests/test_api.py). Unknown fields earn 0 and are listed as missing — the manual check 2026-11-13 (≈68) gave partial credit for unknowns, which the code never does.",
      reasons: [
        "Security: identity-gated mint (-2)",
        "Anti-Manipulation: no liquidity pool formed (-5)",
        "Market Viability: no WBNB liquidity (-4)",
        "Market Viability: no paid shares sold (-3)",
      ],
      missing: [
        "locked_exit",
        "refund_at_risk",
        "per_identity_limit",
        "owner_discretionary_timing",
        "open_code_documents_risks",
        "team_non_anonymous",
        "independent_audit",
        "has_market_price",
      ],
    },
    preview: {
      clean: true,
      requestId: "7208d2a7811a48ac8aff2f9c9d2fc75fbb51b39ff6ca3",
      simulatedAt: "2026-11-13T23:55:00+07:00",
      predictedTokenId: "1500",
      actualTokenId: "1500",
      balanceChanges: "+1 FIND (ERC-721) to wallet, no BNB moved",
      risks: "riskDetails: [], riskBehaviors: [] — clean",
      txHash: "0x6e8e4ab4ecc729b81ea91886318b2e87e845d29ac2c9d2fc75fbb51b39ff6ca3",
      gasUsed: 195342,
    },
  },
  {
    id: 9002,
    contract: "0x4789B451fAc62E5d43f916AEC3aa813C3f327312",
    name: "Zeroday Bunker",
    source: "x",
    source_url: "https://x.com/nhutqui2309",
    first_seen: "2026-11-13",
    status: "VERIFIED_FREE",
    free_left: 1,
    quota_left: 1,
    verification: {
      checked_at: "2026-11-13T01:52:00+07:00",
      sourcify: "exact_match",
      total_supply: 168,
      free_left: 1,
      quota_left: 1,
      mint_price: "0",
      paused: false,
      owner: "0x0000000000000000000000000000000000000000",
      status: "VERIFIED_FREE",
    },
    score: {
      scored_at: "2026-11-13T01:52:00+07:00",
      // Regenerated 2026-11-14 with server/score/rubric.py from the
      // evidence below (audit fix): the old 71 total and its reason
      // strings were a manual estimate and did not match rubric.py.
      // Unknown fields earn 0 and are listed as missing.
      total: 51,
      categories: {
        security: 23,
        investor_protection: 25,
        anti_manipulation: 3,
        transparency: 0,
        market_viability: 0,
      },
      verdict: "PASS",
      hard_cap_applied: false,
      note: "Exact rubric.py output; manual check 2026-11-13 was ≈71 (partial credit for unknowns).",
      reasons: [
        "Security: live owner (-5)",
        "Security: identity-gated mint (-2)",
        "Anti-Manipulation: no liquidity pool formed (-5)",
        "Transparency: anonymous team (-5)",
        "Transparency: no independent audit (-4)",
        "Market Viability: no WBNB liquidity (-4)",
        "Market Viability: no paid shares sold (-3)",
        "Market Viability: no existing market price (-3)",
      ],
      missing: [
        "per_identity_limit",
        "owner_discretionary_timing",
        "open_code_documents_risks",
      ],
    },
    preview: {
      clean: true,
      requestId: "demo-zeroday-preview",
      simulatedAt: "2026-11-13T01:50:00+07:00",
      predictedTokenId: "167",
      actualTokenId: "169",
      balanceChanges: "+1 Zeroday Bunker NFT (ERC-721) to wallet, no BNB moved",
      risks: "riskDetails: [], riskBehaviors: [] — clean",
      txHash: "",
      gasUsed: 0,
    },
  },
  {
    id: 9003,
    contract: "0xb436617b7b5542f9c091a932654e9aeefa4a182a",
    name: "TEGONG MIAO",
    source: "agentidhub",
    source_url: "https://agentidhub.io",
    first_seen: "2026-11-12",
    status: "VERIFIED_FREE",
    free_left: 1,
    quota_left: 1,
    verification: {
      checked_at: "2026-11-13T01:54:00+07:00",
      sourcify: "exact_match",
      total_supply: 1,
      free_left: 1,
      quota_left: 1,
      mint_price: "0",
      paused: false,
      owner: "0x0000000000000000000000000000000000000000",
      status: "VERIFIED_FREE",
    },
    score: {
      scored_at: "2026-11-13T01:54:00+07:00",
      // Regenerated 2026-11-14 with server/score/rubric.py from the
      // evidence below (audit fix): the old 65 total and its reason
      // strings were a manual estimate and did not match rubric.py.
      // Tokens locked until 100% sellout = transfers locked + exit locked.
      total: 46,
      categories: {
        security: 23,
        investor_protection: 13,
        anti_manipulation: 10,
        transparency: 0,
        market_viability: 0,
      },
      verdict: "PASS",
      hard_cap_applied: false,
      note: "Exact rubric.py output; manual check 2026-11-13 was ≈65 (partial credit for unknowns).",
      reasons: [
        "Security: live owner (-5)",
        "Security: identity-gated mint (-2)",
        "Investor Protection: transfers are locked (-7)",
        "Investor Protection: exit / sell is locked (-5)",
        "Anti-Manipulation: no liquidity pool formed (-5)",
        "Transparency: anonymous team (-5)",
        "Transparency: no independent audit (-4)",
        "Market Viability: no WBNB liquidity (-4)",
        "Market Viability: no paid shares sold (-3)",
        "Market Viability: no existing market price (-3)",
      ],
      missing: ["owner_discretionary_timing", "open_code_documents_risks"],
    },
    preview: {
      clean: true,
      requestId: "demo-tegong-preview",
      simulatedAt: "2026-11-13T01:53:00+07:00",
      predictedTokenId: null,
      actualTokenId: null,
      balanceChanges: "+10,000,000 MIAO (ERC-20) to wallet, no BNB moved",
      risks: "riskDetails: [], riskBehaviors: [] — clean",
      txHash: "",
      gasUsed: 0,
    },
  },
];

/** Demo holdings — verified wallet contents, 2026-11-13/14. Every item
 * says "no verified floor" unless a price was verified (none was). */
export const DEMO_HOLDINGS: (Holding & { lockNote: string })[] = [
  { contract: "0x4158B701EaA30E8FaDBaA526F70780A38318c1C4", token_id: "1500", name: "Lumen Findings #1500 (Case 6)", locked: false, floor_note: "no verified floor", lockNote: "Transferable" },
  { contract: "0x4158B701EaA30E8FaDBaA526F70780A38318c1C4", token_id: "271", name: "Lumen Findings #271 (Case 2)", locked: false, floor_note: "no verified floor", lockNote: "Transferable" },
  { contract: "0x4789B451fAc62E5d43f916AEC3aa813C3f327312", token_id: "169", name: "Zeroday Bunker #169", locked: false, floor_note: "no verified floor", lockNote: "Transferable" },
  { contract: "0xb436617b7b5542f9c091a932654e9aeefa4a182a", token_id: null, name: "TEGONG MIAO — 10,000,000", locked: true, floor_note: "no verified floor", lockNote: "Locked until 100% sellout of 4,999 shares (0 paid sold)" },
  { contract: "0x2ccb3fa957e69abd46a6651cc1444ef2ea9bd591", token_id: "4211", name: "Shanhai Beasts 3 #4211", locked: false, floor_note: "no verified floor", lockNote: "Transferable" },
  { contract: "0x2ccb3fa957e69abd46a6651cc1444ef2ea9bd591", token_id: "4212", name: "Shanhai Beasts 3 #4212", locked: false, floor_note: "no verified floor", lockNote: "Transferable" },
  { contract: "0x5314071bba19943f58347ba5dec423e5032a6818", token_id: "698", name: "Obsidian Forge #698", locked: false, floor_note: "no verified floor", lockNote: "Transferable" },
  { contract: "0x8fdb9411753c58476a41f7b88a44989f8d687d63", token_id: "2803", name: "Soul Agent #2803", locked: false, floor_note: "no verified floor", lockNote: "Transferable" },
  { contract: "0xb8164afefc53910d7a74cece15a60a9e0c86089e", token_id: "828", name: "Meow Cards #828", locked: false, floor_note: "no verified floor", lockNote: "Transferable" },
  { contract: "0x7Bd361A88beC064283F77Af8dc781E6A84ceAaE9", token_id: null, name: "Pixel GateHound — 8,000 HOUND", locked: true, floor_note: "no verified floor", lockNote: "Locked until launch (21 / 8,000 paid shares sold)" },
  { contract: "0x4257AC3e0E2B6A4AF35A5D49bB61910305001825", token_id: null, name: "SIDECOIN — 50,000,000", locked: true, floor_note: "no verified floor", lockNote: "Locked until pool opens" },
  { contract: "0x398Fa8a4d9e6FE658E3ECD2F4B5CDC8F3562C522", token_id: null, name: "11•11 — 160,000", locked: true, floor_note: "no verified floor", lockNote: "Locked until pool opens at 5,000 paid shares" },
];

export function findDemoCandidate(contract: string): DemoCandidate | undefined {
  return DEMO_CANDIDATES.find(
    (c) => c.contract.toLowerCase() === contract.toLowerCase(),
  );
}
