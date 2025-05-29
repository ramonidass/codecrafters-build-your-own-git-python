import sys
import os
# from functions import cat_file, hash_object, ls_tree
from app.functions import cat_file, hash_object, ls_tree


def main():

    print("Logs from your program will appear here!", file=sys.stderr)

    if len(sys.argv) < 2:
        print("Usage: <command> [<args>]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")

    elif command == "cat-file":

        if len(sys.argv) < 4 or sys.argv[2] != "-p":
            print("Usage: cat-file -p <object_sha>", file=sys.stderr)
            sys.exit(1)

        cat_file(sys.argv)  # pass the entire sys.argv list

    elif command == "hash-object":

        if len(sys.argv) < 4 or sys.argv[2] != "-w":
            print("Usage: hash-object -w <file_name>", file=sys.stderr)
            sys.exit(1)

        hash_object(sys.argv)

    elif command == "ls-tree":

        if len(sys.argv) < 4:
            print(
                "Usage: ls-tree --name-only <tree-sha> or ls-tree <tree-sha>", file=sys.stderr)
            sys.exit(1)

        ls_tree(sys.argv)

    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
