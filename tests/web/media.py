import unittest

from ..common import WebApiTestBase, WebClientError as ClientError, compat_mock


class MediaTests(WebApiTestBase):

    @classmethod
    def init_all(cls, api):
        return [
            {
                'name': 'test_media_info',
                'test': MediaTests('test_media_info', api),
            },
            {
                'name': 'test_notfound_media_info',
                'test': MediaTests('test_notfound_media_info', api)
            },
            {
                'name': 'test_media_comments',
                'test': MediaTests('test_media_comments', api),
            },
            {
                'name': 'test_notfound_media_comments',
                'test': MediaTests('test_notfound_media_comments', api)
            },
            {
                'name': 'test_media_comments_extract',
                'test': MediaTests('test_media_comments_extract', api)
            },
            {
                'name': 'test_post_comment',
                'test': MediaTests('test_post_comment', api),
                'require_auth': True,
            },
            {
                'name': 'test_post_comment_mock',
                'test': MediaTests('test_post_comment_mock', api),
                'require_auth': True,
            },
            {
                'name': 'test_del_comment',
                'test': MediaTests('test_del_comment', api),
                'require_auth': True,
            },
            {
                'name': 'test_del_comment_mock',
                'test': MediaTests('test_del_comment_mock', api),
                'require_auth': True,
            },
            {
                'name': 'test_post_like',
                'test': MediaTests('test_post_like', api),
                'require_auth': True,
            },
            {
                'name': 'test_post_like_mock',
                'test': MediaTests('test_post_like_mock', api),
            },
            {
                'name': 'test_delete_like',
                'test': MediaTests('test_delete_like', api),
                'require_auth': True,
            },
            {
                'name': 'test_delete_like_mock',
                'test': MediaTests('test_post_like_mock', api),
            },
            {
                'name': 'test_carousel_media_info',
                'test': MediaTests('test_carousel_media_info', api),
            },
        ]

    def test_media_info(self):
        results = self.api.media_info(self.test_media_shortcode)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('link'))
        self.assertIsNotNone(results.get('images'))

    def test_notfound_media_info(self):
        self.assertRaises(ClientError, lambda: self.api.media_info('BSgmaRDg-xX'))

    def test_carousel_media_info(self):
        results = self.api.media_info2('BQ0eAlwhDrw')
        self.assertIsNotNone(results.get('link'))
        self.assertIsNotNone(results.get('type'))
        self.assertIsNotNone(results.get('images'))

    def test_media_comments(self):
        results = self.api.media_comments(self.test_media_shortcode, count=20)
        self.assertGreaterEqual(len(results), 0)

    def test_notfound_media_comments(self):
        self.assertRaises(ClientError, lambda: self.api.media_comments('BSgmaRDg-xX'))

    def test_media_comments_extract(self):
        results = self.api.media_comments(self.test_media_shortcode, count=20, extract=True)
        self.assertGreaterEqual(len(results), 0)
        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], dict)

    @unittest.skip('Modifies data.')
    def test_post_comment(self):
        results = self.api.post_comment(self.test_media_id, '<3')
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('id'))

    @compat_mock.patch('instagram_web_api.Client._make_request')
    def test_post_comment_mock(self, make_request):
        make_request.return_value = {'status': 'ok', 'id': '12345678'}
        self.api.post_comment(self.test_media_id, '<3')
        make_request.assert_called_with(
            'https://www.instagram.com/web/comments/%(media_id)s/add/' % {'media_id': self.test_media_id},
            params={'comment_text': '<3'})

    @unittest.skip('Modifies data / Needs actual data.')
    def test_del_comment(self):
        results = self.api.delete_comment(self.test_media_id, self.test_comment_id)
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_web_api.Client._make_request')
    def test_del_comment_mock(self, make_request):
        make_request.return_value = {'status': 'ok'}
        self.api.delete_comment(self.test_media_id, self.test_comment_id)
        make_request.assert_called_with(
            'https://www.instagram.com/web/comments/%(media_id)s/delete/%(comment_id)s/'
            % {'media_id': self.test_media_id, 'comment_id': self.test_comment_id},
            params='')

    @unittest.skip('Modifies data')
    def test_post_like(self):
        results = self.api.post_like(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_web_api.Client._make_request')
    def test_post_like_mock(self, make_request):
        make_request.return_value = {'status': 'ok'}
        self.api.post_like(self.test_media_id)
        make_request.assert_called_with(
            'https://www.instagram.com/web/likes/%(media_id)s/like/' % {'media_id': self.test_media_id},
            params='')

    @unittest.skip('Modifies data')
    def test_delete_like(self):
        results = self.api.delete_like(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_web_api.Client._make_request')
    def test_delete_like_mock(self, make_request):
        make_request.return_value = {'status': 'ok'}
        self.api.delete_like(self.test_media_id)
        make_request.assert_called_with(
            'https://www.instagram.com/web/likes/%(media_id)s/unlike/' % {'media_id': self.test_media_id},
            params='')
