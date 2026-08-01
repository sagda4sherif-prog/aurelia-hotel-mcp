from datetime import datetime, timezone
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict
from .keyword_search import KeywordStore

# Global episodic store scoped to hotel guests
guest_episodic_store = KeywordStore()

class GuestMemoryRoutingDecision(BaseModel):
    reasoning: str
    destination: Literal["forget", "episodic"]
    event_summary: Optional[str] = None
    context: Optional[str] = None
    outcome: Optional[str] = None

    model_config = ConfigDict(extra="forbid")

def decide_guest_memory_fate(turn_text: str) -> GuestMemoryRoutingDecision:
    """
    Determines if a guest's statement contains lasting preferences, 
    complaints, or special requirements worth remembering.
    """
    lower_text = turn_text.lower()
    if any(keyword in lower_text for keyword in ["prefer", "allergy", "complaint", "vip", "quiet", "smoke"]):
        return GuestMemoryRoutingDecision(
            reasoning="Guest stated an important preference or issue worth retaining for future visits.",
            destination="episodic",
            event_summary=turn_text,
            context="Expressed during hotel interaction",
            outcome="Saved to guest memory profile"
        )
    return GuestMemoryRoutingDecision(reasoning="Routine interaction, not worth storing.", destination="forget")

def maybe_remember_guest_event(turn_text: str, guest_id: str):
    decision = decide_guest_memory_fate(turn_text)
    if decision.destination == "forget":
        return

    guest_episodic_store.upsert(
        payload={
            "event_summary": decision.event_summary,
            "context": decision.context,
            "outcome": decision.outcome,
        },
        metadata={
            "entity_id": guest_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

def load_guest_memory_context(guest_id: str, opening_message: str, top_k: int = 3) -> str:
    matches = guest_episodic_store.query(
        query_text=opening_message,
        top_k=top_k,
        filter={"entity_id": guest_id},
    )

    if not matches:
        return "No prior history or preferences found for this guest."

    lines = [f"- {m['payload']['event_summary']}" for m in matches]
    return "Relevant past guest notes:\n" + "\n".join(lines)

# Demo script to verify sessions
if __name__ == "__main__":
    guest_id = "guest_sarah_101"

    print("=== SESSION 1 (Guest Interaction) ===")
    session_turns = [
        "Hello, how is the weather today?",
        "I strongly prefer a quiet room away from the elevator because I'm a light sleeper.",
        "Also, I have a severe allergy to feather pillows."
    ]
    for turn in session_turns:
        maybe_remember_guest_event(turn, guest_id)
        print(f"Processed: {turn!r}")

    print("\n=== SESSION 2 (New Check-in: Recalling Preferences) ===")
    print(load_guest_memory_context(guest_id, "Does this guest have any room preferences or sleeping requirements?"))

    print("\n=== SESSION 2b (Checking Allergies) ===")
    print(load_guest_memory_context(guest_id, "Are there any allergy alerts for this guest?"))