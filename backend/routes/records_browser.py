from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pathlib import Path
import tempfile
import shutil
import zipfile
import os
from fastapi.responses import FileResponse
import json

router = APIRouter()

BASE_DIR = Path("/home/dev/DATABASE")  # change this


@router.get("/list")
def list_folders(subpath: str = ""):
    target = (BASE_DIR / subpath).resolve()

    # Security: prevent path traversal
    if not str(target).startswith(str(BASE_DIR)):
        raise HTTPException(status_code=400, detail="Invalid path")

    if not target.exists() or not target.is_dir():
        raise HTTPException(status_code=404, detail="Directory not found")

    folders = []
    for p in target.iterdir():
        if p.is_dir() and p.name != "current":
            metadata_file = p / "metadata.json"
            duration = "--:--"
            if metadata_file.exists():
                try:
                    with open(metadata_file, "r") as f:
                        meta_data = json.load(f)
                        # Extract duration (stripping microseconds for the UI)
                        raw_duration = meta_data.get("duration", "--:--")
                        duration = raw_duration.split(".")[0] 
                except (json.JSONDecodeError, IOError):
                    # Fallback if file is corrupt or unreadable
                    duration = "Error"
            folders.append({
                "name": p.name,
                "duration": duration
            })


    return {
        "path": str(target.relative_to(BASE_DIR)),
        "folders": sorted(folders, key=lambda x: x["name"].lower(), reverse=True)
    }


@router.get("/download-folder")
def download_folder(path: str, background_tasks: BackgroundTasks):
    folder = (BASE_DIR / path).resolve()

    if not str(folder).startswith(str(BASE_DIR)):
        raise HTTPException(status_code=400, detail="Invalid path")

    if not folder.exists() or not folder.is_dir():
        raise HTTPException(status_code=404, detail="Folder not found")

    tmp_dir = tempfile.mkdtemp()
    zip_path = Path(tmp_dir) / f"{folder.name}.zip"

    shutil.make_archive(
        zip_path.with_suffix(""),
        "zip",
        folder
    )

    background_tasks.add_task(shutil.rmtree, tmp_dir)

    return FileResponse(
        zip_path,
        filename=f"{folder.name}.zip",
        media_type="application/zip"
    )

@router.get("/download-multiple")
def download_multiple(
    background_tasks: BackgroundTasks,
    paths: list[str] = Query(...)
):
    if not paths:
        raise HTTPException(status_code=400, detail="No folders provided")

    tmp_dir = tempfile.mkdtemp()
    zip_path = Path(tmp_dir) / "selected_folders.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel_path in paths:
            folder = (BASE_DIR / rel_path).resolve()

            # Security checks
            if not str(folder).startswith(str(BASE_DIR)):
                raise HTTPException(status_code=400, detail=f"Invalid path: {rel_path}")

            if not folder.exists() or not folder.is_dir():
                raise HTTPException(status_code=404, detail=f"Folder not found: {rel_path}")

            # Add this folder under its own top-level name
            for root, _, files in os.walk(folder):
                for file in files:
                    full_path = Path(root) / file
                    rel_inside = full_path.relative_to(folder)
                    arcname = Path(folder.name) / rel_inside
                    zf.write(full_path, arcname)

    # Cleanup after response
    background_tasks.add_task(shutil.rmtree, tmp_dir)

    return FileResponse(
        zip_path,
        filename="selected_folders.zip",
        media_type="application/zip"
    )
