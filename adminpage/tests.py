from django.test import TestCase
from codex.baseerror import InputError, LogicError, ValidateError, NotExistError
from wechat.models import Activity
from adminpage.views import ActivityList, ActivityDelete, ActivityDetail, ActivityCreate
import datetime

class ActivityListTestCase(TestCase):
    def setUp(self):
        Activity.objects.create(id=1, name="a_l_test_1", key="key", description="description",
                                start_time=datetime.datetime(2018, 10, 15, 0, 0, 0, 0),
                                end_time=datetime.datetime(2018, 11, 15, 0, 0, 0, 0),
                                place="place",
                                book_start=datetime.datetime(2018, 10, 13, 0, 0, 0, 0),
                                book_end=datetime.datetime(2018, 10, 14, 0, 0, 0, 0),
                                total_tickets=10, status=Activity.STATUS_DELETED, pic_url="", remain_tickets=10)
        Activity.objects.create(id=2, name="a_l_test_2", key="key", description="description",
                                start_time=datetime.datetime(2018, 10, 15, 0, 0, 0, 0),
                                end_time=datetime.datetime(2018, 11, 15, 0, 0, 0, 0),
                                place="place",
                                book_start=datetime.datetime(2018, 10, 13, 0, 0, 0, 0),
                                book_end=datetime.datetime(2018, 10, 14, 0, 0, 0, 0),
                                total_tickets=10, status=Activity.STATUS_SAVED, pic_url="", remain_tickets=10)
        Activity.objects.create(id=3, name="a_l_test_3", key="key", description="description",
                                start_time=datetime.datetime(2018, 10, 15, 0, 0, 0, 0),
                                end_time=datetime.datetime(2018, 11, 15, 0, 0, 0, 0),
                                place="place",
                                book_start=datetime.datetime(2018, 10, 13, 0, 0, 0, 0),
                                book_end=datetime.datetime(2018, 10, 14, 0, 0, 0, 0),
                                total_tickets=10, status=Activity.STATUS_PUBLISHED, pic_url="", remain_tickets=10)

    def testActivityList(self):
        activity_list = ActivityList().get()
        # check whether status >= 0
        self.assertEqual(len(activity_list), 2)
        sorted(activity_list, key=lambda x: x['id'])
        self.assertEqual(activity_list[0]['id'], 2)
        self.assertEqual(activity_list[1]['id'], 3)

    def tearDown(self):
        Activity.objects.get(id=1).delete()
        Activity.objects.get(id=2).delete()
        Activity.objects.get(id=3).delete()

class ActivityDeleteTestCase(TestCase):
    def setUp(self):
        Activity.objects.create(id=1, name="a_l_test_1", key="key", description="description",
                                start_time=datetime.datetime(2018, 10, 15, 0, 0, 0, 0),
                                end_time=datetime.datetime(2018, 11, 15, 0, 0, 0, 0),
                                place="place",
                                book_start=datetime.datetime(2018, 10, 13, 0, 0, 0, 0),
                                book_end=datetime.datetime(2018, 10, 14, 0, 0, 0, 0),
                                total_tickets=10, status=Activity.STATUS_DELETED, pic_url="", remain_tickets=10)
        Activity.objects.create(id=2, name="a_l_test_2", key="key", description="description",
                                start_time=datetime.datetime(2018, 10, 15, 0, 0, 0, 0),
                                end_time=datetime.datetime(2018, 11, 15, 0, 0, 0, 0),
                                place="place",
                                book_start=datetime.datetime(2018, 10, 13, 0, 0, 0, 0),
                                book_end=datetime.datetime(2018, 10, 14, 0, 0, 0, 0),
                                total_tickets=10, status=Activity.STATUS_SAVED, pic_url="", remain_tickets=10)
        Activity.objects.create(id=3, name="a_l_test_3", key="key", description="description",
                                start_time=datetime.datetime(2018, 10, 15, 0, 0, 0, 0),
                                end_time=datetime.datetime(2018, 11, 15, 0, 0, 0, 0),
                                place="place",
                                book_start=datetime.datetime(2018, 10, 13, 0, 0, 0, 0),
                                book_end=datetime.datetime(2018, 10, 14, 0, 0, 0, 0),
                                total_tickets=10, status=Activity.STATUS_PUBLISHED, pic_url="",
                                remain_tickets=10)

    def ActivityDelete_simulation(self, id):
        ActivityDelete_simulation = ActivityDelete()
        ActivityDelete_simulation.input = {}
        ActivityDelete_simulation.input['id'] = id
        return ActivityDelete_simulation

    def testActivityDelete_notExist(self):
        self.assertRaises(NotExistError, self.ActivityDelete_simulation(100).post)

    def testActivityDelete_deleted(self):
        self.assertRaises(LogicError, self.ActivityDelete_simulation(1).post)

    def testActivityDelete_saved(self):
        self.ActivityDelete_simulation(2).post()
        self.assertEqual(Activity.objects.get(id=2).status, Activity.STATUS_DELETED)

    def testActivityDelete_published(self):
        self.ActivityDelete_simulation(3).post()
        self.assertEqual(Activity.objects.get(id=3).status, Activity.STATUS_DELETED)

    def tearDown(self):
        Activity.objects.get(id=1).delete()
        Activity.objects.get(id=2).delete()
        Activity.objects.get(id=3).delete()

