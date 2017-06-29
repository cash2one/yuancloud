import sys

# Mock deprecated yuancloud.addons.web.http module
import yuancloud.http
sys.modules['yuancloud.addons.web.http'] = yuancloud.http
http = yuancloud.http

import controllers
