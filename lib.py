# Library Management System (with copies, overdue fine, librarians)
# Data is stored temporarily in dictionaries/lists (lost when program exits).

from datetime import date, datetime, timedelta

# ---------- SETTINGS (NEW) ----------
LOAN_DAYS = 14          # number of days a book can be kept
FINE_PER_DAY = 2        # fine amount per overdue day (change as needed)

# ---------- DATA ----------
# CHANGED: each book now has "copies" (total) and "available" (copies on shelf)
books = {
    "B101": {"title": "Python Basics", "author": "John Smith", "copies": 3, "available": 3},
    "B102": {"title": "Computer Fundamentals", "author": "R. Kumar", "copies": 2, "available": 2},
    "B103": {"title": "Engineering Mathematics", "author": "A. Sharma", "copies": 1, "available": 1}
}

# NEW: librarians and the currently active librarian
librarians = {
    "L1": "Admin"
}
active_librarian = None   # holds the librarian ID who is logged in

# NEW: list of currently issued books (needed to calculate due date and fine)
issued_records = []       # each item: {book_id, member, issued_by, issue_date, due_date}


# ---------- HELPER FUNCTIONS ----------
def require_librarian():
    """Block actions if no active librarian is set."""
    if active_librarian is None:
        print("No active librarian. Please use option 7 / 8 to set one first.")
        return False
    return True


def read_date(prompt):
    """Read a date as DD-MM-YYYY. Pressing Enter gives today's date."""
    text = input(prompt).strip()
    if text == "":
        return date.today()
    try:
        return datetime.strptime(text, "%d-%m-%Y").date()
    except ValueError:
        return None


# ---------- BOOK FUNCTIONS ----------
def display_books():
    print("\n--- BOOK LIST ---")
    for book_id, d in books.items():
        status = "Available" if d["available"] > 0 else "Not Available"
        # NEW: shows total copies, available copies and issued copies
        print(book_id, "|", d["title"], "|", d["author"], "| Total:", d["copies"],
              "| Available:", d["available"], "| Issued:", d["copies"] - d["available"],
              "|", status)


def add_book():
    if not require_librarian():
        return
    book_id = input("Enter book ID: ").strip().upper()
    title = input("Enter book title: ").strip()
    author = input("Enter author name: ").strip()
    if not title or not author:
        print("Title and author cannot be empty.")
        return

    # NEW: number of copies
    try:
        copies = int(input("Enter number of copies: ").strip())
        if copies <= 0:
            raise ValueError
    except ValueError:
        print("Copies must be a positive number.")
        return

    if book_id in books:
        # NEW: if the book already exists, just add more copies
        books[book_id]["copies"] += copies
        books[book_id]["available"] += copies
        print("Book ID already exists. Added", copies, "more copies.")
        return

    books[book_id] = {"title": title, "author": author,
                      "copies": copies, "available": copies}
    print("Book added successfully.")


def search_book():
    keyword = input("Enter book ID or title: ").strip().lower()
    found = False
    for book_id, d in books.items():
        if keyword == book_id.lower() or keyword in d["title"].lower():
            print(book_id, "|", d["title"], "|", d["author"], "| Total:", d["copies"],
                  "| Available:", d["available"])
            found = True
    if not found:
        print("Book not found.")


def issue_book():
    if not require_librarian():
        return
    book_id = input("Enter book ID to issue: ").strip().upper()
    if book_id not in books:
        print("Book not found.")
        return
    if books[book_id]["available"] == 0:
        print("All copies of this book are already issued.")
        return

    member = input("Enter member name: ").strip()
    if not member:
        print("Member name cannot be empty.")
        return

    issue_date = date.today()
    due_date = issue_date + timedelta(days=LOAN_DAYS)

    books[book_id]["available"] -= 1
    issued_records.append({
        "book_id": book_id,
        "member": member,
        "issued_by": active_librarian,
        "issue_date": issue_date,
        "due_date": due_date
    })
    print("Book issued successfully.")
    print("Due date:", due_date.strftime("%d-%m-%Y"))


def return_book():
    if not require_librarian():
        return
    book_id = input("Enter book ID to return: ").strip().upper()
    if book_id not in books:
        print("Book not found.")
        return

    member = input("Enter member name: ").strip()

    # find the matching issue record
    record = None
    for r in issued_records:
        if r["book_id"] == book_id and r["member"].lower() == member.lower():
            record = r
            break
    if record is None:
        print("No issue record found for this book and member.")
        return

    # NEW: return date (press Enter for today) and fine calculation
    return_date = read_date("Enter return date DD-MM-YYYY (Enter = today): ")
    if return_date is None:
        print("Invalid date format.")
        return
    if return_date < record["issue_date"]:
        print("Return date cannot be before the issue date.")
        return

    overdue_days = (return_date - record["due_date"]).days
    fine = overdue_days * FINE_PER_DAY if overdue_days > 0 else 0

    books[book_id]["available"] += 1
    issued_records.remove(record)
    print("Book returned successfully.")
    print("Due date:", record["due_date"].strftime("%d-%m-%Y"))
    if fine > 0:
        print("Overdue by", overdue_days, "day(s). Fine amount: Rs.", fine)
    else:
        print("Returned on time. No fine.")


# NEW: show all currently issued books with overdue/fine status
def display_issued_books():
    print("\n--- ISSUED BOOKS ---")
    if not issued_records:
        print("No books are currently issued.")
        return
    today = date.today()
    for r in issued_records:
        overdue_days = (today - r["due_date"]).days
        fine = overdue_days * FINE_PER_DAY if overdue_days > 0 else 0
        print(r["book_id"], "|", books[r["book_id"]]["title"], "|", r["member"],
              "| Due:", r["due_date"].strftime("%d-%m-%Y"),
              "| Fine till today: Rs.", fine)


# ---------- LIBRARIAN FUNCTIONS (NEW) ----------
def add_librarian():
    lib_id = input("Enter librarian ID: ").strip().upper()
    if lib_id in librarians:
        print("Librarian ID already exists.")
        return
    name = input("Enter librarian name: ").strip()
    if not lib_id or not name:
        print("ID and name cannot be empty.")
        return
    librarians[lib_id] = name
    print("Librarian added successfully.")


def set_active_librarian():
    global active_librarian
    print("\n--- LIBRARIANS ---")
    for lib_id, name in librarians.items():
        marker = "  <-- ACTIVE" if lib_id == active_librarian else ""
        print(lib_id, "|", name, marker)
    lib_id = input("Enter librarian ID to make active: ").strip().upper()
    if lib_id in librarians:
        active_librarian = lib_id
        print("Active librarian set to:", librarians[lib_id])
    else:
        print("Librarian not found.")


# ---------- MENU ----------
def library_menu():
    while True:
        if active_librarian:
            print("\nActive librarian:", librarians[active_librarian])
        else:
            print("\nActive librarian: None")
        print("1. Display books   2. Add book        3. Search book")
        print("4. Issue book      5. Return book     6. Exit")
        print("7. Add librarian   8. Set active librarian")
        print("9. Display issued books")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            display_books()
        elif choice == "2":
            add_book()
        elif choice == "3":
            search_book()
        elif choice == "4":
            issue_book()
        elif choice == "5":
            return_book()
        elif choice == "6":
            print("Thank you for using the Library Management System.")
            break
        elif choice == "7":
            add_librarian()
        elif choice == "8":
            set_active_librarian()
        elif choice == "9":
            display_issued_books()
        else:
            print("Invalid choice. Please enter 1 to 9.")


library_menu()
