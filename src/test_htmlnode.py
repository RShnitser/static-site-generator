import unittest

from htmlnode import (HTMLNode, LeafNode, ParentNode)

class TestHTMLNode(unittest.TestCase):
    def test_to_html_props(self):
        node = HTMLNode("div", "Hello", None, {"class": "section", "id": "div_id"})
        self.assertEqual(node.props_to_html(), 'class="section" id="div_id"')

    def test_to_html_no_child(self):
        node = LeafNode("div", "Hello",{"class": "section"})
        self.assertEqual(node.to_html(), '<div class="section">Hello</div>')

    def test_to_html_no_tag(self):
        node = LeafNode(None, "Hello")
        self.assertEqual(node.to_html(), 'Hello')

    def test_to_html_parent(self):
        node = ParentNode(
            "p",
            [
                LeafNode(None, "Normal text"),
            ],
         )
        self.assertEqual(node.to_html(), '<p >Normal text</p>')
    
    def test_to_html_parent2(self):
        node = ParentNode(
            "p",
            [
                LeafNode(None, "Normal text"),
                LeafNode("div", "Hello",{"class": "section"}),
                ParentNode("p",[LeafNode(None, "Normal text"),],)
            ],
         )
        self.assertEqual(node.to_html(), '<p >Normal text<div class="section">Hello</div><p >Normal text</p></p>')

if __name__ == "__main__":
    unittest.main()