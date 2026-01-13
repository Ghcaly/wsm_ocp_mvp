import unittest
from api.utils import HttpStatus


class HttpStatusTest(unittest.TestCase):

    def test_http_status_initialization(self):
        # Arrange & Act
        status = HttpStatus(200, 'OK')

        # Assert
        self.assertEqual(status.code, 200)
        self.assertEqual(status.description, 'OK')

    def test_http_status_ok(self):
        # Act & Assert
        self.assertEqual(HttpStatus.OK.code, 200)
        self.assertEqual(HttpStatus.OK.description, 'OK')

    def test_http_status_created(self):
        # Act & Assert
        self.assertEqual(HttpStatus.Created.code, 201)
        self.assertEqual(HttpStatus.Created.description, 'Created')

    def test_http_status_accepted(self):
        # Act & Assert
        self.assertEqual(HttpStatus.Accepted.code, 202)
        self.assertEqual(HttpStatus.Accepted.description, 'Accepted')

    def test_http_status_no_content(self):
        # Act & Assert
        self.assertEqual(HttpStatus.NoContent.code, 204)
        self.assertEqual(HttpStatus.NoContent.description, 'No Content')

    def test_http_status_bad_request(self):
        # Act & Assert
        self.assertEqual(HttpStatus.BadRequest.code, 400)
        self.assertEqual(HttpStatus.BadRequest.description, 'Bad Request')

    def test_http_status_unauthorized(self):
        # Act & Assert
        self.assertEqual(HttpStatus.Unauthorized.code, 401)
        self.assertEqual(HttpStatus.Unauthorized.description, 'Unauthorized')

    def test_http_status_not_found(self):
        # Act & Assert
        self.assertEqual(HttpStatus.NotFound.code, 404)
        self.assertEqual(HttpStatus.NotFound.description, 'Not Found')

    def test_http_status_gone(self):
        # Act & Assert
        self.assertEqual(HttpStatus.Gone.code, 410)
        self.assertEqual(HttpStatus.Gone.description, 'Gone')
