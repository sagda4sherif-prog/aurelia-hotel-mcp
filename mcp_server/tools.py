from __future__ import annotations
from . import mcp
from .schema import ROOM_SEARCH_SCHEMA
from .server import get_db
from jsonschema import validate
import time

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
            "error": "Reservation not found."
        }

    return {
        "reservation_id": row[0],
        "room_id": row[1],
        "check_in": row[2],
        "check_out": row[3],
        "reservation_status": row[4],
    }

@mcp.tool()
def search_available_rooms(room_type: str):
    validate(
        instance={"room_type": room_type},
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
            "message": "No branches available."
        }
    return rows

@mcp.tool()
def approve_guest_transfer(
    reservation_id: int,
    new_branch: str,
    employee_role: str
):
    if employee_role != "manager":
        return {
            "error": "Only managers can approve guest transfers."
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
            "error": "Reservation not found."
        }

    if row[0] == "VIP":
        conn.close()
        return {
            "requires_human_confirmation": True,
            "message": "VIP transfer requires manager confirmation."
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
        "status": "Guest transferred successfully."
    }

@mcp.tool()
def search_all_branches(room_type: str):
    conn = get_db()
    branches = conn.execute(
        """
        SELECT branch_name
        FROM Hotels
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
                "message": f"Searching {branch[0]}"
            }
        )

    return {
        "status": "completed",
        "progress_updates": progress
    }

@mcp.tool()
def recommend_compensation(issue: str):
    recommendations = {
        "Overbooking": "Free room upgrade and breakfast",
        "Maintenance": "20% room discount",
        "Room Not Ready": "Free lounge access",
        "Double Booking": "Upgrade to Deluxe Room",
        "VIP": "Luxury Suite Upgrade"
    }

    return {
        "issue": issue,
        "recommendation": recommendations.get(
            issue,
            "Manager review required"
        )
    }

@mcp.tool()
def analyze_reservation(reservation_id: int):
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
            "error": "Reservation not found."
        }

    guest, room, branch, status = row[0], row[1], row[2], row[3]

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

@mcp.tool()
def resolve_overbooking(
    reservation_id: int,
    new_branch: str,
    employee_role: str
):
    if employee_role != "manager":
        return {
            "error": "Only managers can resolve overbookings."
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
            "error": "Reservation not found."
        }

    if reservation[0] != "Overbooked":
        conn.close()
        return {
            "error": "Reservation is not overbooked."
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
        "status": "Guest successfully transferred.",
        "new_branch": new_branch
    }

@mcp.tool()
def approve_compensation(
    request_id: int,
    approved_by: int,
    amount: float
):
    """
    Approve compensation request with validation.
    """
    if amount > 4000.0:
        return {
            "error": "Compensation amount exceeds allowed limit."
        }

    return {
        "status": "approved",
        "request_id": request_id,
        "amount": amount,
        "approved_by": approved_by
    }