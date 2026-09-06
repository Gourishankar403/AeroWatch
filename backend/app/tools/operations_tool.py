from app.models.operations import OperationsEvidence
from app.providers.faa_provider import FAAProvider


class OperationsTool:

    """Provides operational intelligence 
     capabilites for airport investigations"""


    def __init__(self):
        self.provider=FAAProvider()


    def investigate_airport(
            self,
            aiport:str
    )->OperationsEvidence:
        """Retrieve operaitonal evidence for a specific saiport"""


        return self.provider.get_airport_status(aiport)


