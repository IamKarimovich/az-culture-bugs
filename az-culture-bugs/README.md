# When Azerbaijani culture breaks code

The same string and number operations, run under different culture settings in .NET, and with Azerbaijani letters in Python, JavaScript and SQLite.

## Why

Azerbaijani (and Turkish) have two letters `i`: dotted `i/İ` and dotless `ı/I`. In the `az-Latn-AZ` culture the upper case of `i` is `İ`, and the lower case of `I` is `ı`. Code that uses culture-sensitive APIs for technical strings (keys, e-mails, file extensions, protocol names) silently changes behaviour on a machine or server whose culture is Azerbaijani. Decimal numbers change too. In `az-Latn-AZ` the decimal separator is a comma and the group (thousands) separator is a dot, so `double.Parse("3.14")` reads "3 thousand 14" and returns `314`. The parser does not check where group separators stand, so even `double.Parse("1.2.3.4")` returns `1234` instead of throwing. The separators of each culture are saved to `results/number_format.csv`.

The opposite also happens: culture-blind functions in Python, JavaScript and SQLite handle Azerbaijani words incorrectly.

## What is tested

- **.NET** (`dotnet/Program.cs`): 16 operations under `en-US`, `az-Latn-AZ`, `tr-TR` and the invariant culture. The last three are invariant/ordinal controls.
- **Python and SQLite** (`python_tests.py`): `str.upper()`, `lower()`, `casefold()` on Azerbaijani words; SQLite `upper()`, `COLLATE NOCASE`, `LIKE`.
- **JavaScript** (`js_tests.mjs`): `toUpperCase()` vs `toLocaleUpperCase("az")`, `toLowerCase()`, `parseFloat` with a comma.

"Expected" is what a developer would usually assume: English rules for technical strings, Azerbaijani rules for Azerbaijani words.

## Requirements

.NET 8 SDK, Python 3 with matplotlib, Node.js 18+.

## Run

```
pip install -r requirements.txt
```

Windows (cmd): `run.bat` (in PowerShell: `.\run.bat`). Linux/macOS: `./run.sh`.

Results: `results/*.csv`, `results/fig_dotnet_matrix.png`, `results/fig_python_js_sqlite.png`.

## How to avoid the problems

- Technical strings (keys, identifiers, e-mails, headers, file extensions): `StringComparison.Ordinal` / `OrdinalIgnoreCase`, `ToUpperInvariant()` / `ToLowerInvariant()`, `StringComparer.OrdinalIgnoreCase`.
- Numbers in files, JSON, CSV and APIs: always pass `CultureInfo.InvariantCulture`.
- Text shown to Azerbaijani users: use the Azerbaijani culture explicitly (`new CultureInfo("az-Latn-AZ")`, `toLocaleUpperCase("az")`).
- Python and SQLite: do not rely on `lower()`/`upper()` for Azerbaijani search; normalise explicitly or use an ICU-based collation.
- .NET analyzers CA1304, CA1305, CA1307, CA1309, CA1310 and CA1311 warn about culture-sensitive calls.

## Limitations

- Results depend on the ICU version (Windows and Linux ship different versions). The run records the environment in `results/environment_*.txt`.
- "Expected" values reflect typical developer intent, not linguistic correctness: `3,14` is the correct Azerbaijani display of 3.14, but it breaks machine-readable formats.
