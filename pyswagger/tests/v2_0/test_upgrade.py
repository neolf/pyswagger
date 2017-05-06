from ... import App
from ..utils import get_test_data_folder
from ...scan import Scanner
from ...scanner.v2_0.upgrade import Upgrade
import unittest

class UpgradeTestCase(unittest.TestCase):
    """ for Swagger 2.0 to OpenApi 3.0 """

    def test_wordnik(self):
        """ petstore example
        """
        app = App.load(get_test_data_folder(
            version='2.0',
            which='wordnik'
        ))

        s = Scanner(app)
        u = Upgrade()
        s.scan(root=app.raw, route=[u])

        # openapi.info
        # openapi.components.securitySchemes
        # openapi.components.schemas
        # openapi.components.parameters
        # openapi.components.responses
        # openapi.servers
        # openapi.tags
        # openapi.externalDocs
        # openapi.paths:
        #  - TODO: several representative case
