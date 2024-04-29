from textnode import markdown_to_html_node
import shutil
import os


def copy_to_public(src, dest):
    if not os.path.exists(dest):
        os.mkdir(dest)
    paths = os.listdir(src)
    for p in paths:
        src_path = os.path.join(src, p)
        dst_path = os.path.join(dest, p)
        if os.path.isfile(src_path):
            shutil.copy(src_path, dst_path)
        else:
            copy_to_public(src_path, dst_path)

def extract_title(markdown):
    lines = markdown.splitlines()
    for line in lines:
        if line.startswith("# "):
            title = line.lstrip("# ")
            return title


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    m = open(from_path, "rt")
    t = open(template_path, "rt")
    markdown = m.read()
    template = t.read()
    title = extract_title(markdown)
    node = markdown_to_html_node(markdown)
    html = node.to_html()
    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", html)

    dest_dir_path = os.path.dirname(dest_path)
    if dest_dir_path != "":
        os.makedirs(dest_dir_path, exist_ok=True)

    content = open(dest_path, "w")
    content.write(template)
    content.close()
    
    m.close()
    t.close()

def generate_page_recursive(dir_path_content, template_path, dest_dir_path):
    dirs = os.listdir(dir_path_content)
    for dir in dirs:
        src = os.path.join(dir_path_content, dir)
        dest = os.path.join(dest_dir_path, dir)
        if os.path.isfile(src):
            file = dir.split(".")
            if file[1] == "md":
                dest_f = os.path.join(dest_dir_path, ".".join([file[0], "html"]))
                generate_page(src, template_path, dest_f)
        else:
            generate_page_recursive(src, template_path, dest)

def main():
    if os.path.exists("public"):
        shutil.rmtree("public/")
        os.mkdir("public")
    else:
        os.mkdir("public")

    copy_to_public("static", "public")
    generate_page_recursive("content", "template.html", "public")

main()