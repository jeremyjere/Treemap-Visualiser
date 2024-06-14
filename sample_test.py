import os

from hypothesis import given
from hypothesis.strategies import integers
from papers import PaperTree
from tm_trees import TMTree, FileSystemTree

# This should be the path to the "workshop" folder in the sample data.
# You may need to modify this, depending on where you downloaded and
# extracted the files.
EXAMPLE_PATH = os.path.join(os.getcwd(), 'example-directory', 'workshop')


def test_single_file() -> None:
    """Test a tree with a single file.
    """
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH, 'draft.pptx'))
    assert tree._name == 'draft.pptx'
    assert tree._subtrees == []
    assert tree._parent_tree is None
    assert tree.data_size == 58
    assert is_valid_colour(tree._colour)


def test_example_data() -> None:
    """Test the root of the tree at the 'workshop' folder in the example data
    """
    tree = FileSystemTree(EXAMPLE_PATH)
    assert tree._name == 'workshop'
    assert tree._parent_tree is None
    assert tree.data_size == 151
    assert is_valid_colour(tree._colour)

    assert len(tree._subtrees) == 3
    for subtree in tree._subtrees:
        # Note the use of is rather than ==.
        # This checks ids rather than values.
        assert subtree._parent_tree is tree


@given(integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000))
def test_single_file_rectangles(x, y, width, height) -> None:
    """Test that the correct rectangle is produced for a single file."""
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH, 'draft.pptx'))
    tree.update_rectangles((x, y, width, height))
    rects = tree.get_rectangles()

    # This should be just a single rectangle and colour returned.
    assert len(rects) == 1
    rect, colour = rects[0]
    assert rect == (x, y, width, height)
    assert is_valid_colour(colour)


def test_example_data_rectangles() -> None:
    """This test sorts the subtrees, because different operating systems have
    different behaviours with os.listdir.

    You should *NOT* do any sorting in your own code
    """
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree.expand_all()
    tree.update_rectangles((0, 0, 200, 100))
    rects = tree.get_rectangles()

    # IMPORTANT: This test should pass when you have completed Task 2, but
    # will fail once you have completed Task 5.
    # You should edit it as you make progress through the tasks,
    # and add further tests for the later task functionality.
    assert len(rects) == 6

    # UPDATED:
    # Here, we illustrate the correct order of the returned rectangles.
    # Note that this corresponds to the folder contents always being
    # sorted in alphabetical order. This is enforced in these sample tests
    # only so that you can run them on your own computer, rather than on
    # the Teaching Labs.
    actual_rects = [r[0] for r in rects]
    expected_rects = [(0, 0, 94, 2), (0, 2, 94, 28), (0, 30, 94, 70),
                      (94, 0, 76, 100), (170, 0, 30, 72), (170, 72, 30, 28)]

    assert len(actual_rects) == len(expected_rects)


def test_first_file():
    tree = FileSystemTree(EXAMPLE_PATH)
    assert tree.rect == (0, 0, 0, 0)
    assert tree._name == "workshop"
    assert tree._parent_tree is None


def test_two_subs() -> None:
    """Test a tree with two subtrees.
    """
    subtree = TMTree("left1", [], 700)
    subtree2 = TMTree('right1', [], 10)
    tree = TMTree("root", [subtree, subtree2])
    assert tree._name == 'root'
    assert tree._subtrees == [subtree, subtree2]
    assert tree._parent_tree is None
    assert tree.data_size == 710

    tree.expand()
    tree.update_rectangles((0, 0, 2000, 2000))
    rects = tree.get_rectangles()
    assert len(tree._subtrees) == 2
    assert len(rects) == 2
    assert rects[0][0] == (0, 0, 2000, 1971)
    assert rects[1][0] == (0, 1971, 2000, 29)
    assert is_valid_colour(rects[0][1])
    assert is_valid_colour(rects[1][1])


def test_nested_subs() -> None:
    nested2 = TMTree("left3", [], 10)
    nested1 = TMTree("left2", [nested2], 10)
    nested3 = TMTree("left2", [], 20)
    subtree = TMTree("left1", [nested1, nested3], 30)
    subtree2 = TMTree('right1', [], 50)
    tree = TMTree("root", [subtree, subtree2])
    assert tree._name == 'root'
    assert tree._subtrees == [subtree, subtree2]
    assert tree._parent_tree is None
    assert tree.data_size == 80

    tree.expand()
    tree.update_rectangles((0, 0, 1000, 100))
    rects = tree.get_rectangles()
    assert len(tree._subtrees) == 2
    assert len(rects) == 2
    assert rects[0][0] == (0, 0, 375, 100)
    assert rects[1][0] == (375, 0, 625, 100)
    assert is_valid_colour(rects[0][1])
    assert is_valid_colour(rects[1][1])


