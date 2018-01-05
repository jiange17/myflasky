import unittest
from app.models import User
from app import create_app, db


class UserModelTestCase(unittest.TestCase):

    # def setUp(self):
    #     self.app = create_app('testing')
    #     self.app_context = self.app.app_context()
    #     self.app_context.push()
    #     db.create_all()

    def tearDown(self): #暂时在shell里执行test， 如果要在当前文件执行，则取消这几行注释。
        db.session.remove()
        # db.drop_all()
        # self.app_context.pop()

    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertFalse(u.password_hash == u2.password_hash)

    def test_generate_confirmation_token(self):
        u = User()
        token = u.generate_confirmation_token()
        self.assertFalse(token is None)

    def test_comfirm_token(self):
        u = User()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))


if __name__ == '__main__':
    unittest.main()
