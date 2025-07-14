# 🌳 Directory Tree Generator

A Python script to generate a visual directory structure for your current folder.

## ✨ Features

* **Tree View:** Generates a clean, hierarchical view of files and directories.
* **`.gitignore` Support:** Automatically excludes paths listed in `.gitignore`.
* **Override `.gitignore`:** Use the `-u` argument to list all files and directories.
* **Markdown Output:** Writes the structure to `Structure.md`.

## 🚀 Usage

1.  Save the script (e.g., `tree_generator.py`) in your project directory.
2.  Run from your terminal:

    ```bash
    python tree_generator.py
    # OR to include .gitignore entries:
    python tree_generator.py -u
    ```

## 💡 Purpose

Provides a quick, readable overview of your project's file structure for documentation or navigation.
