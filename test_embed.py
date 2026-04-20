import os
import json
import base64
import re
import mimetypes

def embed_images_in_notebook(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            nb = json.load(f)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return

    notebook_dir = os.path.dirname(filepath)
    modified = False

    for cell in nb.get('cells', []):
        if cell.get('cell_type') != 'markdown':
            continue

        raw_source = cell.get('source', [])
        if isinstance(raw_source, str):
            sources = [raw_source]
        else:
            sources = raw_source

        new_sources = []
        cell_modified = False
        
        # Regex to match <img src="..."> and ![]()
        img_tag_re = re.compile(r'<img[^>]+src=[\'"]([^\'"]+)[\'"][^>]*>')
        md_link_re = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')

        # Initialize attachments if we don't have it
        if 'attachments' not in cell:
            cell['attachments'] = {}

        for line in sources:
            original_line = line
            
            # Find markdown links like ![alt](images/1.png)
            for alt_text, img_path in md_link_re.findall(line):
                if img_path.startswith('http') or img_path.startswith('attachment:') or img_path.startswith('data:'):
                    continue
                
                # Check if it exists
                abs_img_path = os.path.normpath(os.path.join(notebook_dir, img_path))
                if os.path.exists(abs_img_path):
                    filename = os.path.basename(abs_img_path)
                    # base64 encode
                    with open(abs_img_path, 'rb') as img_f:
                        b64 = base64.b64encode(img_f.read()).decode('utf-8')
                    mime = mimetypes.guess_type(abs_img_path)[0] or 'image/png'
                    
                    cell['attachments'][filename] = {mime: b64}
                    # Replace in line
                    line = line.replace(f"]({img_path})", f"](attachment:{filename})")
                    cell_modified = True
                    modified = True

            # Find HTML tags like <img src="images/1.png">
            for img_path in img_tag_re.findall(line):
                if img_path.startswith('http') or img_path.startswith('attachment:') or img_path.startswith('data:'):
                    continue
                
                # Check if exists
                abs_img_path = os.path.normpath(os.path.join(notebook_dir, img_path))
                if os.path.exists(abs_img_path):
                    filename = os.path.basename(abs_img_path)
                    with open(abs_img_path, 'rb') as img_f:
                        b64 = base64.b64encode(img_f.read()).decode('utf-8')
                    mime = mimetypes.guess_type(abs_img_path)[0] or 'image/png'
                    
                    cell['attachments'][filename] = {mime: b64}
                    # Replace in line
                    line = line.replace(f'src="{img_path}"', f'src="attachment:{filename}"')
                    line = line.replace(f"src='{img_path}'", f"src='attachment:{filename}'")
                    cell_modified = True
                    modified = True

            new_sources.append(line)
        
        if cell_modified:
            cell['source'] = new_sources

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
        print(f"Modified: {filepath}")

# Test on one
embed_images_in_notebook(r"d:\machine-learning-introduction\Machine-Learning-Specialization_Coursera\C1 - Supervised Machine Learning - Regression and Classification\Week1\Optional Labs\C1_W1_Lab02_Model_Representation_Soln.ipynb")
