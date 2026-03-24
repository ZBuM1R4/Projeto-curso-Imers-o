import os


def save_uploaded_file(uploaded_file, destination_path: str) -> str:
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)

    with open(destination_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return destination_path