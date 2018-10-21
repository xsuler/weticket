from locust import HttpLocust, TaskSet, task
import uuid

class UserBehavior(TaskSet):
    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        self.login()

    def on_stop(self):
        """ on_stop is called when the TaskSet is stopping """

    def login(self):
        self.client.post("/api/u/user/bind", {"openid":uuid.uuid1(), "student_id":uuid.uuid1()})

    @task(1)
    def index(self):
        self.client.get("/")

    @task(1)
    def profile(self):
        self.client.get("/profile")

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
