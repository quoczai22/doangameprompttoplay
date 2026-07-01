# Build Mario remake

GitHub Actions will build a Windows one-file exe automatically.

## Download from Actions

After pushing to `main` or `master`:

1. Open the repository on GitHub.
2. Go to `Actions`.
3. Open the latest `Build Windows EXE` run.
4. Download the `Mario remake.exe` artifact.

## Create a release

Push a version tag:

```powershell
git tag v1.0.0
git push origin v1.0.0
```

The workflow will create a GitHub Release and upload:

- `Mario remake.exe`
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
