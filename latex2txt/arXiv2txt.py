import shutil
import tempfile
import zipfile
import tarfile
import sys
import os
from translatex import process_latex_file
import re



def find_main_tex_file(base_dir):
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.tex'):
                full_path = os.path.join(root, file)
                with open(full_path, encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if r'\begin{document}' in content:
                        return full_path
    return None


def resolve_tex_file(file_path, base_dir, visited=None):
    if visited is None:
        visited = set()
    resolved_text = ''
    if file_path in visited:
        return ''
    visited.add(file_path)
    try:
        with open(file_path, encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return f'% File not found: {file_path}\n'

    for line in lines:
        match = re.match(r'\\(input|include)\{(.+?)\}', line.strip())
        if match:
            sub_path = match.group(2)
            if not sub_path.endswith('.tex'):
                sub_path += '.tex'
            full_sub_path = os.path.join(base_dir, sub_path)
            if os.path.exists(full_sub_path):
                resolved_text += resolve_tex_file(full_sub_path, base_dir, visited)
            else:
                resolved_text += f'% WARNING: missing file {sub_path}\n'
        else:
            resolved_text += line
    return resolved_text



def extract_tex_from_archive(archive_path, paper_dir, output_base):
    import tempfile
    import shutil
    import os

    success = False
    temp_dir = tempfile.mkdtemp()

    try:

        if archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zf:
                zf.extractall(temp_dir)
        elif archive_path.endswith(('.tar.gz', '.tgz')):
            with tarfile.open(archive_path, 'r:gz') as tf:
                tf.extractall(temp_dir)
        else:
            print(f"Unsupported archive type: {archive_path}")
            return False
        success = True
    except Exception as e:
        print(f"Decompression failed: {archive_path}, error: {e}")
        return False

    if success:

        os.makedirs(paper_dir, exist_ok=True)


        for fname in os.listdir(temp_dir):
            src = os.path.join(temp_dir, fname)
            dst = os.path.join(paper_dir, fname)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)


        main_tex_path = find_main_tex_file(paper_dir)
        if not main_tex_path:
            print(f"Main tex not found in: {archive_path}")
            shutil.rmtree(paper_dir)
            return False

        full_tex = resolve_tex_file(main_tex_path, paper_dir)


        main_tex_final_path = os.path.join(output_base, 'main.tex')
        with open(main_tex_final_path, 'w', encoding='utf-8') as f:
            f.write(full_tex)

        result_txt_path = os.path.join(output_base, 'result.txt')


        try:
            process_latex_file(main_tex_final_path, result_txt_path)

            print(f"✓ Processed: {archive_path}")
        except Exception as e:
            print(f"✗ Failed to process {archive_path}: {e}")

        shutil.rmtree(paper_dir)

        if os.path.exists(main_tex_final_path):
            os.remove(main_tex_final_path)

        return True


def batch_process_latex(root_dir='1', output_dir='processed'):
    os.makedirs(output_dir, exist_ok=True)
    archives = [f for f in os.listdir(root_dir) if f.endswith(('.zip', '.tar.gz', '.tgz'))]

    for idx, archive in enumerate(archives):
        paper_id = f'paper_{idx + 1:04d}'
        paper_dir = os.path.join(output_dir, paper_id)

        archive_path = os.path.join(root_dir, archive)
        print(f'processing {archive_path} -> {paper_id}')

        extract_tex_from_archive(archive_path,paper_dir,output_dir)



if __name__ == '__main__':
    batch_process_latex()