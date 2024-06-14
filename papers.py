import csv
from typing import List, Dict
from tm_trees import TMTree

# Filename for the dataset
DATA_FILE = 'cs1_papers.csv'


class PaperTree(TMTree):
    """A tree representation of Computer Science Education research paper data.

    === Private Attributes ===
    These should store information about this paper's <authors> and <doi>.

    === Inherited Attributes ===
    rect:
        The pygame rectangle representing this node in the treemap
        visualization.
    data_size:
        The size of the data represented by this tree.
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
    - All TMTree RIs are inherited.
    """

    name: str
    subtrees: List[TMTree]
    authors: str
    doi: str
    citations: int

    def __init__(self, name: str, subtrees: List[TMTree], authors: str = '',
                 doi: str = '', citations: int = 0, by_year: bool = True,
                 all_papers: bool = False) -> None:
        """Initialize a new PaperTree with the given <name> and <subtrees>,
        <authors> and <doi>, and with <citations> as the size of the data.

        If <all_papers> is True, then this tree is to be the root of the paper
        tree. In that case, load data about papers from DATA_FILE to build the
        tree.

        If <all_papers> is False, Do NOT load new data.

        <by_year> indicates whether or not the first level of subtrees should be
        the years, followed by each category, subcategory, and so on. If
        <by_year> is False, then the year in the dataset is simply ignored.
        """
        if all_papers:
            subtrees = _build_tree_from_dict(
                ([], _load_papers_to_dict(by_year)))

        TMTree.__init__(self, name, subtrees, citations)
        self.authors = authors
        self.doi = doi

    def get_separator(self) -> str:
        """
        Return the string used to separate names in the string
        representation of a path from the tree root to this tree.
        """
        return "/"

    def get_suffix(self) -> str:
        """
        Return the string used at the end of the string representation of
        a path from the tree root to this tree.
        """
        components = []
        if len(self._subtrees) == 0:
            components.append('file')
        else:
            components.append('category')
            components.append(f'{len(self._subtrees)} items')
        components.append(f'{self.data_size} citations')
        return f' ({", ".join(components)})'


def _build_tree_from_dict(subtrees: tuple[list, dict]) -> list[PaperTree]:
    tree = []
    for leaf in subtrees[0]:
        authors, title, url, citations = leaf
        tree.append(
            PaperTree(title, [], authors, url, int(citations), False, False))
    for key in subtrees[1]:
        subs = _build_tree_from_dict(subtrees[1][key])
        tree.append(PaperTree(key, subs, '', '', 0, False, False))
    return tree


def _load_papers_to_dict(by_year: bool = True) -> Dict:
    """Return a nested dictionary of the data read from the papers dataset file.

    If <by_year>, then use years as the roots of the subtrees of the root of
    the whole tree. Otherwise, ignore years and use categories only.
    """

    def _load_papers_helper(diction: dict[str, tuple], lst: list[str]) -> None:
        if len(lst) >= 2:
            diction.setdefault(lst[0], ([], {}))
            if len(lst) > 2:
                _load_papers_helper(diction[lst[0]][1], lst[1:])
            else:
                diction[lst[0]][0].append(lst[1])

    dic = {}
    with open(DATA_FILE, newline="") as file:
        file.readline()
        rows = csv.reader(file)  # a nested list containing lists of each line
        for line in rows:
            author, title, year, categories, url, cite = line
            categories = categories.split(": ")
            if by_year:
                _load_papers_helper(dic, [year] + categories + [
                    (author, title, url, cite)])
            else:
                _load_papers_helper(dic, categories + [
                    (author, title, url, cite)])
    return dic


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': ['python_ta', 'typing', 'csv', 'tm_trees'],
        'allowed-io': ['_load_papers_to_dict'],
        'max-args': 8
    })
