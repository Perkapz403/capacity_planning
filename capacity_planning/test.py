from locust import SequentialTaskSet, FastHttpUser, constant, task
from tasks.utils.functions import get_auth_token
import logging

class Demo(SequentialTaskSet):
    @task
    def http_test(self):
        with self.rest('GET', '/api/resource/Customer') as resp:
            print(resp.js['data'])

    def on_start(self):
        self.rest = self.user.rest
        return super().on_start()

class DemoUser(FastHttpUser):
    abstract = True

    def __init__(self, environment):
        super().__init__(environment)
    
    def on_start(self):
        self.default_headers = {
        'Authorization': 'token a41ee17f48ae9a9:4dc63df90d95d50'
        }
        return super().on_start()

class TestUser(DemoUser):
    wait_time = constant(60)
    host = 'https://mn.staging.stanch.io'
    tasks = [Demo]