def test_empty_file() -> None:
    tree = TMTree(None, [])
    assert tree._name is None
    assert tree._subtrees == []
    assert tree._parent_tree is None
    assert tree.data_size == 0

    tree.expand()
    tree.update_rectangles((0, 0, 1000, 100))
    rects = tree.get_rectangles()
    assert len(tree._subtrees) == 0
    assert len(rects) == 0


def test_parent_subs() -> None:
    nested2 = TMTree("left3", [], 10)
    nested1 = TMTree("left2", [nested2], 10)
    nested3 = TMTree("left2", [], 20)
    subtree = TMTree("left1", [nested1, nested3], 30)
    subtree2 = TMTree('right1', [], 50)
    tree = TMTree("root", [subtree, subtree2])
    assert nested2.get_parent() == nested1
    assert nested1.get_parent() == subtree
    assert nested3.get_parent() == subtree
    assert subtree.get_parent() == tree
    assert tree.get_parent() is None


def test_papers() -> None:
    tree1 = PaperTree('CS1', [], all_papers=True, by_year=True)
    tree2 = PaperTree('CS1', [], all_papers=True, by_year=False)
    tree3 = PaperTree('CS1', [], all_papers=False, by_year=True)
    tree1.expand_all()
    tree2.expand_all()
    tree3.expand_all()
    rects1 = tree1.get_rectangles()
    rects2 = tree2.get_rectangles()
    rects3 = tree3.get_rectangles()
    assert len(rects1) == 428
    assert len(rects2) == 428
    assert len(rects3) == 0


def test_expand() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree.expand()
    tree.update_rectangles((0, 0, 1500, 900))
    rects = tree.get_rectangles()
    assert len(rects) == 3
    assert rects[0][0] == (0, 0, 705, 900)
    assert rects[1][0] == (705, 0, 576, 900)
    assert rects[2][0] == (1281, 0, 219, 900)
    for rect in rects:
        assert is_valid_colour(rect[1])


def test_expand_paper() -> None:
    tree = PaperTree('CS1', [], all_papers=True, by_year=True)
    _sort_subtrees(tree)
    tree.expand()
    tree.update_rectangles((0, 0, 1500, 900))
    rects = tree.get_rectangles()
    assert len(rects) == 45
    assert rects[0][0] == (0, 0, 3, 900)
    assert rects[1][0] == (3, 0, 11, 900)
    assert rects[2][0] == (14, 0, 0, 900)
    for rect in rects:
        assert is_valid_colour(rect[1])


def test_expand_empty() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree.expand()
    tree.update_rectangles((0, 0, 0, 0))
    rects = tree.get_rectangles()
    assert len(rects) == 3
    assert rects[0][0] == (0, 0, 0, 0)
    assert rects[1][0] == (0, 0, 0, 0)
    assert rects[2][0] == (0, 0, 0, 0)
    for rect in rects:
        assert is_valid_colour(rect[1])


def test_expand_negative() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree.expand()
    tree.update_rectangles((0, 0, -1500, -900))
    rects = tree.get_rectangles()
    assert rects[0][0] == (0, 0, -1500, -423)
    assert rects[1][0] == (0, -423, -1500, -345)
    assert rects[2][0] == (0, -768, -1500, -132)
    for rect in rects:
        assert is_valid_colour(rect[1])


def test_expand_all() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree.expand_all()
    tree.update_rectangles((0, 0, 1500, 900))
    rects = tree.get_rectangles()
    assert rects[0][0] == (0, 0, 705, 25)
    assert rects[1][0] == (0, 25, 705, 253)
    assert rects[2][0] == (0, 278, 705, 622)
    assert rects[3][0] == (705, 0, 576, 900)
    assert rects[4][0] == (1281, 0, 219, 654)
    assert rects[5][0] == (1281, 654, 219, 246)
    assert len(rects) == 6
    for rect in rects:
        assert is_valid_colour(rect[1])


def test_expand_all_paper() -> None:
    tree = PaperTree('CS1', [], all_papers=True, by_year=True)
    _sort_subtrees(tree)
    tree.expand_all()
    tree.update_rectangles((0, 0, 1500, 900))
    rects = tree.get_rectangles()
    assert len(rects) == 428
    assert rects[0][0] == (0, 0, 3, 490)
    assert rects[1][0] == (0, 490, 3, 163)
    assert rects[2][0] == (0, 653, 3, 247)
    for rect in rects:
        assert is_valid_colour(rect[1])


