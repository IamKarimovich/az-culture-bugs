// JavaScript (Node.js): default vs locale-aware string functions. Writes results/javascript.csv
import fs from "fs";
import os from "os";

const tests = [
  ["upper_ascii", `"file".toUpperCase()`, () => "file".toUpperCase(), "FILE"],
  ["az_upper", `"ilham".toUpperCase()`, () => "ilham".toUpperCase(), "İLHAM"],
  ["az_upper_locale", `"ilham".toLocaleUpperCase("az")`, () => "ilham".toLocaleUpperCase("az"), "İLHAM"],
  ["ascii_upper_az_locale", `"file".toLocaleUpperCase("az")`, () => "file".toLocaleUpperCase("az"), "FILE"],
  ["az_lower", `"İSTİQLAL".toLowerCase()`, () => "İSTİQLAL".toLowerCase(), "istiqlal"],
  ["az_lower_length", `"İ".toLowerCase().length`, () => String("İ".toLowerCase().length), "1"],
  ["az_lower_locale", `"İSTİQLAL".toLocaleLowerCase("az")`, () => "İSTİQLAL".toLocaleLowerCase("az"), "istiqlal"],
  ["collator_az", `Intl.Collator("az", {sensitivity:"base"}).compare("file","FILE")`,
    () => String(new Intl.Collator("az", { sensitivity: "base" }).compare("file", "FILE")), "0"],
  ["number_az", `(3.14).toLocaleString("az")`, () => (3.14).toLocaleString("az"), "3.14"],
  ["parse_az_number", `parseFloat("3,14")`, () => String(parseFloat("3,14")), "3.14"],
];

const rows = [["platform", "culture", "test", "code", "expected", "actual", "pass"]];
console.log(`Node ${process.version} | ICU ${process.versions.icu} | ${os.type()} ${os.release()}\n`);
for (const [id, code, fn, expected] of tests) {
  let actual;
  try { actual = fn(); } catch (e) { actual = e.name; }
  const ok = actual === expected;
  console.log(`  ${ok ? "OK  " : "FAIL"} ${code.padEnd(70)} -> ${JSON.stringify(actual)}`);
  rows.push(["JavaScript", "(see code)", id, code, expected, actual, ok ? "True" : "False"]);
}

const q = v => `"${String(v).replace(/"/g, '""')}"`;
fs.mkdirSync("results", { recursive: true });
fs.writeFileSync("results/javascript.csv", rows.map(r => r.map(q).join(",")).join("\n") + "\n");
fs.writeFileSync("results/environment_js.txt", `Node: ${process.version}\nICU: ${process.versions.icu}\nOS: ${os.type()} ${os.release()}\n`);
console.log("\nSaved results/javascript.csv");
