from tkinter.font import Font

def paint_tree(layout_object, display_list):
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)

def tree_to_list(tree, list):
    list.append(tree)
    for child in tree.children:
        tree_to_list(child, list)
    return list

FONTS = {}

def get_font(size, weight, slant) -> Font:
    key = (size, weight, slant)
    if key not in FONTS:
        font = Font(size=size, weight=weight, slant=slant)
        FONTS[key] = font
    return FONTS[key]