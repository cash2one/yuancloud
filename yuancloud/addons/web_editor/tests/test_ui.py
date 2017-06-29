import yuancloud.tests


class TestUi(yuancloud.tests.HttpCase):
    def test_01_admin_rte(self):
        self.phantom_js("/web", "yuancloud.__DEBUG__.services['web.Tour'].run('rte', 'test')", "yuancloud.__DEBUG__.services['web.Tour'].tours.rte", login='admin')

    def test_02_admin_rte_inline(self):
        self.phantom_js("/web", "yuancloud.__DEBUG__.services['web.Tour'].run('rte_inline', 'test')", "yuancloud.__DEBUG__.services['web.Tour'].tours.rte", login='admin')
