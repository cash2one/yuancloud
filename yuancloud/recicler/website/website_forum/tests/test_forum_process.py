import yuancloud.tests

@yuancloud.tests.common.at_install(False)
@yuancloud.tests.common.post_install(True)
class TestUi(yuancloud.tests.HttpCase):
    def test_01_admin_forum_tour(self):
        self.phantom_js("/", "yuancloud.__DEBUG__.services['web.Tour'].run('question', 'test')", "yuancloud.__DEBUG__.services['web.Tour'].tours.question", login="admin")

    def test_02_demo_question(self):
        self.phantom_js("/", "yuancloud.__DEBUG__.services['web.Tour'].run('forum_question', 'test')", "yuancloud.__DEBUG__.services['web.Tour'].tours.forum_question", login="demo")

