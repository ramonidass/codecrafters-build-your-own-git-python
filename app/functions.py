import sys
import os
import zlib
import hashlib


def cat_file(input):

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

        # 4. Parse the header (blob <size>\0content)
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


def hash_object(input):

    try:

        file = input[3]

        with open(file, 'rb') as f:
            content = f.read()

        compressed_data = zlib.compress(content)

        object_type = "blob"
        header = f"{object_type} {len(content)}\0".encode('utf-8')
        object_content = header + compressed_data

        # hash the combined header and compressed data
        sha1_hash = hashlib.sha1(object_content).hexdigest()

        object_directory = os.path.join(".git", "objects", sha1_hash[:2])
        object_path = os.path.join(object_directory, sha1_hash[2:])

        os.makedirs(object_directory, exist_ok=True)

        with open(object_path, 'wb') as f:
            f.write(object_content)

        print(sha1_hash)

    except FileNotFoundError:
        print(f"Error: File '{file}' not found.", file=sys.stderr)
    except PermissionError:
        print(
            f"Error: Permission denied to access '{file}' or create object.", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
