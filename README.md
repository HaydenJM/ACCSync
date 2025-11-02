# ACCSync - Assetto Corsa Competizione Livery Sync

A lightweight, easy-to-use livery synchronization tool for small Assetto Corsa Competizione leagues. Automatically downloads and updates custom liveries from a central server without requiring major infrastructure.

## Features

- **Simple One-Click Sync** - Download all league liveries with a single button press
- **Automatic Updates** - Only downloads new or changed liveries, saving bandwidth
- **Hash-Based Verification** - Uses MD5 checksums to detect livery changes
- **Manifest System** - Track multiple drivers and their liveries effortlessly
- **Minimal Infrastructure** - Works with any static file hosting (AWS S3, GitHub Pages, etc.)
- **User-Friendly GUI** - Clean WPF interface for Windows

## Quick Start

### For League Members (Users)

1. **Download** the latest release from [Releases](../../releases)
2. **Extract** `ACCSync.exe` and `config.json` to a folder
3. **Edit** `config.json`:
   ```json
   {
     "aws_url": "https://your-league-server.com",
     "docs_path": "Documents/Assetto Corsa Competizione/Customs/Liveries",
     "local_manifest_path": "Documents/ACCSync/manifest.json"
   }
   ```
   - `aws_url`: Your league's file hosting URL (provided by league admin)
   - `docs_path`: Path relative to your home directory where ACC stores liveries
   - `local_manifest_path`: Where to store sync state

4. **Run** `ACCSync.exe`
5. **Click** the "Sync Liveries" button
6. **Done!** Your liveries are now up to date

### For League Admins

1. **Organize** all liveries as `.zip` files in a folder
   - Name format: `driver_name.zip` (e.g., `john_smith.zip`)

2. **Generate** the manifest using the included tools:
   ```batch
   cd manifest-tools
   rebuild_manifest.bat
   ```
   - Enter your liveries folder path when prompted
   - This creates `manifest.json` with hashes for all liveries

3. **Upload** both the `manifest.json` and all `.zip` files to your hosting:
   ```
   your-server/
   ├── manifest.json
   └── liveries/
       ├── driver1.zip
       ├── driver2.zip
       └── driver3.zip
   ```

4. **Share** the config with your league members:
   ```json
   {
     "aws_url": "https://your-server.com"
   }
   ```

5. **Update** liveries by adding/modifying `.zip` files, regenerating the manifest, and re-uploading

## Configuration

### User Setup

Edit `config.json` to configure paths:

```json
{
  "aws_url": "https://your-aws-bucket.s3.amazonaws.com",
  "docs_path": "Documents/Assetto Corsa Competizione/Customs/Liveries",
  "local_manifest_path": "Documents/ACCSync/manifest.json"
}
```

**Important:** All paths are relative to your Windows user home directory (`C:\Users\YourName\`)

### Admin Manifest Builder

Generate the sync manifest automatically:

**Batch Script (Easiest):**
```batch
cd manifest-tools
rebuild_manifest.bat
```

**Python Direct:**
```bash
python build_manifest.py "C:\path\to\liveries"
```

**With Options:**
```bash
python build_manifest.py "C:\Liveries" -l "My League 2025" -v "2.0.0"
```

Options:
- `-l, --league` - League name (default: "GT3 Championship")
- `-v, --version` - Version number (default: "1.0.0")
- `-o, --output` - Output directory (default: current)
- `--no-compare` - Skip change detection

See [manifest-tools/MANIFEST_BUILDER.md](manifest-tools/MANIFEST_BUILDER.md) for full documentation.

## Hosting Your Liveries

ACCSync works with any static file host:

**AWS S3:**
```bash
aws s3 cp manifest.json s3://your-bucket/manifest.json --acl public-read
aws s3 cp liveries/ s3://your-bucket/liveries/ --recursive --acl public-read
```

**Other Options:**
- GitHub Releases
- Google Drive (public sharing)
- Dropbox (public links)
- Any HTTP server

## Building from Source

### Prerequisites
- [.NET 8.0 SDK](https://dotnet.microsoft.com/download/dotnet/8.0)
- Windows 10 or later

### Build

**Quick Build:**
```batch
build.bat
# Choose option 3 for standalone executable
```

**Manual:**
```bash
# Development
dotnet build

# Release
dotnet build -c Release

# Standalone executable
dotnet publish -c Release -o output
```

## Manifest Format

```json
{
  "league": "GT3 Championship",
  "version": "1.0.0",
  "updated": "2025-11-02T15:23:45Z",
  "liveries": [
    {
      "driver": "john_doe",
      "file": "john_doe.zip",
      "hash": "b1946ac92492d2347c6235b4d2611184",
      "size_mb": 15.5
    }
  ]
}
```

## Troubleshooting

**"Failed to fetch remote manifest"**
- Verify `aws_url` in config.json
- Check manifest is accessible at `{aws_url}/manifest.json`
- Test internet connection

**Liveries not appearing in-game**
- Confirm `docs_path` points to ACC liveries folder
- Verify .zip file structure is correct
- Restart ACC after syncing

**Permission errors**
- Run as Administrator
- Check folder permissions

## FAQ

**Q: Do I need AWS?**
A: No! The setting is named "aws_url" but works with any file hosting.

**Q: Can I use this for multiple leagues?**
A: Yes! Use separate config files or run multiple instances.

**Q: How much bandwidth does this use?**
A: Only new/changed liveries download. Typical livery is 10-20MB.

**Q: Does this work on Mac/Linux?**
A: Currently Windows-only (WPF). Could be ported to .NET MAUI for cross-platform.

## License

GNU Affero General Public License v3.0 - see [LICENSE](LICENSE)

## Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)
