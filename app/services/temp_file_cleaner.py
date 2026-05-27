from pathlib import Path


TEMP_DIRECTORIES = [
    Path("data/input"),
    Path("data/temp"),
]


def clean_temp_files():
    for directory in TEMP_DIRECTORIES:
        if not directory.exists():
            continue

        for file_path in directory.iterdir():
            if file_path.is_file():
                try:
                    file_path.unlink()
                except Exception:
                    pass