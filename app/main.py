import sys
import os


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    # Uncomment this block to pass the first stage

    command = sys.argv[1]
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
    else:
        raise RuntimeError(f"Unknown command #{command}")

    if command == "cat-file":
        if len(sys.argv) < 4 or sys.argv[2] != "-p":
            print("Usage: mygit cat-file -p <object_sha>", file=sys.stderr)
            sys.exit(1)

        blob_sha = sys.argv[3]

        try:
            # object path
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
                b'\0')  # b'\0' because content is bytes
            if header_end_index == -1:
                print(
                    "Error: Invalid blob object, no null byte separator found.", file=sys.stderr)
                sys.exit(1)

            actual_content = decompressed_content[header_end_index + 1:]
            print(
                f"Actual content length: {len(actual_content)} bytes", file=sys.stderr)

            # 5. Print the actual blob content to standard output
            #    The tests expect the output to be exactly the blob's content.
            #    If the content is text, you might decode it, but for raw bytes,
            #    writing directly to sys.stdout.buffer is safest.
            #    The challenge usually expects text output, so decode and print without extra newline.
            # Or actual_content.decode('utf-8')
            sys.stdout.write(actual_content.decode())
            # print(actual_content.decode(), end="")

        except FileNotFoundError:
            print(f"Error: Object {blob_sha} not found.", file=sys.stderr)
            sys.exit(1)
        except zlib.error as e:
            print(
                f"Error: Failed to decompress object {blob_sha}. {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
