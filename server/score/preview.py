"""baw preview rules, as code — read-only simulation checks.

These functions encode the pitfalls recorded in ~/AGENTS.md (lessons from
real mints). They operate on a parsed ``baw contract-call preview --json``
result. They NEVER call baw and never broadcast anything: the preview is
run by the user on their own baw-logged-in machine and its JSON is imported
here. The web app never calls baw.

Pitfalls encoded:
1. Clean fields live under ``data.simulationResult``, NOT under ``data``.
2. ``risks`` is a DICT {addresses, riskDetails, riskBehaviors}. Clean only
   when ``riskDetails`` AND ``riskBehaviors`` are both empty. A non-empty
   dict is NOT dirty by itself.
3. ``balanceChanges`` entries use the key ``contractAddress``, NOT
   ``tokenAddress`` (``tokenAddress`` is accepted as a fallback only).
4. ERC20 ``balanceChanges[].change`` can arrive as a JSON FLOAT
   (e.g. ``1e+25`` for 10,000,000 MIAO). ``int(float)`` is NOT exactly
   ``10**25`` (float64 rounding). Compare via ``Decimal(str(v))``.
5. A preview tokenId is a PREDICTION. The real tokenId comes only from the
   receipt Transfer log ``topics[3]`` (Zeroday: predicted #167, actual #169).
6. ``baw contract-call execute`` returns the hash as ``data.txHash``,
   NOT ``data.transactionHash``.
7. Never use ``(x or -1) == 0``: when x == 0, ``0`` is falsy, so the check
   silently becomes ``-1 == 0`` (False). Compare directly (``x == 0``).
"""

from decimal import Decimal, InvalidOperation

TRANSFER_TOPIC = (
    "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
)  # keccak256("Transfer(address,address,uint256)")


def simulation_result(preview):
    """Return the ``data.simulationResult`` dict ({} when absent)."""
    if not isinstance(preview, dict):
        return {}
    data = preview.get("data") or {}
    return data.get("simulationResult") or {}


def is_preview_clean(preview):
    """Check whether a baw value-0 preview is clean.

    Returns ``(clean: bool, reasons: list[str])``. Clean requires:
    no ``simulationErrorDetail``, and empty ``riskDetails`` and
    ``riskBehaviors`` under ``risks``.
    """
    sim = simulation_result(preview)
    reasons = []
    if not sim:
        # No simulation at all: cannot confirm clean. Never guess.
        reasons.append("no simulationResult in preview")
        return False, reasons
    error = sim.get("simulationErrorDetail")
    if error:
        reasons.append("simulation error: %s" % (error,))
    risks = sim.get("risks") or {}
    if not isinstance(risks, dict):
        reasons.append("risks field is not a dict (unexpected preview shape)")
        return False, reasons
    details = risks.get("riskDetails") or []
    behaviors = risks.get("riskBehaviors") or []
    if details:
        reasons.append("riskDetails non-empty: %s" % (details,))
    if behaviors:
        reasons.append("riskBehaviors non-empty: %s" % (behaviors,))
    return (not reasons), reasons


def balance_change_for(balance_changes, contract_address):
    """Find the ``change`` for a contract in ``balanceChanges``.

    Matches on ``contractAddress`` first, ``tokenAddress`` as fallback.
    Returns the raw change value, or None when the contract is absent.
    """
    if not balance_changes:
        return None
    target = (contract_address or "").lower()
    for entry in balance_changes:
        if not isinstance(entry, dict):
            continue
        addr = entry.get("contractAddress", entry.get("tokenAddress")) or ""
        if addr.lower() == target:
            return entry.get("change")
    return None


def erc20_change_equals(change, expected_int):
    """Compare an ERC20 balance change to an expected integer amount.

    Uses ``Decimal(str(v))`` so a JSON float like ``1e+25`` compares
    exactly to ``10**25`` (``int(1e+25)`` does not).
    """
    try:
        return Decimal(str(change)) == Decimal(expected_int)
    except (InvalidOperation, ValueError, TypeError):
        return False


def execute_tx_hash(execute_result):
    """Extract the tx hash from a broadcast result: ``data.txHash``."""
    if not isinstance(execute_result, dict):
        return None
    return (execute_result.get("data") or {}).get("txHash")


def receipt_token_id(receipt):
    """Real minted tokenId from a receipt's Transfer log (topics[3]).

    Returns the int tokenId, or None when no Transfer log is present.
    The preview's predicted tokenId must NEVER be used here.
    """
    if not isinstance(receipt, dict):
        return None
    for log in receipt.get("logs") or []:
        topics = log.get("topics") or []
        if len(topics) >= 4 and topics[0].lower() == TRANSFER_TOPIC:
            try:
                return int(topics[3], 16)
            except (TypeError, ValueError):
                continue
    return None


def receipt_success(receipt):
    """A win counts only on receipt status 0x1 (never on broadcast alone)."""
    if not isinstance(receipt, dict):
        return False
    status = receipt.get("status")
    if isinstance(status, str):
        return status in ("0x1", "1")
    return status == 1
