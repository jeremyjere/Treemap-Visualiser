from __future__ import annotations

import math
import os
from random import randint
from typing import List, Tuple, Optional


class TMTree:
    """A TreeMappableTree: a tree that is compatible with the treemap
    visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this assignment will involve you implementing new public
    *methods* for this interface.
    You should not add any new public methods other than those required by
    the client code.
    You can, however, freely add private methods as needed.

    === Public Attributes ===
    rect:
        The pygame rectangle representing this node in the treemap
        visualization.
    data_size:
        The size of the data represented by this tree.

    === Private Attributes ===
    _colour:
        The RGB colour value of the root of this tree.
    _name:
        The root value of this tree, or None if this tree is empty.
    _subtrees:
        The subtrees of this tree.
    _parent_tree:
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.
    _expanded:
        Whether or not this tree is considered expanded for visualization.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.

    - _colour's elements are each in the range 0-255.

    - If _name is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.

    - if _parent_tree is not None, then self is in _parent_tree._subtrees

    - if _expanded is True, then _parent_tree._expanded is True
    - if _expanded is False, then _expanded is False for every tree
      in _subtrees
    - if _subtrees is empty, then _expanded is False
    """

    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: str
    _subtrees: List[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool

    def __init__(self, name: str, subtrees: List[TMTree],
                 data_size: int = 0) -> None:
        """Initialize a new TMTree with a random colour and the provided <name>.

        If <subtrees> is empty, use <data_size> to initialize this tree's
        data_size.

        If <subtrees> is not empty, ignore the parameter <data_size>,
        and calculate this tree's data_size instead.

        Set this tree as the parent for each of its subtrees.

        Precondition: if <name> is None, then <subtrees> is empty.
        >>> tree = TMTree("1", [], 20)
        >>> tree.data_size
        20

        >>> folder = TMTree("2", [tree], 500)
        >>> folder.data_size
        20
        """
        self.rect = (0, 0, 0, 0)
        self._name = name
        self._subtrees = subtrees[:]
        self._parent_tree = None

        # You will change this in Task 5
        self._expanded = False

        # 1. Initialize self._colour and self.data_size, according to the
        # docstring.
        # 2. Set this tree as the parent for each of its subtrees.

        r1 = randint(0, 255)
        r2 = randint(0, 255)
        r3 = randint(0, 255)
        self._colour = (r1, r2, r3)
        # You should not get os.datasize() for folders, only files.
        if self._name is None or not self._subtrees:
            self.data_size = data_size
        else:
            size = 0
            for sub in subtrees:
                if sub._name is not None:
                    size += sub.data_size
            self.data_size = size

        for sub in self._subtrees:
            sub._parent_tree = self

    def is_empty(self) -> bool:
        """Return True iff this tree is empty.
        >>> tree = TMTree("1", [], 20)
        >>> tree.is_empty()
        False
        """
        return self._name is None

    def get_parent(self) -> Optional[TMTree]:
        """Returns the parent of this tree.
        >>> tree = TMTree("1", [], 20)
        >>> tree2 = TMTree("2", [tree], 300)
        >>> tree._parent_tree = tree2
        >>> parent = tree.get_parent()
        >>> parent._subtrees[0]._name
        '1'
        """
        return self._parent_tree

    def update_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        """Update the rectangles in this tree and its descendents using the
        treemap algorithm to fill the area defined by pygame rectangle <rect>.
        >>> tree = TMTree("1", [], 20)
        >>> tree.rect
        (0, 0, 0, 0)
        >>> tree.update_rectangles((0, 0, 50, 60))
        >>> tree.rect
        (0, 0, 50, 60)

        """
        # Read the handout carefully to help get started identifying base cases,
        # then write the outline of a recursive step.
        #
        # Programming tip: use "tuple unpacking assignment" to easily extract
        # elements of a rectangle, as follows.
        # x, y, width, height = rect

        x, y, width, height = rect
        self.rect = rect
        if self.data_size == 0:
            self.rect = (0, 0, 0, 0)
            for subtree in self._subtrees:
                subtree.update_rectangles((0, 0, 0, 0))
        elif not self._subtrees or not self._expanded:
            self.rect = (x, y, width, height)
        else:
            if width > height:  # horizontal rectangles
                self._update_horiz_rectangles(rect)

            elif width <= height:  # vertical rectangles
                self._update_vert_rectangles(rect)

    def _update_horiz_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        x, y, width, height = rect
        curr_width = 0
        # truncate every subtree but the last
        for i in range(len(self._subtrees) - 1):
            if self.data_size == 0:  # avoid ZeroDivisionError
                new_width = 0
            else:
                new_width = int(width * (self._subtrees[i].data_size
                                         / self.data_size))
            self._subtrees[i].update_rectangles(
                (x + curr_width, y, new_width, height))
            curr_width += new_width
        self._subtrees[-1].update_rectangles(
            (x + curr_width, y, width - curr_width, height))

    def _update_vert_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        x, y, width, height = rect
        curr_height = 0
        for i in range(len(self._subtrees) - 1):
            if self.data_size == 0:
                new_height = 0
            else:
                new_height = int(height * (self._subtrees[i].data_size
                                           / self.data_size))
            self._subtrees[i].update_rectangles(
                (x, y + curr_height, width, new_height))
            curr_height += new_height
        self._subtrees[-1].update_rectangles(
            (x, y + curr_height, width, height - curr_height))

    def get_rectangles(self) -> List[Tuple[Tuple[int, int, int, int],
                                           Tuple[int, int, int]]]:
        """Return a list with tuples for every leaf in the displayed-tree
        rooted at this tree. Each tuple consists of a tuple that defines the
        appropriate pygame rectangle to display for a leaf, and the colour
        to fill it with.
        >>> tree = TMTree("1", [], 20)
        >>> rect = tree.get_rectangles()
        >>> rect[0][0]
        (0, 0, 0, 0)
        """
        lst = []
        if self.data_size == 0:
            return []
        if not self._subtrees or not self._expanded:  # if leaf
            return [(self.rect, self._colour)]
        else:
            for subtree in self._subtrees:
                lst.extend(subtree.get_rectangles())
        return lst

    def get_tree_at_position(self, pos: Tuple[int, int]) -> Optional[TMTree]:
        """Return the leaf in the displayed-tree rooted at this tree whose
        rectangle contains position <pos>, or None if <pos> is outside of this
        tree's rectangle.

        If <pos> is on the shared edge between two or more rectangles,
        always return the leftmost and topmost rectangle (wherever applicable).
        >>> tree = TMTree("1", [], 20)
        >>> obj = tree.get_tree_at_position((0, 0))
        >>> obj._name
        '1'
        """

        if not self._subtrees or not self._expanded:
            mouse_x, mouse_y = pos
            lower_x = self.rect[0]
            lower_y = self.rect[1]
            if lower_x <= mouse_x <= (lower_x + self.rect[2]) and \
                    lower_y <= mouse_y <= (lower_y + self.rect[3]):
                return self
        else:
            for subtree in self._subtrees:
                leaf = subtree.get_tree_at_position(pos)
                if leaf is not None:
                    return leaf
        return None

    def update_data_sizes(self) -> int:
        """Update the data_size for this tree and its subtrees, based on the
        size of their leaves, and return the new size.

        If this tree is a leaf, return its size unchanged.
        >>> tree = TMTree("1", [], 20)
        >>> tree.update_data_sizes()
        20
        """

        if not self._subtrees:
            return self.data_size
        else:
            size = 0
            for sub in self._subtrees:
                size += sub.update_data_sizes()
            self.data_size = size
            return self.data_size

    def move(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, move this
        tree to be the last subtree of <destination>. Otherwise, do nothing.
        >>> tree = TMTree("1", [], 20)
        >>> tree2 = TMTree("2", [tree], 30)
        >>> tree._parent_tree = tree2
        >>> dest = TMTree("3", [tree2], 50)
        >>> tree2._parent_tree = dest
        >>> tree4 = TMTree("4", [dest], 20)
        >>> dest._parent_tree = tree4
        >>> tree.move(dest)
        >>> dest._subtrees[1]._name
        '1'
        """
        if not self._subtrees and destination._subtrees:
            destination._subtrees.append(self)
            self._parent_tree._subtrees.remove(self)
            if not self._parent_tree._subtrees:
                self._parent_tree._expanded = False
                self._parent_tree.data_size = 0
            destination._update_all_data_sizes()
            self._parent_tree = destination

    def change_size(self, factor: float) -> None:
        """Change the value of this tree's data_size attribute by <factor>.

        Always round up the amount to change, so that it's an int, and
        some change is made.

        Do nothing if this tree is not a leaf.
        >>> tree = TMTree("1", [], 20)
        >>> tree.change_size(30)
        >>> tree.data_size
        50
        """
        size = 0
        if not self._subtrees:
            if factor >= 0:
                size = math.ceil(factor)
            elif factor < 0:
                size = math.floor(factor)
            self.data_size = max(1, self.data_size + size)
            self._update_all_data_sizes()

    def _update_all_data_sizes(self) -> None:
        if self._parent_tree:
            self._parent_tree._update_all_data_sizes()
        else:
            self.update_data_sizes()
        return

    def delete_self(self) -> bool:
        """Removes the current node from the visualization and
        returns whether the deletion was successful.

        Only do this if this node has a parent tree.

        Do not set self._parent_tree to None, because it might be used
        by the visualiser to go back to the parent folder.
        >>> tree = TMTree("1", [], 20)
        >>> tree2 = TMTree("2", [tree], 30)
        >>> tree._parent_tree = tree2
        >>> tree.delete_self()
        True
        >>> tree2._subtrees
        []
        """
        if self._parent_tree is not None:
            self._parent_tree._subtrees.remove(self)
            if not self._parent_tree._subtrees:
                self._parent_tree.data_size = 0
            self._parent_tree.update_rectangles(self._parent_tree.rect)
            self._parent_tree._update_all_data_sizes()
            return True
        return False

    def expand(self) -> None:
        """
        Expands an internal node of the tree by setting <_expanded> to true
        >>> tree = TMTree("1", [], 20)
        >>> tree2 = TMTree("2", [tree], 30)
        >>> tree._parent_tree = tree2
        >>> tree2._expanded
        False
        >>> tree2.expand()
        >>> tree2._expanded
        True
        """
        if self._subtrees:
            self._expanded = True
        self.update_rectangles(self.rect)

    def expand_all(self) -> None:
        """
        Recursively goes through each subtree to expand itself,
        only if they are internal nodes
        >>> tree = TMTree("1", [], 20)
        >>> tree2 = TMTree("2", [tree], 30)
        >>> tree._parent_tree = tree2
        >>> tree3 = TMTree("3", [tree2], 40)
        >>> tree2._parent_tree = tree3
        >>> tree2._expanded
        False
        >>> tree3._expanded
        False
        >>> tree3.expand_all()
        >>> tree2._expanded
        True
        >>> tree3._expanded
        True
        """
        if self._subtrees:
            self.expand()
            for subtree in self._subtrees:
                subtree.expand_all()

    def collapse(self) -> None:
        """
        Collapses itself and all of its children if <self> has a parent
        >>> tree = TMTree("1", [], 20)
        >>> tree2 = TMTree("2", [tree], 30)
        >>> tree._parent_tree = tree2
        >>> tree3 = TMTree("3", [tree2], 40)
        >>> tree2._parent_tree = tree3
        >>> tree4 = TMTree("5", [], 30)
        >>> tree5 = TMTree("6", [tree4], 10)
        >>> tree_all = TMTree("7", [tree3, tree5], 70)
        >>> tree_all.expand_all()
        >>> tree2.collapse()
        >>> tree2._expanded
        False
        >>> tree5._expanded
        True
        """
        if self._parent_tree is not None:
            self._parent_tree._collapse_helper()

    def collapse_all(self) -> None:
        """
        Collapses every file and folder into one folder
        >>> tree = TMTree("1", [], 20)
        >>> tree2 = TMTree("2", [tree], 30)
        >>> tree._parent_tree = tree2
        >>> tree3 = TMTree("3", [tree2], 40)
        >>> tree2._parent_tree = tree3
        >>> tree4 = TMTree("5", [], 30)
        >>> tree5 = TMTree("6", [tree4], 10)
        >>> tree_all = TMTree("7", [tree3, tree5], 70)
        >>> tree_all.expand_all()
        >>> tree2.collapse_all()
        >>> tree2._expanded
        False
        >>> tree5._expanded
        False
        """
        if self._parent_tree is not None:
            self._parent_tree.collapse_all()
        else:
            # sets all of its children's _expanded to false
            self._collapse_all_helper()

    def _collapse_helper(self) -> None:
        if self._subtrees:
            self._expanded = False
            for subtree in self._subtrees:
                subtree._collapse_helper()
        self.update_rectangles(self.rect)

    def _collapse_all_helper(self) -> None:
        for subtree in self._subtrees:
            subtree._collapse_all_helper()
        self._collapse_helper()

    # Methods for the string representation
    def get_path_string(self) -> str:
        """
        Return a string representing the path containing this tree
        and its ancestors, using the separator for this OS between each
        tree's name.
        """
        if self._parent_tree is None:
            return self._name
        else:
            return self._parent_tree.get_path_string() + \
                   self.get_separator() + self._name

    def get_separator(self) -> str:
        """Return the string used to separate names in the string
        representation of a path from the tree root to this tree.
        """
        raise NotImplementedError

    def get_suffix(self) -> str:
        """Return the string used at the end of the string representation of
        a path from the tree root to this tree.
        """
        raise NotImplementedError


class FileSystemTree(TMTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _name attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/Diane/csc148/assignments'

    The data_size attribute for regular files is simply the size of the file,
    as reported by os.path.getsize.
    """

    def __init__(self, path: str) -> None:
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.
        >>> EXAMPLE_PATH = os.path.join(os.getcwd(), 'example-directory', 'workshop')
        >>> tree = FileSystemTree(EXAMPLE_PATH)
        >>> tree.update_rectangles((0, 0, 1, 1))
        >>> rects = tree.get_rectangles()
        >>> rects[0][0]
        (0, 0, 1, 1)
        """
        # Remember that you should recursively go through the file system
        # and create new FileSystemTree objects for each file and folder
        # encountered.
        #
        # Also remember to make good use of the superclass constructor!
        _name = os.path.basename(path)
        if os.path.isdir(path):  # folders
            size = 0
            subs = []
            for sub_path in os.listdir(path):
                subs.append(FileSystemTree(os.path.join(path, sub_path)))
            for sub in subs:
                size += sub.data_size
            TMTree.__init__(self, _name, subs, size)
        else:  # for file
            _data_size = os.path.getsize(path)
            TMTree.__init__(self, _name, [], _data_size)

    def get_separator(self) -> str:
        """Return the file separator for this OS.
        """
        return os.sep

    def get_suffix(self) -> str:
        """Return the final descriptor of this tree.
        """

        def convert_size(data_size: float, suffix: str = 'B') -> str:
            suffixes = {'B': 'kB', 'kB': 'MB', 'MB': 'GB', 'GB': 'TB'}
            if data_size < 1024 or suffix == 'TB':
                return f'{data_size:.2f}{suffix}'
            return convert_size(data_size / 1024, suffixes[suffix])

        components = []
        if len(self._subtrees) == 0:
            components.append('file')
        else:
            components.append('folder')
            components.append(f'{len(self._subtrees)} items')
        components.append(convert_size(self.data_size))
        return f' ({", ".join(components)})'


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'math', 'random', 'os', '__future__'
        ]
    })
