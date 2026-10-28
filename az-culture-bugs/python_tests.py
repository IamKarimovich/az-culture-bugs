"""Python and SQLite: the same kind of checks. Writes results/python.csv

Python's str.upper()/lower() ignore the system locale and use Unicode rules
that are the same for every language. SQLite's built-in upper()/lower() only
change ASCII letters.
"""
import csv
import locale
import platform
import sqlite3
import sys
from pathlib import Path

db = sqlite3.connect(":memory:")
sql = lambda q, *a: db.execute(q, a).fetchone()[0]

# (platform, test id, code, function, expected)
TESTS = [
    ("Python", "upper_ascii", '"file".upper()', lambda: "file".upper(), "FILE"),
    ("Python", "lower_ascii", '"FILE".lower()', lambda: "FILE".lower(), "file"),
    ("Python", "az_upper", '"ilham".upper()', lambda: "ilham".upper(), "İLHAM"),
    ("Python", "az_lower", '"İSTİQLAL".lower()', lambda: "İSTİQLAL".lower(), "istiqlal"),
    ("Python", "az_lower_length", 'len("İ".lower())', lambda: str(len("İ".lower())), "1"),
    ("Python", "az_casefold_equal", '"İLHAM".casefold() == "ilham".casefold()',
     lambda: str("İLHAM".casefold() == "ilham".casefold()), "True"),
    ("Python", "dotless_upper", '"ı".upper()', lambda: "ı".upper(), "I"),
    ("Python", "schwa_upper", '"Azərbaycan".upper()', lambda: "Azərbaycan".upper(), "AZƏRBAYCAN"),
    ("SQLite", "sqlite_upper_ascii", "SELECT upper('file')", lambda: sql("SELECT upper(?)", "file"), "FILE"),
    ("SQLite", "sqlite_upper_az", "SELECT upper('şəhər')", lambda: sql("SELECT upper(?)", "şəhər"), "ŞƏHƏR"),
    ("SQLite", "sqlite_nocase_az", "SELECT 'ÇAY' = 'çay' COLLATE NOCASE",
     lambda: str(bool(sql("SELECT ? = ? COLLATE NOCASE", "ÇAY", "çay"))), "True"),
    ("SQLite", "sqlite_like_az", "SELECT 'Gəncə' LIKE 'GƏNCƏ'",
     lambda: str(bool(sql("SELECT ? LIKE ?", "Gəncə", "GƏNCƏ"))), "True"),
]


def main():
    Path("results").mkdir(exist_ok=True)
    rows = []
    print(f"Python {platform.python_version()} | SQLite {sqlite3.sqlite_version} | {platform.platform()}\n")
    for plat, tid, code, fn, expected in TESTS:
        try:
            actual = fn()
        except Exception as ex:  # keep going, record the error
            actual = type(ex).__name__
        ok = actual == expected
        print(f"  {'OK  ' if ok else 'FAIL'} {code:<48} -> {actual!r}")
        rows.append([plat, "(locale-independent)", tid, code, expected, actual, ok])

    with open("results/python.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["platform", "culture", "test", "code", "expected", "actual", "pass"])
        w.writerows(rows)
    Path("results/environment_python.txt").write_text(
        f"Python: {platform.python_version()}\nSQLite: {sqlite3.sqlite_version}\nOS: {platform.platform()}\n"
        f"Locale: {locale.getlocale()}\n", encoding="utf-8")
    print("\nSaved results/python.csv")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
