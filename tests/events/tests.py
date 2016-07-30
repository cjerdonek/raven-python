import six

from raven.base import Client
from raven.events import Exception as ExceptionEvent
from raven.utils.testutils import TestCase


class ExceptionTest(TestCase):

    # Handle compatibility.
    if hasattr(Exception, '__suppress_context__'):
        # Then exception chains are supported.
        def transform_expected(self, expected):
            return expected
    else:
        # Otherwise, we only report the first element.
        def transform_expected(self, expected):
            return expected[:1]

    def get_values(self):
        c = Client()
        event = ExceptionEvent(c)
        result = event.capture()
        info = result['exception']
        values = info['values']

        return values

    def check_capture(self, expected):
        """
        Check the return value of capture().

        Args:
          expected: the expected "type" values.
        """
        values = self.get_values()
        type_names = [value['type'] for value in values]
        expected = self.transform_expected(expected)

        self.assertEqual(type_names, expected)

    def test_stacktrace(self):
        try:
            raise ValueError()
        except Exception:
            values = self.get_values()
            value, = values
            stacktrace = value['stacktrace']
            frames = stacktrace['frames']
            frame, = frames
            raise Exception(sorted(frame.keys()))

    def test_simple(self):
        try:
            raise ValueError()
        except Exception:
            self.check_capture(['ValueError'])

    def test_nested(self):
        try:
            raise ValueError()
        except Exception:
            try:
                raise KeyError()
            except Exception:
                self.check_capture(['KeyError', 'ValueError'])

    def test_raise_from(self):
        try:
            raise ValueError()
        except Exception as exc:
            try:
                six.raise_from(KeyError(), exc)
            except Exception:
                self.check_capture(['KeyError', 'ValueError'])

    def test_raise_from_different(self):
        try:
            raise ValueError()
        except Exception as exc:
            try:
                six.raise_from(KeyError(), TypeError())
            except Exception:
                self.check_capture(['KeyError', 'TypeError'])
