# Manifest Builder - Quick Guide

The `build_manifest.py` script automatically scans your liveries folder and generates a `manifest.json` file. Run it whenever you add, remove, or update liveries.

## Quick Start

### Option 1: Batch Script (Easiest)

Double-click `rebuild_manifest.bat` and enter the path to your liveries folder:

```
C:\Users\YourName\Documents\AccLiveries
```

The script will:
- Scan all `.zip` files
- Calculate MD5 hashes
- Generate `manifest.json`
- Show what changed (added/removed/updated)

### Option 2: PowerShell

```powershell
.\rebuild_manifest.ps1 -LiveriesFolder "C:\path\to\liveries"
```

### Option 3: Python Direct

```bash
python build_manifest.py "C:\path\to\liveries"
```

## Usage Examples

### Basic usage
```bash
python build_manifest.py "C:\Liveries"
```

### Custom league name and version
```bash
python build_manifest.py "C:\Liveries" -l "My League 2025" -v "2.0.0"
```

### Save to specific output folder
```bash
python build_manifest.py "C:\Liveries" -o "C:\Output\"
```

### Combine options
```bash
python build_manifest.py "C:\Liveries" -l "GT2 Series" -v "1.5.0" -o "C:\AWS\"
```

### Skip comparison with existing manifest
```bash
python build_manifest.py "C:\Liveries" --no-compare
```

## Command Line Arguments

```
Positional:
  liveries_folder           Path to folder containing .zip livery files

Optional:
  -o, --output              Output directory for manifest.json (default: current dir)
  -l, --league              League name for manifest (default: "GT3 Championship")
  -v, --version             Manifest version (default: "1.0.0")
  --no-compare              Skip comparison with existing manifest
  -h, --help               Show help message
```

## What Gets Generated

The script creates a `manifest.json` with this structure:

```json
{
  "league": "GT3 Championship",
  "version": "1.0.0",
  "updated": "2025-10-30T15:23:45.123456Z",
  "liveries": [
    {
      "driver": "John_Doe",
      "file": "john_doe.zip",
      "hash": "b1946ac92492d2347c6235b4d2611184",
      "size_mb": 15.5
    },
    {
      "driver": "Jane_Smith",
      "file": "jane_smith.zip",
      "hash": "4a7d1ed414474e4033ac29ccb8653d9b",
      "size_mb": 12.3
    }
  ]
}
```

## Change Detection

The script automatically compares with the existing `manifest.json` and shows:

```
==================================================
MANIFEST CHANGES
==================================================

Added (2):
  + New_Driver_1
  + New_Driver_2

Removed (1):
  - Old_Driver

Updated (1):
  ~ Updated_Driver

==================================================
```

## Workflow

1. **Add new livery**: Copy `john_smith.zip` to your liveries folder
2. **Run builder**: Execute `rebuild_manifest.bat` (or your preferred method)
3. **Upload**: Copy the new `manifest.json` to your AWS bucket
4. **Sync**: Users run ACC Livery Sync to download the new livery

Or in one command:
```bash
python build_manifest.py "C:\Liveries" && aws s3 cp manifest.json s3://mybucket/manifest.json
```

## Tips

- **File naming**: Use underscores for spaces in driver names (`John_Smith` not `John Smith`)
- **Organized folder**: Keep all livery .zip files in a single folder
- **Batch updates**: Add multiple liveries, then run the builder once
- **Version tracking**: Update the version number when making significant changes
- **League name**: Change if managing multiple leagues
- **Automated**: Can be scheduled with Windows Task Scheduler for periodic updates

## File Format Requirements

- Must be `.zip` files
- Filename (without .zip) becomes the `driver` name
- Can contain subdirectories inside the zip
- ACC will extract to the Liveries folder automatically

## Troubleshooting

**"No .zip files found"**
- Check the folder path is correct
- Ensure files have `.zip` extension (lowercase)

**"Permission denied" error**
- Run Command Prompt or PowerShell as Administrator
- Check folder permissions

**Different hash for same file**
- .zip files can be recreated differently even with same contents
- The hash is used to detect actual changes

## Integration with AWS

After building the manifest, upload it to S3:

```bash
# Using AWS CLI
aws s3 cp manifest.json s3://your-bucket/manifest.json
```

Users will then pull the updated manifest when they click "Sync Liveries" in the app.
