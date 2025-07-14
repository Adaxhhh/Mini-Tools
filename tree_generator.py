import os
import argparse
import re

def get_directory_structure(startpath, ignore_gitignore=False):
    """
    Generates a string representation of the directory structure with Unicode symbols.

    Args:
        startpath (str): The root directory to start scanning from.
        ignore_gitignore (bool): If True, .gitignore rules are ignored.

    Returns:
        str: A string representing the directory structure in a tree format.
    """
    structure_str = ""
    ignored_patterns = []

    if not ignore_gitignore and os.path.exists(os.path.join(startpath, '.gitignore')):
        with open(os.path.join(startpath, '.gitignore'), 'r', encoding='utf-8') as f: # Ensure reading gitignore with utf-8
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    is_negated = False
                    if line.startswith('!'):
                        is_negated = True
                        line = line[1:]

                    line = line.strip('/')

                    pattern = re.escape(line)
                    pattern = pattern.replace(r'\*', '.*')
                    pattern = pattern.replace(r'\?', '.')

                    if not line.startswith('/') and not line.startswith('**'):
                        pattern = f".*{pattern}"

                    if line.endswith('/') and not line.endswith('**'):
                        pattern = f"{pattern}/?.*"

                    if '/' not in line and not line.endswith('/') and not line.startswith('**'):
                        pattern = f"(^|.*/){pattern}(/|$)"

                    ignored_patterns.append({'pattern': re.compile(pattern), 'negated': is_negated})

    unignored_paths = set()

    # First pass to identify explicitly unignored paths
    if not ignore_gitignore:
        for root, dirs, files in os.walk(startpath):
            relative_root = os.path.relpath(root, startpath)
            if relative_root == ".":
                relative_root = ""

            all_entries_at_level = [os.path.join(relative_root, d) for d in dirs] + \
                                   [os.path.join(relative_root, f) for f in files]

            for entry_path in all_entries_at_level:
                normalized_entry_path = entry_path.replace(os.sep, '/')
                for rule in ignored_patterns:
                    if rule['negated'] and rule['pattern'].search(normalized_entry_path):
                        unignored_paths.add(entry_path)
                        if os.path.isdir(os.path.join(startpath, entry_path)):
                            for dirpath, dirnames, filenames in os.walk(os.path.join(startpath, entry_path)):
                                rel_subpath = os.path.relpath(dirpath, startpath)
                                for f in filenames:
                                    unignored_paths.add(os.path.join(rel_subpath, f))
                                for d in dirnames:
                                    unignored_paths.add(os.path.join(rel_subpath, d))

    # This function will recursively build the structure
    def build_tree(current_dir, prefix=""):
        nonlocal structure_str
        try:
            contents = sorted(os.listdir(current_dir))
        except PermissionError:
            # Handle cases where the script doesn't have permission to list a directory
            structure_str += f"{prefix}├── [Permission Denied]\n"
            return
        except FileNotFoundError:
            # Handle cases where a directory might have been deleted during walk
            structure_str += f"{prefix}├── [Not Found]\n"
            return

        dirs = [d for d in contents if os.path.isdir(os.path.join(current_dir, d))]
        files = [f for f in contents if os.path.isfile(os.path.join(current_dir, f))]

        # Filter out ignored directories and files
        if not ignore_gitignore:
            filtered_dirs = []
            for d in dirs:
                relative_path_dir = os.path.relpath(os.path.join(current_dir, d), startpath)
                normalized_relative_path_dir = relative_path_dir.replace(os.sep, '/')
                should_ignore_dir = False
                for rule in ignored_patterns:
                    if not rule['negated'] and rule['pattern'].search(normalized_relative_path_dir) and relative_path_dir not in unignored_paths:
                        should_ignore_dir = True
                        break
                    elif rule['negated'] and rule['pattern'].search(normalized_relative_path_dir):
                        should_ignore_dir = False
                if not should_ignore_dir:
                    filtered_dirs.append(d)
            dirs = filtered_dirs

            filtered_files = []
            for f in files:
                relative_path_file = os.path.relpath(os.path.join(current_dir, f), startpath)
                normalized_relative_path_file = relative_path_file.replace(os.sep, '/')
                should_ignore_file = False
                for rule in ignored_patterns:
                    if not rule['negated'] and rule['pattern'].search(normalized_relative_path_file) and relative_path_file not in unignored_paths:
                        should_ignore_file = True
                        break
                    elif rule['negated'] and rule['pattern'].search(normalized_relative_path_file):
                        should_ignore_file = False
                if not should_ignore_file:
                    filtered_files.append(f)
            files = filtered_files

        all_items = dirs + files
        for i, item in enumerate(all_items):
            path = os.path.join(current_dir, item)
            is_last = (i == len(all_items) - 1)
            
            # Unicode symbols for better visual
            pointer = "└── " if is_last else "├── "
            structure_str += f"{prefix}{pointer}{item}\n"

            if os.path.isdir(path):
                extension = "    " if is_last else "│   "
                build_tree(path, prefix + extension)

    # Start building the tree from the root directory
    base_name = os.path.basename(startpath)
    structure_str += f"{base_name}/\n"
    build_tree(startpath, "")

    return structure_str

def main():
    parser = argparse.ArgumentParser(description="Generate a directory structure in Markdown format.")
    parser.add_argument("-u", "--ignore-gitignore", action="store_true",
                        help="Ignore .gitignore rules and list all files and directories.")
    args = parser.parse_args()

    current_directory = os.getcwd()
    structure = get_directory_structure(current_directory, args.ignore_gitignore)

    output_filename = "Structure.md"
    # Ensure UTF-8 encoding for output file
    with open(output_filename, "w", encoding='utf-8') as f:
        f.write("# Directory Structure\n\n")
        f.write("```\n")
        f.write(structure)
        f.write("```\n")

    print(f"Directory structure written to {output_filename}")

if __name__ == "__main__":
    main()
