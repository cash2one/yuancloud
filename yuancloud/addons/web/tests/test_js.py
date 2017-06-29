import yuancloud.tests

class WebSuite(yuancloud.tests.HttpCase):
    def test_01_js(self):
        self.phantom_js('/web/tests?mod=web',"","", login='admin')
