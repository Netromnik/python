from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import WikiArticleModel,WikiPermModel
from base.models import CustomGroup as Group

User = get_user_model()
# Create your tests here.

class AlWikiTest(TestCase):
    def _create_row(self):
        u = User(username="test-f", password="123")
        u.save()
        obj = WikiArticleModel(title="root-f",
                               slug="root_f",
                               content="content-root",
                               author=u,
                               )
        WikiArticleModel.node_manager.create_root(obj)
        self.root = obj
        self.list_model_not_save = [
            WikiArticleModel(title=f"sub_root-f{i}",
                             slug=f"sub_root_f{i}",
                             content="sub_contents-root",
                             author=u,
                             ) for i in range(200)]
        obj = WikiArticleModel(title="root-l",
                               slug="root_l",
                               content="content-root",
                               author=u,
                               )
        WikiArticleModel.node_manager.create_root(obj)

    def setUp(self) -> None:
        self._create_row()

    def test_save(self):
        """
        test save children in root
        :return:
        """
        root = WikiArticleModel.node_manager.get_roots()[0]
        [root.add_children(x) for x in self.list_model_not_save]
        self.assertEqual(root.get_children().count(),200,msg=["list", len(self.list_model_not_save), "children", root.get_children().count(),
                  "bd", WikiArticleModel.node_manager.filter(level=1).count()])

    def test_save_perent(self):
        root = WikiArticleModel.node_manager.get_roots()[0]
        mod = self.list_model_not_save[0:2]
        root.add_children(mod[0])
        mod[0].add_children(mod[1])
        self.assertEqual(root.id, mod[0].parent_id)
        self.assertEqual(mod[0].id, mod[1].parent_id)
        self.assertEqual(None, root.parent_id)

        mod[0].add_children(mod[0])
        self.assertEqual(mod[0].id, mod[0].parent_id)

    def test_get_simple(self):
        root = WikiArticleModel.node_manager.get_roots()[0]
        mod = self.list_model_not_save[0:2]
        root.add_children(mod[0])
        mod[0].add_children(mod[1])

        self.assertEqual(root.id, mod[0].get_parent().id)
        self.assertEqual(mod[0].id, mod[1].get_parent().id)
        self.assertEqual(root.id, root.get_parent().id)

        self.assertEqual(root, root.get_root())
        self.assertEqual(root, mod[0].get_root())
        self.assertEqual(root, mod[1].get_root())

        self.assertEqual(WikiArticleModel.node_manager.filter(level=1).count(), root.get_children().count())

    def test_get_multi(self):
        root, other_root = WikiArticleModel.node_manager.get_roots()[0:2]
        mod = self.list_model_not_save[0:2]
        other_mod = self.list_model_not_save[2:20]
        [other_root.add_children(i) for i in other_mod]
        root.add_children(mod[0])
        root.add_children(mod[0])
        mod[0].add_children(mod[1])

        self.assertEqual(root.id, mod[0].get_parent().id)
        self.assertEqual(mod[0].id, mod[1].get_parent().id)
        self.assertEqual(root.id, root.get_parent().id)

        self.assertEqual(root, root.get_root())
        self.assertEqual(root, mod[0].get_root())
        self.assertEqual(root, mod[1].get_root())

        self.assertEqual(WikiArticleModel.node_manager.filter(level=1, parent=root).count(),
                         root.get_children().count())
        self.assertEqual(WikiArticleModel.node_manager.filter(level=2).count(), mod[0].get_children().count())

    def test_path(self):
        path = "1:3"
        root = WikiArticleModel.node_manager.get_roots()[0]
        mod = self.list_model_not_save[0:2]
        root.add_children(mod[0])
        mod[0].add_children(mod[1])
        self.assertEqual(path, mod[1].path, "path not work ;(")

    def test_move_node(self):
        root, other_root = WikiArticleModel.node_manager.get_roots()[0:2]
        mod = self.list_model_not_save[0:2]
        other_mod = self.list_model_not_save[2:20]
        [other_root.add_children(i) for i in other_mod]
        root.add_children(mod[0])
        root.add_children(mod[0])
        mod[0].add_children(mod[1])

        self.assertEqual(root.id, mod[0].parent_id)

        try:
            WikiArticleModel.node_manager.mv(mod[0], other_root)
        except ValueError:
            pass

        self.assertEqual(root.id, mod[0].parent_id)

        self.assertEqual(mod[0].id, mod[1].parent_id)

        WikiArticleModel.node_manager.mv(mod[1], other_root)

        self.assertNotEqual(mod[0].id, mod[1].parent_id)
        self.assertEqual(other_root.id, mod[1].parent_id)

class TestWikiPerm(TestCase):
    def _create_row(self):
        self.g = Group(name="test-g")
        self.g.save()
        self.user_not_save = User(username="test-f", password="123")
        self.user_save = User(username="test-f", password="123")
        self.user_save.save()
        obj = [WikiArticleModel(title=f"root-f{i}",
                               slug="root_f",
                               content="content-root",
                               author=self.user_save,
                               ) for i in range(10)]

        self.list_sub = [WikiArticleModel(title=f"sub-f{i}",
                               slug="root_f",
                               content="content-root",
                               author=self.user_save,
                               ) for i in range(100)]
        [ WikiArticleModel.node_manager.create_root(i) for i in obj]
        self.roots = obj

    def setUp(self) -> None:
        self._create_row()

    def test_save(self):
        root = self.roots[0]
        other_root = self.roots[1]
        WikiPermModel.manager_perm.add_perm(root,group=self.g)
        WikiPermModel.manager_perm.add_perm(other_root,group=self.g)

    def test_delete(self):
        root = self.roots[0]
        other_root = self.roots[1]
        WikiPermModel.manager_perm.add_perm(root, group=self.g)
        WikiPermModel.manager_perm.add_perm(other_root,group=self.g)
        WikiPermModel.manager_perm.dell_all_perm_group(self.g)
        self.assertEqual( WikiPermModel.manager_perm.all().count(),0)

    def test_get_perm_root(self):
        root = self.roots[0]
        other_root = self.roots[1]
        WikiPermModel.manager_perm.add_perm(root,group=self.g)


        self.assertEqual(WikiPermModel.manager_perm.get_perm_node(root),True)
        self.assertEqual(WikiPermModel.manager_perm.get_perm_node(other_root),False)

        WikiPermModel.manager_perm.dell_all_perm_group(self.g)

        self.assertNotEqual(WikiPermModel.manager_perm.get_perm_node(root), True)

    def test_get_perm_sub(self):
        root = self.roots[0]
        other_root = self.roots[1]
        WikiPermModel.manager_perm.add_perm(root,group=self.g)
        sub,subsub = self.list_sub[0:2]
        root.add_children(sub)
        sub.add_children(subsub)

        osub, osubsub = self.list_sub[2:4]
        other_root.add_children(osub)
        osub.add_children(osubsub)

        self.assertEqual(WikiPermModel.manager_perm.get_perm_node(sub),True)
        self.assertEqual(WikiPermModel.manager_perm.get_perm_node(subsub),True)

        self.assertEqual(WikiPermModel.manager_perm.get_perm_node(osub),False)
        self.assertEqual(WikiPermModel.manager_perm.get_perm_node(osubsub),False)

        WikiPermModel.manager_perm.dell_all_perm_group(self.g)

        self.assertNotEqual(WikiPermModel.manager_perm.get_perm_node(sub), True)
        self.assertNotEqual(WikiPermModel.manager_perm.get_perm_node(subsub), True)