def test_expand_all_empty() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree.expand_all()
    tree.update_rectangles((0, 0, 0, 0))
    rects = tree.get_rectangles()
    assert rects[0][0] == (0, 0, 0, 0)
    assert rects[1][0] == (0, 0, 0, 0)
    assert rects[2][0] == (0, 0, 0, 0)
    assert rects[3][0] == (0, 0, 0, 0)
    assert rects[4][0] == (0, 0, 0, 0)
    assert rects[5][0] == (0, 0, 0, 0)
    assert len(rects) == 6
    for rect in rects:
        assert is_valid_colour(rect[1])


def test_expand_all_negative() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree.expand_all()
    tree.update_rectangles((0, 0, -1500, -900))
    rects = tree.get_rectangles()
    assert rects[0][0] == (0, 0, -1500, -11)
    assert rects[1][0] == (0, -11, -1500, -119)
    assert rects[2][0] == (0, -130, -1500, -293)
    assert rects[3][0] == (0, -423, -1500, -345)
    assert rects[4][0] == (0, -768, -1500, -96)
    assert rects[5][0] == (0, -864, -1500, -36)
    assert len(rects) == 6
    for rect in rects:
        assert is_valid_colour(rect[1])


def test_collapse() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree.expand_all()
    tree.update_rectangles((0, 0, 1500, 900))
    tree.collapse()
    rects = tree.get_rectangles()
    assert rects[0][0] == (0, 0, 705, 25)
    assert rects[1][0] == (0, 25, 705, 253)
    assert rects[2][0] == (0, 278, 705, 622)
    assert rects[3][0] == (705, 0, 576, 900)
    assert rects[4][0] == (1281, 0, 219, 654)
    assert rects[5][0] == (1281, 654, 219, 246)
    assert len(rects) == 6
    for rect in rects:
        assert is_valid_colour(rect[1])


def test_collapse_paper() -> None:
    tree = PaperTree('CS1', [], all_papers=True, by_year=True)
    _sort_subtrees(tree)
    tree.expand_all()
    tree.update_rectangles((0, 0, 1500, 900))
    tree.collapse()
    rects = tree.get_rectangles()
    assert len(rects) == 428
    assert rects[0][0] == (0, 0, 3, 490)
    assert rects[1][0] == (0, 490, 3, 163)
    assert rects[2][0] == (0, 653, 3, 247)
    for rect in rects:
        assert is_valid_colour(rect[1])


def test_collapse_empty() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree.expand_all()
    tree.update_rectangles((0, 0, 0, 0))
    tree.collapse()
    rects = tree.get_rectangles()
    assert rects[0][0] == (0, 0, 0, 0)
    assert rects[1][0] == (0, 0, 0, 0)
    assert rects[2][0] == (0, 0, 0, 0)
    assert rects[3][0] == (0, 0, 0, 0)
    assert rects[4][0] == (0, 0, 0, 0)
    assert rects[5][0] == (0, 0, 0, 0)
    assert len(rects) == 6
    for rect in rects:
        assert is_valid_colour(rect[1])


def test_collapse_negative() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree.expand_all()
    tree.update_rectangles((0, 0, -1500, -900))
    tree.collapse()
    rects = tree.get_rectangles()
    assert rects[0][0] == (0, 0, -1500, -11)
    assert rects[1][0] == (0, -11, -1500, -119)
    assert rects[2][0] == (0, -130, -1500, -293)
    assert rects[3][0] == (0, -423, -1500, -345)
    assert rects[4][0] == (0, -768, -1500, -96)
    assert rects[5][0] == (0, -864, -1500, -36)
    assert len(rects) == 6
    for rect in rects:
        assert is_valid_colour(rect[1])


def test_collapse_all() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree.expand_all()
    tree.update_rectangles((0, 0, 1500, 900))
    tree.collapse_all()
    rects = tree.get_rectangles()
    assert rects[0][0] == (0, 0, 1500, 900)
    assert len(rects) == 1
    assert is_valid_colour(rects[0][1])


def test_collapse_all_paper() -> None:
    tree = PaperTree('CS1', [], all_papers=True, by_year=True)
    _sort_subtrees(tree)
    tree.expand_all()
    tree.update_rectangles((0, 0, 1500, 900))
    tree.collapse_all()
    rects = tree.get_rectangles()
    assert rects[0][0] == (0, 0, 1500, 900)
    assert len(rects) == 1
    assert is_valid_colour(rects[0][1])


