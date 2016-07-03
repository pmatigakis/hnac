from hnac.web.app import create_app

import settings

app = create_app(settings)

app.run()
