"""
Revert all image paths in notebooks back to original relative paths.
Converts /content/Machine-Learning-Specialization_Coursera/... paths
back to relative paths like images/foo.png
"""
import os, json, re

REPO_ROOT = r"d:\machine-learning-introduction\Machine-Learning-Specialization_Coursera"
COLAB_PREFIX = "/content/Machine-Learning-Specialization_Coursera/"

def process_notebook(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            nb = json.load(f)
    except Exception:
        return False

    notebook_dir = os.path.dirname(filepath)
    # Get the notebook's directory relative to repo root
    nb_rel_dir = os.path.relpath(notebook_dir, REPO_ROOT).replace(os.sep, '/')

    modified = False

    for cell in nb.get('cells', []):
        if cell.get('cell_type') != 'markdown':
            continue

        sources = cell.get('source', [])
        if not sources:
            continue
        if isinstance(sources, str):
            sources = [sources]

        new_sources = []
        cell_modified = False

        for line in sources:
            new_line = line

            # Find all /content/Machine-Learning-Specialization_Coursera/... paths
            def replace_colab_path(m):
                nonlocal cell_modified, modified
                full_path = m.group(0)
                # Extract the repo-relative path
                repo_rel = full_path[len(COLAB_PREFIX):]
                # Compute relative path from notebook dir
                # Both are relative to repo root, using forward slashes
                from os.path import relpath
                # Convert to OS paths for relpath calculation
                img_abs = os.path.join(REPO_ROOT, repo_rel.replace('/', os.sep))
                rel = os.path.relpath(img_abs, notebook_dir).replace(os.sep, '/')
                cell_modified = True
                modified = True
                return rel

            new_line = re.sub(
                re.escape(COLAB_PREFIX) + r'[^"\')>\s]+',
                replace_colab_path,
                new_line
            )

            new_sources.append(new_line)

        if cell_modified:
            cell['source'] = new_sources

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
        print(f"  REVERTED: {os.path.relpath(filepath, REPO_ROOT)}")
        return True
    return False


count = 0
for root, dirs, files in os.walk(REPO_ROOT):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    for f in files:
        if f.endswith('.ipynb'):
            if process_notebook(os.path.join(root, f)):
                count += 1

print(f"\nDone. Reverted {count} notebooks to local relative paths.")
