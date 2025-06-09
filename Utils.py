# Turns a tree node into a list of nodes
def treeToList(tree, arr):
    arr.append(tree)
    for child in tree.children:
        treeToList(child, arr)
    return arr