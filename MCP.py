from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context

import sqlite3
import time
from jsonschema import validate

# ======================================================
# MCP SERVER
# ======================================================

mcp = FastMCP(
    "Aurelia Hotel Recovery Server",
    json_response=True
)

# ======================================================
# DATABASE
# ======================================================

DB = "......"          


def get_db():
    return sqlite3.connect(DB)


# ======================================================
# CAPABILITY NEGOTIATION
# ======================================================

SERVER_CAPABILITIES = {
    "tools": True,
    "resources": True,
    "prompts": True,
    "notifications": True,
    "progress": True
}


@mcp.tool()
def initialize():

    """
    Capability Negotiation
    """

    return {
        "server": "Aurelia Hotel Recovery Server",
        "version": "1.0",
        "capabilities": SERVER_CAPABILITIES
    }
@mcp.tool()
def get_reservation(reservation_id: int):

    """
    Return reservation details.
    """

    conn = get_db()

    row = conn.execute(
        """
        SELECT *
        FROM Reservations
        WHERE reservation_id = ?
        """,
        (reservation_id,)
    ).fetchone()

    conn.close()

    if not row:
        return {
            "error":
            "Reservation not found."
        }

    return {
        "reservation_id": row[0],
        "guest_name": row[1],
        "room_type": row[2],
        "branch": row[3],
        "status": row[4]
    }
@mcp.tool()
def search_available_rooms(room_type: str):

    validate(

    instance={

        "room_type": room_type

    },

    schema=ROOM_SEARCH_SCHEMA

)
    conn = get_db()

    rows = conn.execute(
        """
        SELECT
            branch_name,
            available_rooms
        FROM Rooms
        WHERE room_type = ?
        AND available_rooms > 0
        """,
        (room_type,)
    ).fetchall()

    conn.close()

    return rows
@mcp.tool()
def find_alternative_branch(room_type: str):

    conn = get_db()

    rows = conn.execute(
        """
        SELECT
            branch_name,
            available_rooms
        FROM Rooms
        WHERE room_type = ?
        ORDER BY available_rooms DESC
        """,
        (room_type,)
    ).fetchall()

    conn.close()

    if not rows:
        return {
            "message":
            "No branches available."
        }

    return rows
@mcp.tool()
def approve_guest_transfer(
    reservation_id: int,
    new_branch: str,
    employee_role: str
):

    # Authorization

    if employee_role != "manager":

        return {
            "error":
            "Only managers can approve guest transfers."
        }

    conn = get_db()

    row = conn.execute(
        """
        SELECT status
        FROM Reservations
        WHERE reservation_id = ?
        """,
        (reservation_id,)
    ).fetchone()

    if not row:

        conn.close()

        return {
            "error":
            "Reservation not found."
        }

    # Elicitation Trigger

    if row[0] == "VIP":

        conn.close()

        return {

            "requires_human_confirmation": True,

            "message":

            "VIP transfer requires manager confirmation."

        }

    conn.execute(
        """
        UPDATE Reservations
        SET branch = ?
        WHERE reservation_id = ?
        """,
        (new_branch, reservation_id)
    )

    conn.commit()

    conn.close()

    return {

        "status":

        "Guest transferred successfully."

    }
# ======================================================
# RESOURCES
# ======================================================

@mcp.resource(
    "policy://guest-compensation"
)
def compensation_policy():

    return """
Guest Compensation Policy

1. Overbooking:
   - Free room upgrade if available.
   - Complimentary breakfast.
   - Late checkout.

2. Room Under Maintenance:
   - Upgrade if possible.
   - 20% room discount.

3. Room Not Ready:
   - Free lounge access.
   - Welcome drink.

4. Guest Transfer:
   - Free transportation.
   - Discount voucher.

5. VIP Guest:
   - Manager approval required.
"""
@mcp.resource(
    "policy://manager-approval"
)
def manager_policy():

    return """
Manager approval is required when:

- VIP guest reservation
- Compensation exceeds $200
- Guest transfer to another branch
- Reservation cancellation after check-in
"""
@mcp.prompt()
def draft_guest_apology(
    guest_name: str,
    issue: str
):

    return f"""
Write a professional apology email.

Guest:
{guest_name}

Issue:
{issue}

The email should:

- apologize sincerely
- explain the situation
- reassure the guest
- remain professional
"""
@mcp.prompt()
def draft_transfer_message(
    guest_name: str,
    old_branch: str,
    new_branch: str
):

    return f"""
Write a message informing

Guest:
{guest_name}

that their reservation has been transferred

From:
{old_branch}

To:
{new_branch}

Use a polite and reassuring tone.
"""
@mcp.tool()
def search_all_branches(room_type: str):

    conn = get_db()

    branches = conn.execute(
        """
        SELECT branch_name
        FROM Branches
        """
    ).fetchall()

    conn.close()

    progress = []

    total = len(branches)

    for index, branch in enumerate(branches):

        time.sleep(1)

        percent = int(((index + 1) / total) * 100)

        progress.append(
            {
                "branch": branch[0],
                "progress": percent,
                "message":
                f"Searching {branch[0]}"
            }
        )

    return {
        "status": "completed",
        "progress_updates": progress
    }
