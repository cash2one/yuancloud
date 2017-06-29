import yuancloud.tests

@yuancloud.tests.common.at_install(False)
@yuancloud.tests.common.post_install(True)
class TestUi(yuancloud.tests.HttpCase):
    def test_01_admin_widget_x2many(self):
        self.phantom_js("/web#action=test_new_api.action_discussions",
                        "yuancloud.__DEBUG__.services['web.Tour'].run('widget_x2many', 'test')",
                        "yuancloud.__DEBUG__.services['web.Tour'].tours.widget_x2many",
                        login="admin")
