import os

def check_path(file: str, title: str) -> str:
    """Checks if file name exist.
       If the name exists it appends a unique number,
       incrementing one at a time.
    """
    path = os.path.join(file,f"{title}.csv")
    counter = 1
    while os.path.exists(path):
        path = os.path.join(file, f"{title}_({str(counter)}).csv")
        counter += 1
    return path