def test_collapse_all_empty() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree.expand_all()
    tree.update_rectangles((0, 0, 0, 0))
    tree.collapse_all()
    rects = tree.get_rectangles()
    assert rects[0][0] == (0, 0, 0, 0)
    assert len(rects) == 1
    assert is_valid_colour(rects[0][1])


def test_collapse_all_negative() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree.expand_all()
    tree.update_rectangles((0, 0, -1500, -900))
    tree.collapse_all()
    rects = tree.get_rectangles()
    assert rects[0][0] == (0, 0, -1500, -900)
    assert len(rects) == 1


def test_off_vis() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree.expand_all()
    tree.update_rectangles((50, 75, 1800, 1796))
    rects = tree.get_rectangles()
    assert len(rects) == 6
    assert rects[0][0] == (50, 75, 846, 50)
    assert rects[1][0] == (50, 125, 846, 506)
    assert rects[2][0] == (50, 631, 846, 1240)
    assert rects[3][0] == (896, 75, 691, 1796)
    assert rects[4][0] == (1587, 75, 263, 1306)
    assert rects[5][0] == (1587, 1381, 263, 490)
    for rect in rects:
        assert is_valid_colour(rect[1])


def test_off_vis_paper() -> None:
    tree = PaperTree('CS1', [], all_papers=True, by_year=True)
    _sort_subtrees(tree)
    tree.expand_all()
    tree.update_rectangles((50, 75, 1800, 1796))
    rects = tree.get_rectangles()
    assert len(rects) == 428
    assert rects[0][0] == (50, 75, 3, 979)
    assert rects[1][0] == (50, 1054, 3, 326)
    assert rects[2][0] == (50, 1380, 3, 491)
    for rect in rects:
        assert is_valid_colour(rect[1])


def test_zero_vis() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree.expand_all()
    tree.update_rectangles((0, 0, 0, 0))
    rects = tree.get_rectangles()
    for rect in rects:
        assert rect[0] == (0, 0, 0, 0)
        assert is_valid_colour(rect[1])
    assert len(rects) == 6


def test_one_vis() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree.expand_all()
    tree.update_rectangles((0, 0, 1, 1))
    rects = tree.get_rectangles()
    assert len(rects) == 6
    assert rects[0][0] == (0, 0, 0, 0)
    assert rects[1][0] == (0, 0, 0, 0)
    assert rects[2][0] == (0, 0, 1, 0)
    assert rects[3][0] == (0, 0, 1, 0)
    assert rects[4][0] == (0, 0, 1, 0)
    assert rects[5][0] == (0, 0, 1, 1)
    for rect in rects:
        assert is_valid_colour(rect[1])


def test_one_vis_paper() -> None:
    tree = PaperTree('CS1', [], all_papers=True, by_year=True)
    _sort_subtrees(tree)
    tree.expand_all()
    tree.update_rectangles((0, 0, 1, 1))
    rects = tree.get_rectangles()
    assert len(rects) == 428
    assert rects[0][0] == (0, 0, 0, 0)
    assert rects[1][0] == (0, 0, 0, 0)
    assert rects[2][0] == (0, 0, 1, 0)
    for rect in rects:
        assert is_valid_colour(rect[1])


def test_large_vis() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree.expand_all()
    tree.update_rectangles((0, 0, 9999999999, 9999999999))
    rects = tree.get_rectangles()
    assert len(rects) == 6
    assert rects[0][0] == (0, 0, 281690140, 4701986754)
    assert rects[1][0] == (281690140, 0, 2816901408, 4701986754)
    assert rects[2][0] == (3098591548, 0, 6901408451, 4701986754)
    assert rects[3][0] == (0, 4701986754, 9999999999, 3841059602)
    assert rects[4][0] == (0, 8543046356, 7272727272, 1456953643)
    assert rects[5][0] == (7272727272, 8543046356, 2727272727, 1456953643)
    for rect in rects:
        assert is_valid_colour(rect[1])


