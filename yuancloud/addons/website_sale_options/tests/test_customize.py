import yuancloud.tests

@yuancloud.tests.common.at_install(False)
@yuancloud.tests.common.post_install(True)
class TestUi(yuancloud.tests.HttpCase):
    def test_01_admin_shop_customize_tour(self):
        self.phantom_js("/", "yuancloud.__DEBUG__.services['web.Tour'].run('shop_customize', 'test')", "yuancloud.__DEBUG__.services['web.Tour'].tours.shop_customize", login="admin")
