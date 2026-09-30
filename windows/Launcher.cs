// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Long Ngo.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Net;
using System.Reflection;
using System.Security.Cryptography;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using System.Web.Script.Serialization;
using System.Windows.Forms;

[assembly: System.Runtime.Versioning.TargetFramework(".NETFramework,Version=v4.8")]
[assembly: AssemblyVersion("0.1.2.0")]

static class Launcher {
    const string Version = "0.1.2";
    static readonly string Store;
    static readonly string Runtime;
    static Launcher() {
        // Set before the first Path call: .NET caches these switches.
        AppContext.SetSwitch("Switch.System.IO.UseLegacyPathHandling", false);
        AppContext.SetSwitch("Switch.System.IO.BlockLongPaths", false);
        Store = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "VFMGIS");
        Runtime = Path.Combine(Store, "r2");
    }
    static Dictionary<string,string> Manifest;
    static FileStream Lock;

    static Stream Resource(string name) {
        var s = Assembly.GetExecutingAssembly().GetManifestResourceStream(name);
        if (s == null) throw new InvalidOperationException("Thiếu thành phần: " + name);
        return s;
    }
    static string TextResource(string name) {
        using (var r = new StreamReader(Resource(name), Encoding.UTF8)) return r.ReadToEnd();
    }
    static string Hash(string path) {
        using (var h = SHA256.Create()) using (var s = File.OpenRead(path))
            return BitConverter.ToString(h.ComputeHash(s)).Replace("-", "").ToLowerInvariant();
    }
    static void VerifyArchive(string path) {
        if (!String.Equals(Hash(path), Manifest["sha256"], StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("Bộ chạy tải về không khớp SHA-256. Chưa chạy tệp này; hãy thử tải lại.");
    }
    static string LongPath(string path) {
        string full = Path.GetFullPath(path);
        if (full.StartsWith(@"\\?\", StringComparison.Ordinal)) return full;
        return full.StartsWith(@"\\", StringComparison.Ordinal) ? @"\\?\UNC\" + full.Substring(2) : @"\\?\" + full;
    }
    static void ExtractRuntime(string archivePath, string destination) {
        string root = LongPath(destination).TrimEnd(Path.DirectorySeparatorChar);
        Directory.CreateDirectory(root);
        using (var archive = ZipFile.OpenRead(archivePath)) {
            foreach (var entry in archive.Entries) {
                const string wrapper = "gvSIG-desktop-2.6.0-3335-final-win-x86_64/";
                string name = entry.FullName.Replace('\\', '/');
                if (!name.StartsWith(wrapper, StringComparison.Ordinal))
                    throw new InvalidDataException("Cấu trúc ZIP gvSIG không đúng phiên bản đã kiểm tra.");
                name = name.Substring(wrapper.Length);
                if (name.Length == 0) continue;
                if (name.Split('/').Any(p => p == ".." || p.Contains(":")) || name.StartsWith("/"))
                    throw new InvalidDataException("Đường dẫn ZIP không hợp lệ.");
                string path = Path.GetFullPath(Path.Combine(root, name.Replace('/', Path.DirectorySeparatorChar)));
                if (!path.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
                    throw new InvalidDataException("Đường dẫn ZIP vượt thư mục bộ chạy.");
                if (String.IsNullOrEmpty(entry.Name)) { Directory.CreateDirectory(path); continue; }
                Directory.CreateDirectory(Path.GetDirectoryName(path));
                // Upstream ZIP contains case-colliding translations; match 7-Zip's last-entry-wins behavior.
                entry.ExtractToFile(path, true);
            }
        }
    }
    static string FindRuntimeRoot(string folder) {
        var matches = Directory.GetDirectories(LongPath(folder), "addons", SearchOption.AllDirectories).Where(p => p.Contains("org.gvsig.scripting.app.mainplugin") && new DirectoryInfo(p).Parent.Name == "scripts").ToArray();
        if (matches.Length != 1) throw new IOException("Không xác định được thư mục Scripting của gvSIG.");
        return matches[0];
    }
    static void InstallAddon(string folder) {
        string plugin = FindRuntimeRoot(folder);
        string destination = Path.Combine(plugin, "VFMGIS");
        Directory.CreateDirectory(destination);
        using (var archive = new ZipArchive(Resource("addon.zip"), ZipArchiveMode.Read)) {
            foreach (var entry in archive.Entries) {
                if (String.IsNullOrEmpty(entry.Name)) continue;
                string path = Path.GetFullPath(Path.Combine(destination, entry.FullName.Replace('/', Path.DirectorySeparatorChar)));
                if (!path.StartsWith(destination + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
                    throw new InvalidDataException("Đường dẫn gói không hợp lệ.");
                Directory.CreateDirectory(Path.GetDirectoryName(path));
                entry.ExtractToFile(path, true);
            }
        }
    }
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode)]
    static extern uint GetShortPathName(string path, StringBuilder buffer, uint length);
    static string ShortPath(string path) {
        var buffer = new StringBuilder(32768);
        uint count = GetShortPathName(path, buffer, (uint)buffer.Capacity);
        return count > 0 && count < buffer.Capacity ? buffer.ToString() : path;
    }
    static string FindLauncher(string folder) {
        var names = new[] { "gvsig.exe", "gvsig-desktop.exe", "gvsig.bat", "gvsig-desktop.bat" };
        var files = Directory.GetFiles(LongPath(folder), "*", SearchOption.AllDirectories)
            .Where(p => names.Contains(Path.GetFileName(p).ToLowerInvariant()))
            .OrderBy(p => p.Split(Path.DirectorySeparatorChar).Length)
            .ThenBy(p => Path.GetExtension(p).Equals(".exe", StringComparison.OrdinalIgnoreCase) ? 0 : 1).ToArray();
        if (files.Length == 0) throw new FileNotFoundException("Không tìm thấy chương trình khởi động gvSIG.");
        string file = files[0];
        return file.StartsWith(@"\\?\", StringComparison.Ordinal) ? file.Substring(4) : file;
    }
    static void StartGIS(string folder, string report) {
        string launch = ShortPath(FindLauncher(folder));
        bool bat = Path.GetExtension(launch).Equals(".bat", StringComparison.OrdinalIgnoreCase);
        var info = new ProcessStartInfo {
            FileName = bat ? Environment.GetEnvironmentVariable("COMSPEC") : launch,
            Arguments = bat ? "/d /c \"\"" + launch + "\"\"" : "",
            WorkingDirectory = Path.GetDirectoryName(launch),
            UseShellExecute = false,
            CreateNoWindow = true
        };
        info.EnvironmentVariables["VFMGIS_AUTOSTART"] = "1";
        if (report != null) info.EnvironmentVariables["VFMGIS_TEST_REPORT"] = report;
        if (report != null) File.WriteAllText(report + ".launch", "Launcher: " + launch + "\nWorking directory: " + info.WorkingDirectory);
        Process.Start(info);
    }
    static void VerifySelf() {
        if (Manifest["sha256"].Length != 64 || !(Manifest["url"].StartsWith("https://downloads.gvsig.org/") || Manifest["url"].StartsWith("http://downloads.gvsig.org/")))
            throw new InvalidDataException("Thông tin bộ chạy không hợp lệ.");
        using (var archive = new ZipArchive(Resource("addon.zip"), ZipArchiveMode.Read)) {
            foreach (var name in new[] { "autorun.py", "autorun.inf", "ui.py", "engine.py", "core.py", "sample.py", "smoke.py", "runtime_check.py" })
                if (archive.GetEntry(name) == null) throw new InvalidDataException("Thiếu " + name);
        }
    }
    [STAThread]
    static int Main(string[] args) {
        try {
            AppContext.SetSwitch("Switch.System.IO.UseLegacyPathHandling", false);
            AppContext.SetSwitch("Switch.System.IO.BlockLongPaths", false);
            ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
            Manifest = new JavaScriptSerializer().Deserialize<Dictionary<string,string>>(TextResource("runtime.json"));
            VerifySelf();
            if (args.Length > 0 && args[0] == "--verify") return 0;
            if (args.Length > 0 && args[0] == "--verify-long-paths") {
                string temp = Path.Combine(Path.GetTempPath(), "vfmgis-path-" + Guid.NewGuid().ToString("N"));
                try {
                    string nested = temp;
                    while (nested.Length < 300) nested = Path.Combine(nested, "long-path-regression-test");
                    nested = LongPath(nested);
                    Directory.CreateDirectory(nested);
                    string file = Path.GetFullPath(Path.Combine(nested, "test.txt"));
                    File.WriteAllText(file, "VFMGIS");
                    if (File.ReadAllText(file) != "VFMGIS") throw new IOException("Long path regression failed");
                } finally { if (Directory.Exists(temp)) Directory.Delete(LongPath(temp), true); }
                return 0;
            }
            if (args.Length == 3 && args[0] == "--test-archive") {
                string zip = Path.GetFullPath(args[1]);
                string testFolder = Path.Combine(Path.GetDirectoryName(zip), "runtime dotnet test", "r2");
                VerifyArchive(zip);
                ExtractRuntime(zip, testFolder);
                InstallAddon(testFolder);
                StartGIS(testFolder, Path.GetFullPath(args[2]));
                return 0;
            }
            if (args.Length == 3 && args[0] == "--test-runtime") {
                InstallAddon(Path.GetFullPath(args[1]));
                StartGIS(Path.GetFullPath(args[1]), Path.GetFullPath(args[2]));
                return 0;
            }
            if (!Environment.Is64BitOperatingSystem) throw new PlatformNotSupportedException("VFMGIS cần Windows 64-bit.");
            Directory.CreateDirectory(Store);
            try { Lock = new FileStream(Path.Combine(Store,"setup.lock"), FileMode.OpenOrCreate, FileAccess.ReadWrite, FileShare.None); }
            catch (IOException) { throw new IOException("Một cửa sổ khởi động VFMGIS khác đang chạy. Hãy chờ cửa sổ đó hoàn tất."); }
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new SetupWindow());
            return 0;
        } catch (Exception e) {
            if (args.Length > 0) { File.WriteAllText(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "launcher-test-error.txt"), e.ToString()); if (args.Length == 3) File.WriteAllText(args[2], e.ToString()); Console.Error.WriteLine(e); return 1; }
            MessageBox.Show(e.Message, "VFMGIS · Không thể khởi động", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        } finally { if (Lock != null) Lock.Dispose(); }
    }
    sealed class SetupWindow : Form {
        readonly Label status = new Label();
        readonly ProgressBar progress = new ProgressBar();
        readonly Button retry = new Button();
        bool busy;
        public SetupWindow() {
            Text = "VFMGIS 0.1.2 · Khởi động GIS tiếng Việt";
            Size = new Size(570, 275); StartPosition = FormStartPosition.CenterScreen;
            FormBorderStyle = FormBorderStyle.FixedDialog; MaximizeBox = false;
            Font = new Font("Segoe UI", 10); BackColor = Color.White;
            var title = new Label { Text="VFMGIS", Font=new Font("Segoe UI",24,FontStyle.Bold), ForeColor=Color.FromArgb(24,60,83), AutoSize=true, Location=new Point(24,18) };
            status.SetBounds(26,78,510,55); status.Text = "Chuẩn bị môi trường GIS…";
            progress.SetBounds(26,145,505,20);
            retry.Text = "Thử lại"; retry.SetBounds(420,185,110,30); retry.Visible=false;
            retry.Click += async (sender,e) => await RunSetup();
            Controls.AddRange(new Control[]{title,status,progress,retry});
            Shown += async (sender,e) => await RunSetup();
            FormClosing += (sender,e) => { if (busy) { e.Cancel=true; status.Text="Đang tải hoặc giải nén. Vui lòng chờ hoàn tất trước khi đóng."; } };
        }
        async Task RunSetup() {
            busy=true; retry.Visible=false;
            try {
                string ready = Path.Combine(Runtime, ".vfmgis-ready");
                if (!File.Exists(ready) || File.ReadAllText(ready).Trim() != Manifest["sha256"]) {
                    string download = Path.Combine(Store,"runtime.zip.part");
                    status.Text = "Lần đầu: tải gvSIG và Java (~503 MB).\nCần Internet; không cần quyền quản trị.";
                    progress.Style=ProgressBarStyle.Continuous; progress.Value=0;
                    bool cached = File.Exists(download) && await Task.Run(() => Hash(download) == Manifest["sha256"]);
                    if (!cached) using (var client=new WebClient()) {
                        client.Headers[HttpRequestHeader.UserAgent]="VFMGIS/"+Version;
                        client.DownloadProgressChanged += (sender,e) => { progress.Value=Math.Max(0,Math.Min(100,e.ProgressPercentage)); status.Text=String.Format("Đang tải bộ chạy: {0:N0} / {1:N0} MB\nLần sau không cần tải lại.",e.BytesReceived/1048576.0,e.TotalBytesToReceive/1048576.0); };
                        await client.DownloadFileTaskAsync(new Uri(Manifest["url"]), download);
                    }
                    status.Text="Kiểm tra SHA-256 và giải nén bộ chạy…"; progress.Style=ProgressBarStyle.Marquee;
                    await Task.Run(() => {
                        VerifyArchive(download);
                        string staging=Runtime+".tmp";
                        if (Directory.Exists(staging)) Directory.Delete(LongPath(staging),true);
                        Directory.CreateDirectory(staging);
                        ExtractRuntime(download,staging);
                        FindRuntimeRoot(staging); FindLauncher(staging);
                        if (Directory.Exists(Runtime)) throw new IOException("Thư mục bộ chạy cũ chưa hoàn tất: "+Runtime+". Đổi tên thư mục đó rồi thử lại.");
                        File.WriteAllText(Path.Combine(staging,".vfmgis-ready"),Manifest["sha256"]);
                        Directory.Move(staging,Runtime); File.Delete(download);
                    });
                }
                status.Text="Đang mở không gian VFMGIS…"; progress.Style=ProgressBarStyle.Marquee;
                await Task.Run(() => InstallAddon(Runtime));
                StartGIS(Runtime,null);
                busy=false; Close();
            } catch (Exception e) {
                File.WriteAllText(Path.Combine(Store,"launcher-error.txt"),e.ToString());
                status.Text = e is PathTooLongException ? "Đường dẫn giải nén quá dài. Xem chi tiết lỗi bên dưới." : "Chưa khởi động được. Xem thông báo chi tiết bên dưới.";
                progress.Style=ProgressBarStyle.Continuous; progress.Value=0;
                busy=false; retry.Visible=true;
                MessageBox.Show(this,e.Message+"\n\nChi tiết: "+Path.Combine(Store,"launcher-error.txt"),"VFMGIS",MessageBoxButtons.OK,MessageBoxIcon.Error);
            }
        }
    }
}
