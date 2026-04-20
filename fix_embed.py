import os
import json
import base64
import re
import mimetypes
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

def fix_and_inline_images(filepath):
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
        if not raw_source:
            continue
            
        if isinstance(raw_source, str):
            sources = [raw_source]
        else:
            sources = raw_source

        new_sources = []
        cell_modified = False
        
        # 1. Inline existing attachments
        if 'attachments' in cell:
            attachments = cell['attachments']
            for i, line in enumerate(sources):
                for filename, mime_dict in list(attachments.items()):
                    if f"attachment:{filename}" in line:
                        mime_type = list(mime_dict.keys())[0]
                        b64_data = mime_dict[mime_type]
                        data_uri = f"data:{mime_type};base64,{b64_data}"
                        sources[i] = line.replace(f"attachment:{filename}", data_uri)
                        line = sources[i]
                        cell_modified = True
                        modified = True
            
            # Remove attachments to prevent duplication and save space
            del cell['attachments']

        img_tag_re = re.compile(r'<img[^>]+src=[\'"]([^\'"]+)[\'"][^>]*>')
        md_link_re = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')

        # 2. Check for missed relative paths
        for line in sources:
            # Find markdown links like ![alt](images/1.png)
            for alt_text, img_path in md_link_re.findall(line):
                if img_path.startswith('http') or img_path.startswith('data:'):
                    continue
                
                # Check if it exists
                abs_img_path = os.path.normpath(os.path.join(notebook_dir, img_path))
                if os.path.exists(abs_img_path):
                    with open(abs_img_path, 'rb') as img_f:
                        b64 = base64.b64encode(img_f.read()).decode('utf-8')
                    mime = mimetypes.guess_type(abs_img_path)[0] or 'image/png'
                    data_uri = f"data:{mime};base64,{b64}"
                    
                    line = line.replace(f"]({img_path})", f"]({data_uri})")
                    cell_modified = True
                    modified = True

            # Find HTML tags like <img src="images/1.png">
            for img_path in img_tag_re.findall(line):
                if img_path.startswith('http') or img_path.startswith('data:'):
                    continue
                
                # Check if exists
                abs_img_path = os.path.normpath(os.path.join(notebook_dir, img_path))
                if os.path.exists(abs_img_path):
                    with open(abs_img_path, 'rb') as img_f:
                        b64 = base64.b64encode(img_f.read()).decode('utf-8')
                    mime = mimetypes.guess_type(abs_img_path)[0] or 'image/png'
                    data_uri = f"data:{mime};base64,{b64}"
                    
                    line = line.replace(f'src="{img_path}"', f'src="{data_uri}"')
                    line = line.replace(f"src='{img_path}'", f"src='{data_uri}'")
                    cell_modified = True
                    modified = True

            new_sources.append(line)
            
        if cell_modified:
            cell['source'] = new_sources

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
        logging.info(f"Inlined images in: {filepath}")

repo_root = r"d:\machine-learning-introduction\Machine-Learning-Specialization_Coursera"

for root, dirs, files in os.walk(repo_root):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    for file in files:
        if file.endswith('.ipynb'):
            fix_and_inline_images(os.path.join(root, file))
