from htmlnode import LeafNode, ParentNode
import re

text_type_text = "text"
text_type_bold = "bold"
text_type_italic = "italic"
text_type_code = "code"
text_type_link = "link"
text_type_image = "image"

block_type_paragraph = "paragraph"
block_type_heading = "heading"
block_type_code = "code"
block_type_quote = "quote"
block_type_ulist = "unordered_list"
block_type_olist = "ordered_list"

class TextNode():

    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        return self.text == other.text and self.text_type == other.text_type and self.url == other.url
    
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type}, {self.url})"
    
def text_node_to_html_node(text_node):
    if text_node.text_type == text_type_text:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == text_type_bold:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == text_type_italic:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == text_type_code:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == text_type_link:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    elif text_node.text_type == text_type_image:
        return LeafNode("img", "", {"src":text_node.url, "alt":text_node.text})
    raise ValueError("invalid text type")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    result = []
    for node in old_nodes:
        if node.text_type == text_type_text:
            nodes = []
            split = node.text.split(delimiter)
            if len(split) % 2 == 0:
                 raise Exception("invalid markdown")
            isText = True
            for text in split:
                if len(text) == 0:
                    pass
                else:
                    if isText:
                        nodes.append(TextNode(text, text_type_text))
                    else:
                        nodes.append(TextNode(text, text_type))
                isText = not isText
            result.extend(nodes)

        else:
            result.append(node)
    return result

def extract_markdown_images(text):
    result = re.findall(r"!\[(.*?)\]\((.*?)\)", text)
    return result

def extract_markdown_links(text):
    result = re.findall(r"\[(.*?)\]\((.*?)\)", text)
    return result

def split_nodes_image(old_nodes):
    result = []
    for node in old_nodes:
        if node.text_type == text_type_text:
            nodes = []
            next_text = node.text
            img_tup_list = extract_markdown_images(node.text)
            
            for img_tup in img_tup_list:

                split = next_text.split(f"![{img_tup[0]}]({img_tup[1]})", 1)
                if len(split) != 2:
                    raise Exception("invalid markdown")
                if len(split[0]) > 0:
                    nodes.append(TextNode(split[0], text_type_text))
                nodes.append(TextNode(img_tup[0], text_type_image, img_tup[1]))
                next_text = split[1]
            if len(next_text) > 0:
                nodes.append(TextNode(next_text, text_type_text))
            result.extend(nodes)
        else:
            result.append(node)
    return result

def split_nodes_link(old_nodes):
    result = []
    for node in old_nodes:
        if node.text_type == text_type_text:
            nodes = []
            next_text = node.text
            lnk_tup_list = extract_markdown_links(node.text)
          
            for lnk_tup in lnk_tup_list:

                split = next_text.split(f"[{lnk_tup[0]}]({lnk_tup[1]})", 1)
                if len(split) != 2:
                    raise Exception("invalid markdown")
                if len(split[0]) > 0:
                    nodes.append(TextNode(split[0], text_type_text))
                nodes.append(TextNode(lnk_tup[0], text_type_link, lnk_tup[1]))
                next_text = split[1]
            if len(next_text) > 0:
                nodes.append(TextNode(next_text, text_type_text))
            result.extend(nodes)
        else:
            result.append(node)
    return result

def text_to_textnodes(text):
    result = [TextNode(text, text_type_text)] 
    result = split_nodes_delimiter(result, "**", text_type_bold)
    result = split_nodes_delimiter(result, "*", text_type_italic)
    result = split_nodes_delimiter(result, "`", text_type_code)
    result = split_nodes_image(result)
    result = split_nodes_link(result)
    return result

def markdown_to_blocks(markdown):
    result = []
    blocks = markdown.split("\n\n")
    for block in blocks:
        if len(block) == 0:
          continue
        block = block.strip()
        result.append(block)
    return result

def block_to_block_type(block):
   
    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return block_type_heading
    
    lines = block.splitlines()

    if len(lines) > 1 and lines[0].startswith("```") and lines[-1].startswith("```"):
        return block_type_code
    
    if block.startswith(">"):
        for line in lines:
            if not line.startswith(">"):
                return block_type_paragraph
            return block_type_quote
    if block.startswith("* "):
        for line in lines:
            if not line.startswith("* "):
                return block_type_paragraph
        return block_type_ulist
    if block.startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                return block_type_paragraph
        return block_type_ulist
    if block.startswith("1. "):
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return block_type_paragraph
            i += 1
        return block_type_olist
    return block_type_paragraph

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children


def paragraph_to_html_node(block):
    lines = block.split("\n")
    paragraph = " ".join(lines)
    children = text_to_children(paragraph)
    return ParentNode("p", children)


def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    if level + 1 >= len(block):
        raise ValueError(f"Invalid heading level: {level}")
    text = block[level + 1 :]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)


def code_to_html_node(block):
    if not block.startswith("```") or not block.endswith("```"):
        raise ValueError("Invalid code block")
    text = block[4:-3]
    children = text_to_children(text)
    code = ParentNode("code", children)
    return ParentNode("pre", [code])


def olist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[3:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ol", html_items)


def ulist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[2:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ul", html_items)


def quote_to_html_node(block):
    lines = block.split("\n")
    new_lines = []
    for line in lines:
        if not line.startswith(">"):
            raise ValueError("Invalid quote block")
        new_lines.append(line.lstrip(">").strip())
    content = " ".join(new_lines)
    children = text_to_children(content)
    return ParentNode("blockquote", children)

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)
    return ParentNode("div", children, None)


def block_to_html_node(block):
    block_type = block_to_block_type(block)
    if block_type == block_type_paragraph:
        return paragraph_to_html_node(block)
    if block_type == block_type_heading:
        return heading_to_html_node(block)
    if block_type == block_type_code:
        return code_to_html_node(block)
    if block_type == block_type_olist:
        return olist_to_html_node(block)
    if block_type == block_type_ulist:
        return ulist_to_html_node(block)
    if block_type == block_type_quote:
        return quote_to_html_node(block)
    raise ValueError("Invalid block type")
    
    