import sys
import os
import zlib
import hashlib
from typing import List, Tuple
from pathlib import Path


def cat_file(input: list[str]) -> None:

    blob_sha = input[3]
    try:
        object_path = os.path.join(
            ".git", "objects", blob_sha[:2], blob_sha[2:])
        print(f"Looking for object at: {object_path}", file=sys.stderr)

        with open(object_path, "rb") as f:  # rb -> read bytes
            compressed_content = f.read()
            print(
                f"Read {len(compressed_content)} compressed bytes", file=sys.stderr)

        decompressed_content = zlib.decompress(compressed_content)
        print(
            f"Decompressed to {len(decompressed_content)} bytes", file=sys.stderr)

        # Parse the header (blob <size>\0content)
        #    Find the null byte that separates header from content
        header_end_index = decompressed_content.find(
            b'\x00')  # b'\0' because content is bytes
        if header_end_index == -1:
            print(
                "Error: Invalid blob object, no null byte separator found.", file=sys.stderr)
            sys.exit(1)

        actual_content = decompressed_content[header_end_index + 1:]
        print(
            f"Actual content length: {len(actual_content)} bytes", file=sys.stderr)

        print(actual_content.decode(), end="")

    except FileNotFoundError:
        print(f"Error: Object {blob_sha} not found.", file=sys.stderr)
    except zlib.error as e:
        print(
            f"Error: Failed to decompress object {blob_sha}. {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)


def hash_object(input: list[str]) -> None:

    try:
        file = input[3]

        with open(file, 'rb') as f:
            content = f.read()

        object_type = "blob"
        header = f"{object_type} {len(content)}\0".encode('utf-8')
        object_content = header + content

        # hash the combined header and uncompressed data
        sha1_hash = hashlib.sha1(object_content).hexdigest()

        compressed_data = zlib.compress(
            object_content)  # compress after hashing

        object_directory = os.path.join(".git", "objects", sha1_hash[:2])
        object_path = os.path.join(object_directory, sha1_hash[2:])

        os.makedirs(object_directory, exist_ok=True)

        with open(object_path, 'wb') as f:
            f.write(compressed_data)  # write the compressed data

        print(sha1_hash)

    except FileNotFoundError:
        print(f"Error: File '{file}' not found.", file=sys.stderr)
    except PermissionError:
        print(
            f"Error: Permission denied to access '{file}' or create object.", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)


def ls_tree(input: list[str]) -> None:

    try:
        tree_sha = input[3]
        object_path = os.path.join(
            ".git", "objects", tree_sha[:2], tree_sha[2:])
        print(f"Looking for object at: {object_path}", file=sys.stderr)

        with open(object_path, "rb") as f:
            compressed_data = f.read()
        decompressed_data = zlib.decompress(compressed_data)

        header_end_index = decompressed_data.find(
            b'\x00')

        content = header_end_index + 1
        current_index = content

        while current_index < len(decompressed_data):

            null_byte_index = decompressed_data.find(
                b'\x00', current_index)  # start at current index

            mode_and_filename = decompressed_data[current_index:null_byte_index]

            try:
                mode_and_filename_str = mode_and_filename.decode('utf-8')
            except UnicodeDecodeError:
                print("Error decoding mode and filename.")
                return

            # max split 1 (in case file name has a space)
            str_parts = mode_and_filename_str.split(" ", 1)
            if len(str_parts) != 2:
                print("getting wrong string format")

            filename = str_parts[1]
            print(filename)
            current_index = null_byte_index + 21

    except FileNotFoundError:
        print(f"Error: File '{tree_sha}' not found.", file=sys.stderr)
    except PermissionError:
        print(
            f"Error: Permission denied to access '{tree_sha}' or create object.", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)


def store_object(content: bytes) -> str:

    sha1_hash = hashlib.sha1(content).hexdigest()
    compressed_data = zlib.compress(content)

    object_directory = Path(".git") / "objects" / sha1_hash[:2]
    object_path = object_directory / sha1_hash[2:]

    object_directory.mkdir(parents=True, exist_ok=True)

    with open(object_path, 'wb') as f:
        f.write(compressed_data)

    return sha1_hash


def write_tree(dir_path: Path) -> str:
    entries: List[Tuple[str, str, str, str]] = []

    for item_path in dir_path.iterdir():
        if item_path.name == ".git":
            continue

        mode: str = ""
        object_hash: str = ""
        object_type: str = ""

        if item_path.is_file():
            with open(item_path, "rb") as f:
                content = f.read()

            # Construct blob content with Git header
            blob_content_with_header = b"blob " + \
                str(len(content)).encode() + b"\0" + content

            object_hash = store_object(blob_content_with_header)

            object_type = "blob"
            mode = "100644"  # Standard file mode
            if os.stat(item_path).st_mode & 0o111:  # Check if executable bit is set
                mode = "100755"

        elif item_path.is_dir():
            object_type = "tree"
            object_hash = write_tree(item_path)
            mode = "40000"  # Directory mode
        else:
            continue  # Skip unknown types (e.g., symlinks)

        if object_hash:
            entries.append((mode, object_type, object_hash, item_path.name))

    # Sort entries by name
    entries.sort(key=lambda x: x[3])

    tree_content = b""
    for mode, obj_type, obj_hash, name in entries:
        # Git tree entry format: <mode> <name>\0<hash_bytes>
        tree_content += f"{mode} {name}".encode() + b"\0" + \
            bytes.fromhex(obj_hash)

    # Git tree object header: "tree <size>\0<tree_content>"
    tree_header = f"tree {len(tree_content)}".encode() + b"\0"
    final_tree_blob = tree_header + tree_content

    tree_sha1_hash = store_object(final_tree_blob)

    return tree_sha1_hash