def test_get_tree_at_position() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree.update_rectangles((0, 0, 555, 1250))
    tree.expand_all()
    assert len(tree.get_rectangles()) == 6
    loc = tree.get_tree_at_position((0, 1))
    assert loc._name == 'Plan.tex'
    loc.collapse()
    loc = tree.get_tree_at_position((0, 1000))
    assert loc._name == "draft.pptx"
    loc.collapse()
    loc = tree.get_tree_at_position((556, 0))
    assert not loc
    loc = tree.get_tree_at_position((555, 0))
    assert loc._name == "workshop"
    loc.collapse()
    loc = tree.get_tree_at_position((0, 1250))
    assert loc._name == "workshop"
    loc = tree.get_tree_at_position((0, 1251))
    assert not loc


def test_get_tree_at_position_paper() -> None:
    tree = PaperTree('CS1', [], all_papers=True, by_year=True)
    _sort_subtrees(tree)
    tree.update_rectangles((0, 0, 555, 1250))
    tree.expand_all()
    assert len(tree.get_rectangles()) == 428
    loc = tree.get_tree_at_position((0, 1))
    assert loc._name == 'Separation of Introductory Programming' \
                        ' and Language Instruction'
    loc.collapse()
    loc = tree.get_tree_at_position((0, 1000))
    assert loc._name == 'Investigating the Effective Implementation of Pair ' \
                        'Programming: An Empirical Investigation'
    loc.collapse()
    loc = tree.get_tree_at_position((556, 0))
    assert not loc
    loc = tree.get_tree_at_position((555, 0))
    assert loc._name == 'Introductory Programming at Cornell'
    loc.collapse()
    loc = tree.get_tree_at_position((0, 1250))
    assert loc._name == 'Fix the First, Ignore the Rest: ' \
                        'Dealing with Multiple Compiler Error Messages'
    loc = tree.get_tree_at_position((0, 1251))
    assert not loc


def test_no_vis_get_tree() -> None:
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH, 'draft.pptx'))
    tree.data_size = 0
    tree.update_data_sizes()
    tree.update_rectangles((0, 0, 0, 0))
    assert tree.rect == (0, 0, 0, 0)
    loc = tree.get_tree_at_position((1, 1))
    assert not loc


def test_no_vis_get_tree_paper() -> None:
    tree = PaperTree('CS1', [], all_papers=True, by_year=True)
    tree.data_size = 0
    tree.update_data_sizes()
    tree.update_rectangles((0, 0, 0, 0))
    assert tree.rect == (0, 0, 0, 0)
    loc = tree.get_tree_at_position((1, 1))
    assert not loc


def test_delete_self() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree._subtrees[0].delete_self()
    assert len(tree._subtrees) == 2
    assert tree.data_size == 80
    tree._subtrees[0].delete_self()
    assert len(tree._subtrees) == 1
    assert tree.data_size == 22
    tree.delete_self()
    assert tree.data_size == 22
    tree._subtrees[0]._subtrees[1].delete_self()
    assert tree.data_size == 16
    tree._subtrees[0].delete_self()
    assert tree.data_size == 0
    tree.update_rectangles(tree.rect)
    assert tree.rect == (0, 0, 0, 0)


def test_delete_self_paper() -> None:
    tree = PaperTree('CS1', [], all_papers=True, by_year=True)
    _sort_subtrees(tree)
    tree._subtrees[0].delete_self()
    assert len(tree._subtrees) == 44
    assert tree.data_size == 5037
    tree._subtrees[0].delete_self()
    assert len(tree._subtrees) == 43
    assert tree.data_size == 4997
    tree.delete_self()
    assert tree.data_size == 4997


def test_move() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree._subtrees[0].move(tree._subtrees[1])
    assert len(tree._subtrees) == 3
    assert tree.data_size == 151
    assert tree._subtrees[0].data_size == 71
    assert len(tree._subtrees[1]._subtrees) == 0
    assert len(tree._subtrees[0]._subtrees) == 2
    tree._subtrees[0]._subtrees[0].move(tree._subtrees[0])
    assert tree._subtrees[1].data_size == 58
    assert tree._subtrees[0].data_size == 71
    assert len(tree._subtrees[0]._subtrees) == 2


def test_move_paper() -> None:
    tree = PaperTree('CS1', [], all_papers=True, by_year=True)
    _sort_subtrees(tree)
    tree._subtrees[0].move(tree._subtrees[1])
    assert len(tree._subtrees) == 45
    assert tree.data_size == 5048
    assert tree._subtrees[0].data_size == 11
    assert len(tree._subtrees[1]._subtrees) == 3
    assert len(tree._subtrees[0]._subtrees) == 3
    tree._subtrees[0]._subtrees[0].move(tree._subtrees[0])
    assert tree._subtrees[1].data_size == 40
    assert tree._subtrees[0].data_size == 11
    assert len(tree._subtrees[0]._subtrees) == 3


