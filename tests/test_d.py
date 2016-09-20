from unittest import TestCase

from deparse import D


class TestD(TestCase):

    def setUp(self):
        super(TestD, self).setUp()
        self.d = D('a pattern to match')

    def test_if_merge_single_returns_new_value(self):
        assert self.d.merge_single('old', 'new') == 'new'

    def test_if_merge_single_returns_preserves_old_when_new_is_none(self):
        assert self.d.merge_single('old', None) == 'old'

    def test_if_merge_single_returns_preserves_old_when_new_falsy(self):
        assert self.d.merge_single('old', 0) == 0