@mcp.tool()
def recommend_compensation(issue: str):

    recommendations = {

        "Overbooking":
        "Free room upgrade and breakfast",

        "Maintenance":
        "20% room discount",

        "Room Not Ready":
        "Free lounge access",

        "Double Booking":
        "Upgrade to Deluxe Room",

        "VIP":
        "Luxury Suite Upgrade"
    }

    return {
        "issue": issue,
        "recommendation":
        recommendations.get(
            issue,
            "Manager review required"
        )
    }
@mcp.tool()
def analyze_reservation(
    reservation_id: int
):

    conn = get_db()

    row = conn.execute(
        """
        SELECT
            guest_name,
            room_type,
            branch,
            status
        FROM Reservations
        WHERE reservation_id = ?
        """,
        (reservation_id,)
    ).fetchone()

    conn.close()

    if not row:

        return {
            "error":
            "Reservation not found."
        }

    guest = row[0]
    room = row[1]
    branch = row[2]
    status = row[3]

    if status == "Overbooked":

        risk = "High"

        recommendation = "Transfer guest"

    elif status == "Maintenance":

        risk = "Medium"

        recommendation = "Upgrade room"

    else:

        risk = "Low"

        recommendation = "Normal check-in"

    return {

        "guest": guest,

        "room": room,

        "branch": branch,

        "status": status,

        "risk": risk,

        "recommendation": recommendation

    }
# ======================================================
# NOTIFICATIONS
# ======================================================

current_role = "receptionist"


@mcp.tool()
def get_available_tools():

    if current_role == "receptionist":

        return [
            "get_reservation",
            "search_available_rooms",
            "find_alternative_branch",
            "recommend_compensation"
        ]

    elif current_role == "manager":

        return [
            "get_reservation",
            "search_available_rooms",
            "find_alternative_branch",
            "recommend_compensation",
            "approve_guest_transfer",
            "resolve_overbooking"
        ]

    return []
@mcp.tool()
def promote_to_manager():

    global current_role

    current_role = "manager"

    return {

        "notification":
        "tools/list_changed",

        "new_role":
        current_role,

        "available_tools":
        get_available_tools()

    }
@mcp.tool()
def demote_to_receptionist():

    global current_role

    current_role = "receptionist"

    return {

        "notification":
        "tools/list_changed",

        "new_role":
        current_role,

        "available_tools":
        get_available_tools()

    }
@mcp.tool()
def resolve_overbooking(

    reservation_id: int,

    new_branch: str,

    employee_role: str

):

    if employee_role != "manager":

        return {
            "error":
            "Only managers can resolve overbookings."
        }

    conn = get_db()

    reservation = conn.execute(
        """
        SELECT status
        FROM Reservations
        WHERE reservation_id = ?
        """,
        (reservation_id,)
    ).fetchone()

    if reservation is None:

        conn.close()

        return {

            "error":
            "Reservation not found."

        }

    if reservation[0] != "Overbooked":

        conn.close()

        return {

            "error":
            "Reservation is not overbooked."

        }

    conn.execute(
        """
        UPDATE Reservations

        SET branch = ?,
            status = 'Transferred'

        WHERE reservation_id = ?
        """,
        (new_branch, reservation_id)
    )

    conn.commit()

    conn.close()

    return {

        "status":
        "Guest successfully transferred.",

        "new_branch":
        new_branch

    }
ROOM_SEARCH_SCHEMA = {

    "type": "object",

    "properties": {

        "room_type": {

            "type": "string"

        }

    },

    "required": [

        "room_type"

    ],

    "additionalProperties": False

}
@mcp.prompt()
def draft_compensation_email(

    guest_name: str,

    compensation: str

):

    return f"""
Write a professional email.

Guest:
{guest_name}

Compensation:

{compensation}

Explain why the hotel is offering
this compensation.

Remain polite and empathetic.
"""
@mcp.resource(
    "policy://vip-guidelines"
)
def vip_guidelines():

    return """
VIP Guest Policy

- Never downgrade room.

- Manager approval required
  before transferring.

- Offer complimentary transport.

- Offer premium compensation
  when necessary.
"""
if __name__ == "__main__":

    print("Starting Aurelia Hotel MCP Server...")

    mcp.run()