class ActivityDetailTestCase(TestCase):
    dict_2 = {
        'id': 2,
        'name': "a_l_test_2_new",
        'place': "place",
        'description': "description",
        'picUrl': "",
        'startTime': datetime.datetime(2018, 10, 15, 0, 0, 0, 0),
        'endTime': datetime.datetime(2018, 11, 15, 0, 0, 0, 0),
        'bookStart': datetime.datetime(2018, 10, 13, 0, 0, 0, 0),
        'bookEnd': datetime.datetime(2018, 10, 14, 0, 0, 0, 0),
        'totalTickets': 10,
        'status': Activity.STATUS_SAVED
    }
    dict_3 = {
        'id': 3,
        'name': "a_l_test_3_new",
        'place': "place",
        'description': "description",
        'picUrl': "",
        'startTime': datetime.datetime(2018, 10, 15, 0, 0, 0, 0),
        'endTime': datetime.datetime(2018, 11, 15, 0, 0, 0, 0),
        'bookStart': datetime.datetime(2018, 10, 13, 0, 0, 0, 0),
        'bookEnd': datetime.datetime(2018, 10, 14, 0, 0, 0, 0),
        'totalTickets': 10,
        'status': Activity.STATUS_PUBLISHED
    }
    dict_100 = {
        'id': 100,
        'name': "a_l_test_100",
        'place': "place",
        'description': "description",
        'picUrl': "",
        'startTime': datetime.datetime(2018, 10, 15, 0, 0, 0, 0),
        'endTime': datetime.datetime(2018, 11, 15, 0, 0, 0, 0),
        'bookStart': datetime.datetime(2018, 10, 13, 0, 0, 0, 0),
        'bookEnd': datetime.datetime(2018, 10, 14, 0, 0, 0, 0),
        'totalTickets': 10,
        'status': Activity.STATUS_PUBLISHED
    }
    def setUp(self):
        Activity.objects.create(id=1, name="a_l_test_1", key="key", description="description",
                                start_time=datetime.datetime(2018, 10, 15, 0, 0, 0, 0),
                                end_time=datetime.datetime(2018, 11, 15, 0, 0, 0, 0),
                                place="place",
                                book_start=datetime.datetime(2018, 10, 13, 0, 0, 0, 0),
                                book_end=datetime.datetime(2018, 10, 14, 0, 0, 0, 0),
                                total_tickets=10, status=Activity.STATUS_DELETED, pic_url="", remain_tickets=10)
        Activity.objects.create(id=2, name="a_l_test_2", key="key", description="description",
                                start_time=datetime.datetime(2018, 10, 15, 0, 0, 0, 0),
                                end_time=datetime.datetime(2018, 11, 15, 0, 0, 0, 0),
                                place="place",
                                book_start=datetime.datetime(2018, 10, 13, 0, 0, 0, 0),
                                book_end=datetime.datetime(2018, 10, 14, 0, 0, 0, 0),
                                total_tickets=10, status=Activity.STATUS_SAVED, pic_url="", remain_tickets=10)
        Activity.objects.create(id=3, name="a_l_test_3", key="key", description="description",
                                start_time=datetime.datetime(2018, 10, 15, 0, 0, 0, 0),
                                end_time=datetime.datetime(2018, 11, 15, 0, 0, 0, 0),
                                place="place",
                                book_start=datetime.datetime(2018, 10, 13, 0, 0, 0, 0),
                                book_end=datetime.datetime(2018, 10, 14, 0, 0, 0, 0),
                                total_tickets=10, status=Activity.STATUS_PUBLISHED, pic_url="",
                                remain_tickets=10)

    def ActivityDetail_get_simulation(self, id):
        ActivityDetail_get_simulation = ActivityDetail()
        ActivityDetail_get_simulation.input = {}
        ActivityDetail_get_simulation.input['id'] = id
        return ActivityDetail_get_simulation

    def ActivityDetail_post_simulation(self, dict):
        ActivityDetail_post_simulation = ActivityDetail()
        ActivityDetail_post_simulation.input = dict
        return ActivityDetail_post_simulation

    def testActivityDetail_get_notExist(self):
        self.assertRaises(NotExistError, self.ActivityDetail_get_simulation(100).get)

    def testActivityDetail_get_deleted(self):
        self.assertRaises(LogicError, self.ActivityDetail_get_simulation(1).get)

    def testActivityDetail_get_saved(self):
        activity_dict = self.ActivityDetail_get_simulation(2).get()
        self.assertEqual(activity_dict['name'], "a_l_test_2")

    def testActivityDetail_get_published(self):
        activity_dict = self.ActivityDetail_get_simulation(3).get()
        self.assertEqual(activity_dict['name'], "a_l_test_3")

    def testActivityDetail_post_notExist(self):
        self.assertRaises(NotExistError, self.ActivityDetail_post_simulation(self.dict_100).post)

    def testActivityDetail_post_saved(self):
        self.ActivityDetail_post_simulation(self.dict_2).post()
        activity = Activity.objects.get(id=2)
        self.assertEqual(activity.name, "a_l_test_2_new")

    def testActivityDetail_post_published(self):
        self.ActivityDetail_post_simulation(self.dict_3).post()
        activity = Activity.objects.get(id=3)
        self.assertEqual(activity.name, "a_l_test_3")

    def tearDown(self):
        Activity.objects.get(id=1).delete()
        Activity.objects.get(id=2).delete()
        Activity.objects.get(id=3).delete()

class ActivityCreateTestCase(TestCase):
    dict_1 = {
        'name': "name_1",
        'key': "key_1",
        'place': "place_1",
        'description': "description",
        'picUrl': "",
        'startTime': datetime.datetime(2018, 10, 15, 0, 0, 0, 0),
        'endTime': datetime.datetime(2018, 11, 15, 0, 0, 0, 0),
        'bookStart': datetime.datetime(2018, 10, 13, 0, 0, 0, 0),
        'bookEnd': datetime.datetime(2018, 10, 14, 0, 0, 0, 0),
        'totalTickets': 10,
        'status': Activity.STATUS_SAVED
    }

    def setUp(self):
        pass

    def ActivityCreate_post_simulation(self, dict):
        ActivityCreate_simulation = ActivityCreate()
        ActivityCreate_simulation.input = dict
        return ActivityCreate_simulation

    def testActivityCreate(self):
        self.ActivityCreate_post_simulation(self.dict_1).post()
        self.assertEqual(Activity.objects.get(name=self.dict_1['name']).key, self.dict_1['key'])

    def tearDown(self):
        Activity.objects.get(name=self.dict_1['name']).delete()