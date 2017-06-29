import yuancloud.tests

@yuancloud.tests.common.at_install(False)
@yuancloud.tests.common.post_install(True)
class TestUi(yuancloud.tests.HttpCase):
    def test_admin(self):
        self.phantom_js("/", "yuancloud.__DEBUG__.services['web.Tour'].run('event_buy_tickets', 'test')", "yuancloud.__DEBUG__.services['web.Tour'].tours.event_buy_tickets", login="admin")

    def test_demo(self):
        self.phantom_js("/", "yuancloud.__DEBUG__.services['web.Tour'].run('event_buy_tickets', 'test')", "yuancloud.__DEBUG__.services['web.Tour'].tours.event_buy_tickets", login="demo")

    def test_public(self):
        self.phantom_js("/", "yuancloud.__DEBUG__.services['web.Tour'].run('event_buy_tickets', 'test')", "yuancloud.__DEBUG__.services['web.Tour'].tours.event_buy_tickets")
