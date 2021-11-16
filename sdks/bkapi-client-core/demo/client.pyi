from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup

class Group(OperationGroup):
    @property
    def test(self) -> Operation:
        """test api"""

class Client(APIGatewayClient):
    @property
    def api(self) -> Group:
        """api resources"""
