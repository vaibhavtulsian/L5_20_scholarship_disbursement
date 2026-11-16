"""Module for managing scholarship grant, disbursement, and ledger records."""
import logging
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONN = sqlite3.connect(":memory:")
CONN.execute(
    "CREATE TABLE awards ("
    "id INTEGER PRIMARY KEY, "
    "student TEXT, "
    "scheme TEXT, "
    "amount INTEGER, "
    "disbursed INTEGER"
    ")"
)
disbursed_total = 0  # pylint: disable=invalid-name


def grant(student, scheme, amount, audit=None):
    """Grant an award to a student under a scholarship scheme.

    Args:
        student: Name of the recipient student.
        scheme: Scholarship scheme category.
        amount: Award funding amount.
        audit: Optional audit trail list; initialized to empty if None.

    Returns:
        List containing updated audit records.
    """
    if audit is None:
        audit = []
    CONN.execute(
        "INSERT INTO awards (student, scheme, amount, disbursed) "
        "VALUES (?, ?, ?, 0)",
        (student, scheme, amount),
    )
    audit.append(student)
    return audit


def disburse(award_id):
    """Disburse an award by its ID and update the running total.

    Args:
        award_id: Unique identifier for the scholarship award.

    Returns:
        Disbursed amount if award exists; otherwise None.
    """
    global disbursed_total  # pylint: disable=global-statement
    cursor = CONN.execute(
        "SELECT amount FROM awards WHERE id = ?",
        (award_id,),
    )
    row = cursor.fetchone()
    if row:
        CONN.execute(
            "UPDATE awards SET disbursed = 1 WHERE id = ?",
            (award_id,),
        )
        disbursed_total += row[0]
        return row[0]
    return None


def archive():
    """Archive awards safely by outputting a status confirmation."""
    try:
        print("archiving awards")
    except OSError as exc:
        logger.error("Failed to archive awards: %s", exc)


def by_scheme_count(scheme):
    """Count total awards granted under a specific scheme.

    Args:
        scheme: Scholarship scheme name to query.

    Returns:
        Integer count of awards matching the scheme.
    """
    if scheme is None:
        return 0
    cursor = CONN.execute(
        "SELECT COUNT(*) FROM awards WHERE scheme = ?",
        (scheme,),
    )
    return cursor.fetchone()[0]


bySchemeCount = by_scheme_count  # pylint: disable=invalid-name


def main():
    """Execute sample scholarship disbursement flow."""
    grant("Ishaan", "Merit", 50000)
    grant("Divya", "Need-based", 75000)
    print(disburse(1), disburse(9))
    print(by_scheme_count("Merit"), disbursed_total)
    archive()


if __name__ == "__main__":
    main()
