using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text.Json;
using System.Threading.Tasks;

namespace ACCSync
{
    public class Config
    {
        private Dictionary<string, JsonElement> _config;
        private readonly string _configPath;

        public Config()
        {
            _configPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "config.json");
            _config = LoadConfig();
        }

        private Dictionary<string, JsonElement> LoadConfig()
        {
            var defaults = new Dictionary<string, JsonElement>();

            try
            {
                if (File.Exists(_configPath))
                {
                    string json = File.ReadAllText(_configPath);
                    using (JsonDocument doc = JsonDocument.Parse(json))
                    {
                        foreach (var property in doc.RootElement.EnumerateObject())
                        {
                            defaults[property.Name] = property.Value.Clone();
                        }
                    }
                    return defaults;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error loading config: {ex.Message}");
            }

            // Return default configuration if file doesn't exist
            var defaultJson = """
            {
              "aws_url": "https://your-aws-bucket.s3.amazonaws.com",
              "docs_path": "Assetto Corsa Competizione/Customs/Liveries",
              "local_manifest_path": "ACCSync/manifest.json"
            }
            """;

            using (JsonDocument doc = JsonDocument.Parse(defaultJson))
            {
                foreach (var property in doc.RootElement.EnumerateObject())
                {
                    defaults[property.Name] = property.Value.Clone();
                }
            }

            return defaults;
        }

        public string Get(string key)
        {
            if (_config.TryGetValue(key, out var value))
            {
                return value.GetString();
            }
            return null;
        }
    }

    public class LiverySync
    {
        private readonly string _awsUrl;
        private readonly string _manifestUrl;
        private readonly string _liveriesFolder;

        public string DocsPath { get; private set; }
        public string LocalManifestPath { get; private set; }

        private static readonly HttpClient HttpClient = new HttpClient();

        public LiverySync()
        {
            // Load configuration
            var config = new Config();
            _awsUrl = config.Get("aws_url") ?? "https://your-aws-bucket.s3.amazonaws.com";
            _manifestUrl = $"{_awsUrl}/manifest.json";
            _liveriesFolder = $"{_awsUrl}/liveries";

            // Set up paths
            string documentsPath = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);
            string docsPathStr = config.Get("docs_path") ?? "Assetto Corsa Competizione/Customs/Liveries";
            string manifestPathStr = config.Get("local_manifest_path") ?? "ACCSync/manifest.json";

            DocsPath = Path.Combine(documentsPath, docsPathStr);
            LocalManifestPath = Path.Combine(documentsPath, manifestPathStr);

            // Ensure directories exist
            Directory.CreateDirectory(DocsPath);
            Directory.CreateDirectory(Path.GetDirectoryName(LocalManifestPath));
        }

        public async Task<(bool Success, string Message)> SyncLiveries(Action<string, int> progressCallback = null)
        {
            try
            {
                progressCallback?.Invoke("Fetching manifest...", 0);

                var remoteManifest = await FetchRemoteManifest();
                if (remoteManifest == null)
                    return (false, "Failed to fetch remote manifest");

                var localManifest = LoadLocalManifest();
                var liveries = remoteManifest.RootElement.GetProperty("liveries").EnumerateArray().ToList();

                // Find liveries to download
                var liveriesToDownload = new List<JsonElement>();

                for (int i = 0; i < liveries.Count; i++)
                {
                    var livery = liveries[i];
                    progressCallback?.Invoke($"Checking liveries... ({i + 1}/{liveries.Count})",
                        (int)((i / (double)liveries.Count) * 50));

                    string driverName = livery.GetProperty("driver").GetString();
                    string liveryHash = livery.GetProperty("hash").GetString();

                    if (!localManifest.ContainsKey(driverName) || localManifest[driverName] != liveryHash)
                    {
                        liveriesToDownload.Add(livery);
                    }
                }

                if (liveriesToDownload.Count == 0)
                {
                    progressCallback?.Invoke("Already up to date!", 100);
                    return (true, "No new liveries to download");
                }

                // Download and extract liveries
                for (int i = 0; i < liveriesToDownload.Count; i++)
                {
                    var livery = liveriesToDownload[i];
                    string driverName = livery.GetProperty("driver").GetString();
                    string fileName = livery.GetProperty("file").GetString();
                    string liveryUrl = $"{_liveriesFolder}/{fileName}";

                    progressCallback?.Invoke($"Downloading {driverName}...",
                        50 + (int)((i / (double)liveriesToDownload.Count) * 50));

                    string zipPath = Path.Combine(DocsPath, fileName);

                    if (!await DownloadFile(liveryUrl, zipPath, driverName))
                        continue;

                    // Extract zip
                    try
                    {
                        ZipFile.ExtractToDirectory(zipPath, DocsPath, overwriteFiles: true);
                        File.Delete(zipPath);
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Error extracting {driverName}: {ex.Message}");
                    }

                    // Update local manifest
                    localManifest[driverName] = livery.GetProperty("hash").GetString();
                }

                // Save updated manifest
                SaveLocalManifest(localManifest);

                progressCallback?.Invoke("Sync complete!", 100);
                return (true, $"Downloaded {liveriesToDownload.Count} liveries");
            }
            catch (Exception ex)
            {
                return (false, $"Sync error: {ex.Message}");
            }
        }

        private async Task<bool> DownloadFile(string url, string destination, string description = null)
        {
            try
            {
                using (var response = await HttpClient.GetAsync(url, HttpCompletionOption.ResponseHeadersRead))
                {
                    response.EnsureSuccessStatusCode();

                    using (var contentStream = await response.Content.ReadAsStreamAsync())
                    using (var fileStream = new FileStream(destination, FileMode.Create, FileAccess.Write, FileShare.None))
                    {
                        await contentStream.CopyToAsync(fileStream);
                    }
                }
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error downloading {url}: {ex.Message}");
                return false;
            }
        }

        private async Task<JsonDocument> FetchRemoteManifest()
        {
            try
            {
                using (var response = await HttpClient.GetAsync(_manifestUrl))
                {
                    response.EnsureSuccessStatusCode();
                    var content = await response.Content.ReadAsStringAsync();
                    return JsonDocument.Parse(content);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error fetching remote manifest: {ex.Message}");
                return null;
            }
        }

        private Dictionary<string, string> LoadLocalManifest()
        {
            if (!File.Exists(LocalManifestPath))
                return new Dictionary<string, string>();

            try
            {
                string json = File.ReadAllText(LocalManifestPath);
                var options = new JsonSerializerOptions();
                var data = JsonSerializer.Deserialize<Dictionary<string, string>>(json, options);
                return data ?? new Dictionary<string, string>();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error loading local manifest: {ex.Message}");
                return new Dictionary<string, string>();
            }
        }

        private void SaveLocalManifest(Dictionary<string, string> manifest)
        {
            try
            {
                var options = new JsonSerializerOptions { WriteIndented = true };
                string json = JsonSerializer.Serialize(manifest, options);
                File.WriteAllText(LocalManifestPath, json);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error saving manifest: {ex.Message}");
            }
        }
    }
}
