import time
import hmac
import base64
import hashlib
from random import randint


def gen_user_breadcrumb(size):
    key = 'iN4$aGr0m'
    dt = int(time.time() * 1000)

    # typing time elapsed
    time_elapsed = randint(500, 1500) + size * randint(500, 1500)

    text_change_event_count = max(1, size / randint(3, 5))

    data = '%(size)s %(elapsed)s %(count)s %(dt)s' % {
        'size': size, 'elapsed': time_elapsed, 'count': text_change_event_count, 'dt': dt
    }
    return '%s\n%s\n' % (
        base64.b64encode(hmac.new(key.encode('ascii'), data.encode('ascii'), digestmod=hashlib.sha256).digest()),
        base64.b64encode(data))


class Chunk(object):
    """
    Simple object class to encapulate an upload Chunk
    """
    def __init__(self, index, start, end, total):
        self.index = index
        self.start = start
        self.end = end
        self.total = total

    @property
    def is_first(self):
        return self.index == 0

    @property
    def is_last(self):
        return self.index == self.total - 1

    @property
    def length(self):
        return self.end - self.start


def chunk_generator(chunk_count, chunk_size, file_data):
    """
    Generic chunk generator logic

    :param chunk_count: Number of chunks wanted
    :param chunk_size: Size of each chunk
    :param file_data: bytes to be split into chunk
    :return:
    """
    total_len = len(file_data)
    for i in range(chunk_count):
        start_range = i * chunk_size
        end_range = (start_range + chunk_size) if i < (chunk_count - 1) else total_len
        chunk_info = Chunk(i, start_range, end_range, chunk_count)
        yield chunk_info, file_data[chunk_info.start: chunk_info.end]


def max_chunk_size_generator(chunk_size, file_data):
    """
    Generate chunks by defining a maximum chunk size

    :param chunk_size: Maximum chunk size allow
    :param file_data: bytes data
    :return:
    """
    chunk_count, final_chunk = divmod(len(file_data), chunk_size)
    if final_chunk:
        chunk_count += 1
    return chunk_generator(chunk_count, chunk_size, file_data)


def max_chunk_count_generator(chunk_count, file_data):
    """
    Generate chunks by defining a maximum number of chunks

    :param chunk_count: Max number of chunks
    :param file_data: bytes data
    :return:
    """
    chunk_size = len(file_data) // chunk_count
    return chunk_generator(chunk_count, chunk_size, file_data)


class InstagramID:
    """
    Utility class to convert between IG's internal numeric ID and the shortcode used in weblinks.
    Does NOT apply to private accounts.
    """
    ENCODING_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'

    @classmethod
    def _encode(cls, num, alphabet=ENCODING_CHARS):
        if num == 0:
            return alphabet[0]
        arr = []
        base = len(alphabet)
        while num:
            rem = num % base
            num //= base
            arr.append(alphabet[rem])
        arr.reverse()
        return ''.join(arr)

    @classmethod
    def _decode(cls, shortcode, alphabet=ENCODING_CHARS):
        base = len(alphabet)
        strlen = len(shortcode)
        num = 0
        idx = 0
        for char in shortcode:
            power = (strlen - (idx + 1))
            num += alphabet.index(char) * (base ** power)
            idx += 1
        return num

    @classmethod
    def weblink_from_media_id(cls, media_id):
        """
        Returns the web link for the media id

        :param media_id:
        :return:
        """
        return 'https://www.instagram.com/p/%s/' % cls.shorten_media_id(media_id)

    @classmethod
    def shorten_media_id(cls, media_id):
        """
        Returns the shortcode for a media id

        :param media_id: string in the format id format: AAA_BB where AAA is the pk, BB is user_id
        :return:
        """
        # media id format: AAA_BB where AAA is the pk, BB is user_id
        internal_id = int((str(media_id).split('_')[0]))
        return cls.shorten_id(internal_id)

    @classmethod
    def shorten_id(cls, internal_id):
        """
        Returns the shortcode for a numeric media PK

        :param internal_id: numeric ID value
        :return:
        """
        return cls._encode(internal_id)

    @classmethod
    def expand_code(cls, short_code):
        """
        Returns the numeric ID for a shortcode

        :param short_code:
        :return:
        """
        return cls._decode(short_code)
