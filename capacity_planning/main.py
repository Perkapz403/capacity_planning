from locust import FastHttpUser, LoadTestShape, constant_pacing
from tasks.utils.functions import get_auth_token, get_company
from tasks.purchase_invoice import PurchaseAccountant
from tasks.sales_invoice import SalesAccountant

class BaseUser(FastHttpUser):
    abstract = True
    wait_time = constant_pacing(40)

    def __init__(self, environment):
        self.default_headers = {
            'Authorization': get_auth_token(self.host)
        }
        self.company = get_company(self.host)
        super().__init__(environment)


class SUGAAccountUser(BaseUser):
    host   = 'https://suga.staging.stanch.io'
    tasks  = [SalesAccountant, PurchaseAccountant]

class MNAccountUser(BaseUser):
    host   = 'https://plus.staging.stanch.io'
    tasks  = [SalesAccountant, PurchaseAccountant]

class StanchAccountUser(BaseUser):
    host   = 'https://sugi.staging.stanch.io'
    tasks  = [SalesAccountant, PurchaseAccountant]

class RRRAccountUser(BaseUser):
    host   = 'https://rrr.staging.stanch.io'
    tasks  = [SalesAccountant, PurchaseAccountant]

class RedmiAccountUser(BaseUser):
    host   = 'https://redmi.staging.stanch.io'
    tasks  = [SalesAccountant, PurchaseAccountant]

class RealmeAccountUser(BaseUser):
    host   = 'https://realme.staging.stanch.io'
    tasks  = [SalesAccountant, PurchaseAccountant]

class MercuryAccountUser(BaseUser):
    host   = 'https://mercury.staging.stanch.io'
    tasks  = [SalesAccountant, PurchaseAccountant]


"""
# SPIKE TEST
class StagesShapeWithCustomUsers(LoadTestShape):

    stages = [
        {"duration": 10, "users": 2, "spawn_rate": 10, "user_classes": [BHAccountUser]},
        {"duration": 30, "users": 10, "spawn_rate": 10, "user_classes": [MNAccountUser]},
        {"duration": 60, "users": 4, "spawn_rate": 10, "user_classes": [StanchAccountUser]},
        {"duration": 120, "users": 10, "spawn_rate": 10, "user_classes": [TvsAccountUser]},
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                try:
                    tick_data = (stage["users"], stage["spawn_rate"], stage["user_classes"])
                except:
                    tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data

        return None
"""