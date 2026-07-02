# Build Mario remake

GitHub Actions will build desktop packages automatically:

- Windows: `Mario remake.exe`
- macOS: `Mario remake.app` zipped as `Mario remake-macOS.zip`

## Download from Actions

After pushing to `main` or `master`:

1. Open the repository on GitHub.
2. Go to `Actions`.
3. Open the latest `Build Desktop Apps` run.
4. Download the Windows or macOS artifact.

## Create a release

Push a version tag:

```powershell
git tag v1.0.0
git push origin v1.0.0
```

The workflow will create a GitHub Release and upload:

- `Mario remake.exe`
- `Mario remake-macOS.zip`
- `mario_remake_cover.png`

## Local build

```powershell
python -m pip install -r requirements.txt
python -m PyInstaller mario_remake.spec --noconfirm --clean
```

The local exe will be:

```text
dist\Mario remake.exe
```

Local macOS build must be run on a Mac:

```bash
python -m pip install -r requirements.txt
mkdir -p build/icon.iconset
sips -z 1024 1024 gamemario/assets/images/mario_remake_cover.png --out build/icon.iconset/icon_512x512@2x.png
iconutil -c icns build/icon.iconset -o gamemario/assets/images/mario_remake.icns
python -m PyInstaller mario_remake_macos.spec --noconfirm --clean
```
