from flask import Flask, request, g, has_request_context
import logging

app = Flask(__name__)

# Custom filter to add request ID to log records
class RequestIDFilter(logging.Filter):
    def filter(self, record):
        if has_request_context():
            record.request_id = g.get('request_id', 'N/A')
        else:
            record.request_id = 'N/A'
        return True

# Configure logging
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(request_id)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.addFilter(RequestIDFilter())
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

# Set request ID before each request
@app.before_request
def set_request_id():
    if 'X-Request-ID' in request.headers:
        g.request_id = request.headers['X-Request-ID']

# Example route
@app.route('/test')
def test():
    app.logger.info('This is a test log')
    return 'Test'

if __name__ == '__main__':
    app.run(debug=True)
​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​
