from email_store import *


class TestClass:

    def test_add_email(self):
        email_store = EmailStore()
        email = email_store.add("Kevin", "Hayden")
        assert email in email_store.emails

    def test_none_first_name(self):
        email_store = EmailStore()
        try:
            email_store.add(None, "Hayden")
        except Exception:
            assert True
            return
        assert False

    def test_none_last_name(self):
        email_store = EmailStore()
        try:
            email_store.add("Kevin", None)
        except Exception:
            assert True
            return
        assert False

    def test_add_duplicate(self):
        email_store = EmailStore()
        email_store.add("Kevin", "Hayden")
        email = email_store.add("Kevin", "Hayden")
        print(email)
        assert email in email_store.emails

    def test_remove_not_exist(self):
        email_store = EmailStore()
        try:
            email_store.remove("abcd@marist.edu")
        except Exception:
            assert True
            return
        assert False
