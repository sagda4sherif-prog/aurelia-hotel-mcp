from mcp.server.fastmcp import FastMCP
import sqlite3

mcp = FastMCP("Compensation Tool")

DATABASE = "hotel.db"


def get_db():
    return sqlite3.connect(DATABASE)


@mcp.tool()
def approve_compensation(
    request_id: int,
    approved_by: int,
    amount: float
):
    """
    Approve a guest compensation request.

    Defensive Design:
    - Request must exist.
    - Amount must be positive.
    - Amount must not exceed the requested compensation.
    """

    if amount <= 0:
        return {
            "success": False,
            "message": "Compensation amount must be greater than zero."
        }

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT compensation_amount, approval_status
        FROM Compensations
        WHERE request_id = ?
    """, (request_id,))

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return {
            "success": False,
            "message": "Compensation request not found."
        }

    requested_amount, status = row

    if status == "Approved":
        conn.close()
        return {
            "success": False,
            "message": "This compensation has already been approved."
        }

    if amount > requested_amount:
        conn.close()
        return {
            "success": False,
            "message": "Approved amount cannot exceed the requested amount."
        }

    cursor.execute("""
        UPDATE Compensations
        SET
            approval_status = 'Approved',
            approved_by = ?,
            approved_at = CURRENT_TIMESTAMP,
            compensation_amount = ?
        WHERE request_id = ?
    """, (approved_by, amount, request_id))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "request_id": request_id,
        "approved_amount": amount,
        "message": "Compensation approved successfully."
    }


if __name__ == "__main__":
    mcp.run()