def test_destination_parent_move() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree._subtrees[1].move(tree)
    assert len(tree._subtrees[2]._subtrees) == 0
    assert tree._subtrees[1].data_size == 22
    tree.expand()
    tree.update_rectangles((0, 0, 9998, 950))
    rects = tree.get_rectangles()

    assert len(rects) == 3
    assert tree._subtrees[0].data_size == 71
    assert rects[0][0] == (0, 0, 4701, 950)
    assert rects[1][0] == (4701, 0, 1456, 950)
    assert rects[2][0] == (6157, 0, 3841, 950)


def test_destination_parent_move_paper() -> None:
    tree = PaperTree('CS1', [], all_papers=True, by_year=True)
    _sort_subtrees(tree)
    tree._subtrees[1].move(tree)
    assert len(tree._subtrees[2]._subtrees) == 1
    assert tree._subtrees[1].data_size == 40
    tree.expand()
    tree.update_rectangles((0, 0, 9998, 950))
    rects = tree.get_rectangles()

    assert len(rects) == 45
    assert tree._subtrees[0].data_size == 11
    assert rects[0][0] == (0, 0, 21, 950)
    assert rects[1][0] == (21, 0, 79, 950)
    assert rects[2][0] == (100, 0, 3, 950)


def test_change_size() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)
    tree._subtrees[0].change_size(0.01)
    assert tree._subtrees[0].data_size == 71
    tree._subtrees[1].change_size(0.01)
    assert tree._subtrees[1].data_size == 59
    tree._subtrees[1].change_size(-0.01)
    assert tree._subtrees[1].data_size == 58
    assert tree.data_size == 151
    tree._subtrees[2]._subtrees[0]._subtrees[0].change_size(0.01)
    assert tree._subtrees[2]._subtrees[0]._subtrees[0].data_size == 17
    assert tree._subtrees[2].data_size == 23
    tree._subtrees[2]._subtrees[0]._subtrees[0].change_size(-0.01)
    assert tree._subtrees[2]._subtrees[0]._subtrees[0].data_size == 16
    tree._subtrees[2]._subtrees[0]._subtrees[0].change_size(-0.01)
    assert tree._subtrees[2]._subtrees[0].data_size == 15


def test_change_size_paper() -> None:
    tree = PaperTree('CS1', [], all_papers=True, by_year=True)
    _sort_subtrees(tree)
    tree._subtrees[0].change_size(0.01)
    assert tree._subtrees[0].data_size == 11
    tree._subtrees[1].change_size(0.01)
    assert tree._subtrees[1].data_size == 40
    tree._subtrees[1].change_size(-0.01)
    assert tree._subtrees[1].data_size == 40
    assert tree.data_size == 5048
    tree._subtrees[2]._subtrees[0]._subtrees[0].change_size(0.01)
    assert tree._subtrees[2]._subtrees[0]._subtrees[0].data_size == 2
    assert tree._subtrees[2].data_size == 2
    tree._subtrees[2]._subtrees[0]._subtrees[0].change_size(-0.01)
    assert tree._subtrees[2]._subtrees[0]._subtrees[0].data_size == 2
    tree._subtrees[2]._subtrees[0]._subtrees[0].change_size(-0.01)
    assert tree._subtrees[2]._subtrees[0].data_size == 2


@given(integers(min_value=-1000, max_value=-950))
def test_change_size_low(x: int) -> None:
    tree = TMTree("1", [], 5)
    tree.change_size(x)
    assert tree.data_size == 1


##############################################################################
# Helpers
##############################################################################


def is_valid_colour(colour: tuple[int, int, int]) -> bool:
    """Return True iff <colour> is a valid colour. That is, if all of its
    values are between 0 and 255, inclusive.
    """
    for i in range(3):
        if not 0 <= colour[i] <= 255:
            return False
    return True


def _sort_subtrees(tree: TMTree) -> None:
    """Sort the subtrees of <tree> in alphabetical order.
    THIS IS FOR THE PURPOSES OF THE SAMPLE TEST ONLY; YOU SHOULD NOT SORT
    YOUR SUBTREES IN THIS WAY. This allows the sample test to run on different
    operating systems.

    This is recursive, and affects all levels of the tree.
    """
    if not tree.is_empty():
        for subtree in tree._subtrees:
            _sort_subtrees(subtree)

        tree._subtrees.sort(key=lambda t: t._name)


if __name__ == '__main__':
    import pytest

    pytest.main(['a2_sample_test.py'])
