// Runs the same string and number operations under different cultures and checks
// whether the result is what a developer would expect.
// Writes results/dotnet.csv (run from the project root: dotnet run --project dotnet).

using System.Globalization;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.RegularExpressions;

Console.OutputEncoding = Encoding.UTF8;

var cultures = new[] { "en-US", "az-Latn-AZ", "tr-TR", "" }; // "" = invariant

// (id, what real code does, function, expected result)
var tests = new (string Id, string Code, Func<string> Run, string Expected)[]
{
    ("upper_ascii", "\"file\".ToUpper()", () => "file".ToUpper(), "FILE"),
    ("lower_ascii", "\"FILE\".ToLower()", () => "FILE".ToLower(), "file"),
    ("email_lower", "\"INFO@SITE.AZ\".ToLower()", () => "INFO@SITE.AZ".ToLower(), "info@site.az"),
    ("equals_ignorecase", "string.Equals(\"file\", \"FILE\", CurrentCultureIgnoreCase)",
        () => string.Equals("file", "FILE", StringComparison.CurrentCultureIgnoreCase).ToString(), "True"),
    ("endswith_ignorecase", "\"photo.GIF\".EndsWith(\".gif\", CurrentCultureIgnoreCase)",
        () => "photo.GIF".EndsWith(".gif", StringComparison.CurrentCultureIgnoreCase).ToString(), "True"),
    ("dictionary_lookup", "Dictionary(CurrentCultureIgnoreCase)[\"ID\"] with key \"id\"", () =>
    {
        var d = new Dictionary<string, int>(StringComparer.CurrentCultureIgnoreCase) { ["id"] = 1 };
        return d.ContainsKey("ID").ToString();
    }, "True"),
    ("regex_ignorecase", "Regex.IsMatch(\"FILE\", \"file\", IgnoreCase)",
        () => Regex.IsMatch("FILE", "file", RegexOptions.IgnoreCase).ToString(), "True"),
    ("double_parse", "double.Parse(\"3.14\")", () => double.Parse("3.14").ToString(CultureInfo.InvariantCulture), "3.14"),
    ("double_tostring", "3.14.ToString()", () => 3.14.ToString(), "3.14"),
    ("az_upper", "\"ilham\".ToUpper()  (Azerbaijani word)", () => "ilham".ToUpper(), "İLHAM"),
    ("az_lower", "\"İSTİQLAL\".ToLower()  (Azerbaijani word)", () => "İSTİQLAL".ToLower(), "istiqlal"),
    // Controls: the invariant / ordinal APIs should pass everywhere.
    ("control_upper_invariant", "\"file\".ToUpperInvariant()", () => "file".ToUpperInvariant(), "FILE"),
    ("control_equals_ordinal", "string.Equals(\"file\", \"FILE\", OrdinalIgnoreCase)",
        () => string.Equals("file", "FILE", StringComparison.OrdinalIgnoreCase).ToString(), "True"),
    ("control_parse_invariant", "double.Parse(\"3.14\", CultureInfo.InvariantCulture)",
        () => double.Parse("3.14", CultureInfo.InvariantCulture).ToString(CultureInfo.InvariantCulture), "3.14"),
};

var rows = new List<string> { "platform,culture,test,code,expected,actual,pass" };
Console.WriteLine($"{RuntimeInformation.OSDescription} | .NET {Environment.Version}\n");

foreach (var name in cultures)
{
    var culture = name == "" ? CultureInfo.InvariantCulture : new CultureInfo(name);
    CultureInfo.CurrentCulture = culture;
    CultureInfo.CurrentUICulture = culture;
    var label = name == "" ? "invariant" : name;
    Console.WriteLine($"== {label} ==");

    foreach (var t in tests)
    {
        string actual;
        try { actual = t.Run(); }
        catch (Exception ex) { actual = ex.GetType().Name; }
        var pass = actual == t.Expected;
        Console.WriteLine($"  {(pass ? "OK  " : "FAIL")} {t.Code,-62} -> {actual}");
        rows.Add(string.Join(",", ".NET", label, t.Id, Q(t.Code), Q(t.Expected), Q(actual), pass));
    }
    Console.WriteLine();
}

Directory.CreateDirectory("results");
File.WriteAllLines("results/dotnet.csv", rows, new UTF8Encoding(false));
File.WriteAllText("results/environment_dotnet.txt",
    $"OS: {RuntimeInformation.OSDescription}\n.NET: {Environment.Version}\n", new UTF8Encoding(false));
Console.WriteLine("Saved results/dotnet.csv");

static string Q(string s) => "\"" + s.Replace("\"", "\"\"") + "\"";
