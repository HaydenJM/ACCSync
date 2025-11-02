import json
import hashlib
import os
from pathlib import Path
from datetime import datetime
import argparse
import sys


class ManifestBuilder:
    def __init__(self, liveries_folder, manifest_output=None):
        """
        Initialize the manifest builder.

        Args:
            liveries_folder: Path to the folder containing .zip livery files
            manifest_output: Path where to save the manifest.json (default: current dir)
        """
        self.liveries_folder = Path(liveries_folder)
        self.manifest_output = Path(manifest_output) if manifest_output else Path.cwd()

        if not self.liveries_folder.exists():
            raise ValueError(f"Liveries folder not found: {self.liveries_folder}")

        if not self.manifest_output.exists():
            self.manifest_output.mkdir(parents=True, exist_ok=True)

    def calculate_hash(self, filepath):
        """Calculate MD5 hash of a file."""
        md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5.update(chunk)
        return md5.hexdigest()

    def get_file_size(self, filepath):
        """Get file size in MB."""
        return round(os.path.getsize(filepath) / (1024 * 1024), 2)

    def scan_liveries(self):
        """Scan liveries folder and collect .zip files."""
        liveries = []

        # Find all .zip files
        zip_files = sorted(self.liveries_folder.glob('*.zip'))

        if not zip_files:
            print(f"No .zip files found in {self.liveries_folder}")
            return liveries

        print(f"Found {len(zip_files)} livery file(s)")
        print()

        for i, zip_file in enumerate(zip_files, 1):
            driver_name = zip_file.stem  # filename without .zip
            file_hash = self.calculate_hash(zip_file)
            file_size = self.get_file_size(zip_file)

            livery_entry = {
                "driver": driver_name,
                "file": zip_file.name,
                "hash": file_hash,
                "size_mb": file_size
            }

            liveries.append(livery_entry)
            print(f"[{i}/{len(zip_files)}] {driver_name}")
            print(f"    File: {zip_file.name}")
            print(f"    Size: {file_size} MB")
            print(f"    Hash: {file_hash}")
            print()

        return liveries

    def build_manifest(self, league_name="GT3 Championship", version="1.0.0"):
        """Build the manifest JSON structure."""
        liveries = self.scan_liveries()

        manifest = {
            "league": league_name,
            "version": version,
            "updated": datetime.utcnow().isoformat() + "Z",
            "liveries": liveries
        }

        return manifest

    def save_manifest(self, manifest, filename="manifest.json"):
        """Save manifest to JSON file."""
        filepath = self.manifest_output / filename

        try:
            with open(filepath, 'w') as f:
                json.dump(manifest, f, indent=2)

            print(f"Manifest saved to: {filepath}")
            print(f"Total liveries: {len(manifest['liveries'])}")
            print(f"Version: {manifest['version']}")
            print(f"Updated: {manifest['updated']}")

            return True
        except Exception as e:
            print(f"Error saving manifest: {e}")
            return False

    def load_existing_manifest(self, filename="manifest.json"):
        """Load existing manifest for comparison."""
        filepath = self.manifest_output / filename

        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading existing manifest: {e}")

        return None

    def compare_manifests(self, old_manifest, new_manifest):
        """Compare old and new manifests and report changes."""
        if not old_manifest:
            print("No previous manifest found - creating new one")
            return

        old_drivers = {item['driver']: item['hash'] for item in old_manifest.get('liveries', [])}
        new_drivers = {item['driver']: item['hash'] for item in new_manifest.get('liveries', [])}

        added = set(new_drivers.keys()) - set(old_drivers.keys())
        removed = set(old_drivers.keys()) - set(new_drivers.keys())
        updated = {driver for driver in new_drivers if driver in old_drivers and new_drivers[driver] != old_drivers[driver]}

        print("=" * 50)
        print("MANIFEST CHANGES")
        print("=" * 50)

        if added:
            print(f"\nAdded ({len(added)}):")
            for driver in sorted(added):
                print(f"  + {driver}")

        if removed:
            print(f"\nRemoved ({len(removed)}):")
            for driver in sorted(removed):
                print(f"  - {driver}")

        if updated:
            print(f"\nUpdated ({len(updated)}):")
            for driver in sorted(updated):
                print(f"  ~ {driver}")

        if not any([added, removed, updated]):
            print("\nNo changes detected")

        print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="Build or update the ACC Livery Sync manifest",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_manifest.py C:\\path\\to\\liveries
  python build_manifest.py C:\\path\\to\\liveries -o C:\\output\\
  python build_manifest.py C:\\path\\to\\liveries -l "My League" -v "2.0.0"
        """
    )

    parser.add_argument(
        'liveries_folder',
        help='Path to folder containing .zip livery files'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output directory for manifest.json (default: current directory)',
        default=None
    )

    parser.add_argument(
        '-l', '--league',
        help='League name for manifest (default: "GT3 Championship")',
        default="GT3 Championship"
    )

    parser.add_argument(
        '-v', '--version',
        help='Manifest version (default: "1.0.0")',
        default="1.0.0"
    )

    parser.add_argument(
        '--no-compare',
        action='store_true',
        help='Skip comparison with existing manifest'
    )

    args = parser.parse_args()

    try:
        builder = ManifestBuilder(args.liveries_folder, args.output)

        print(f"Building manifest from: {builder.liveries_folder}")
        print()

        # Load existing manifest for comparison
        old_manifest = None if args.no_compare else builder.load_existing_manifest()

        # Build new manifest
        new_manifest = builder.build_manifest(args.league, args.version)

        # Compare if old manifest exists
        if old_manifest and not args.no_compare:
            builder.compare_manifests(old_manifest, new_manifest)
            print()

        # Save manifest
        if builder.save_manifest(new_manifest):
            print("\nManifest built successfully!")
            sys.exit(0)
        else:
            print("\nFailed to save manifest")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
