import pickle
from io import BytesIO
import sys
import codecs
import mimetypes
import random
import string

from aiohttp import CookieJar

from .compat import compat_cookiejar, compat_pickle


class ClientCookieJar(CookieJar):
    """Custom CookieJar that can be pickled to/from strings
    """
    def __init__(self, cookie_string=None, **kwargs):
        CookieJar.__init__(self, **kwargs)
        if cookie_string:
            self._cookies = pickle.loads(codecs.decode(cookie_string.encode(), "base64"))

    # @property
    # def auth_expires(self):
    #     for cookie in self:
    #         if cookie.name in ('ds_user_id', 'ds_user'):
    #             return cookie.expires
    #     return None
    #
    # @property
    # def expires_earliest(self):
    #     """For backward compatibility"""
    #     return self.auth_expires

    def dump(self):
        return codecs.encode(pickle.dumps(self._cookies), "base64").decode()


class MultipartFormDataEncoder(object):
    """
    Modified from
    http://stackoverflow.com/questions/1270518/python-standard-library-to-post-multipart-form-data-encoded-data
    """
    def __init__(self, boundary=None):
        self.boundary = boundary or \
            ''.join(random.choice(string.ascii_letters + string.digits + '_-') for _ in range(30))
        self.content_type = 'multipart/form-data; boundary={}'.format(self.boundary)

    @classmethod
    def u(cls, s):
        if sys.hexversion < 0x03000000 and isinstance(s, str):
            s = s.decode('utf-8')
        if sys.hexversion >= 0x03000000 and isinstance(s, bytes):
            s = s.decode('utf-8')
        return s

    def iter(self, fields, files):
        """
        :param fields: sequence of (name, value) elements for regular form fields
        :param files: sequence of (name, filename, contenttype, filedata) elements for data to be uploaded as files
        :return:
        """
        encoder = codecs.getencoder('utf-8')
        for (key, value) in fields:
            key = self.u(key)
            yield encoder('--{}\r\n'.format(self.boundary))
            yield encoder(self.u('Content-Disposition: form-data; name="{}"\r\n').format(key))
            yield encoder('\r\n')
            if isinstance(value, (int, float)):
                value = str(value)
            yield encoder(self.u(value))
            yield encoder('\r\n')
        for (key, filename, contenttype, fd) in files:
            key = self.u(key)
            filename = self.u(filename)
            yield encoder('--{}\r\n'.format(self.boundary))
            yield encoder(self.u('Content-Disposition: form-data; name="{}"; filename="{}"\r\n').format(key, filename))
            yield encoder('Content-Type: {}\r\n'.format(
                contenttype or mimetypes.guess_type(filename)[0] or 'application/octet-stream'))
            yield encoder('Content-Transfer-Encoding: binary\r\n')
            yield encoder('\r\n')
            yield (fd, len(fd))
            yield encoder('\r\n')
        yield encoder('--{}--\r\n'.format(self.boundary))

    def encode(self, fields, files):
        body = BytesIO()
        for chunk, _ in self.iter(fields, files):
            body.write(chunk)
        return self.content_type, body.getvalue()
