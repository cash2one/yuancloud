import yuancloud.tests

@yuancloud.tests.common.at_install(False)
@yuancloud.tests.common.post_install(True)
class TestUi(yuancloud.tests.HttpCase):
    def test_admin(self):
        self.phantom_js("/", "yuancloud.__DEBUG__.services['web.Tour'].run('blog', 'test')", "yuancloud.__DEBUG__.services['web.Tour'].tours.blog", login='admin')
