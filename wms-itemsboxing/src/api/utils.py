
class HttpStatus:   
    def __init__(self, code, description):
        self.code = code
        self.description = description


HttpStatus.OK = HttpStatus(200, 'OK')
HttpStatus.Created = HttpStatus(201, 'Created')
HttpStatus.Accepted = HttpStatus(202, 'Accepted')
HttpStatus.NoContent = HttpStatus(204, 'No Content')
HttpStatus.BadRequest = HttpStatus(400, 'Bad Request')
HttpStatus.Unauthorized = HttpStatus(401, 'Unauthorized')
HttpStatus.NotFound = HttpStatus(404, 'Not Found')
HttpStatus.Gone = HttpStatus(410, 'Gone')
