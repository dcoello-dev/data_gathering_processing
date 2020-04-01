from flask import Flask
from app.data_handler import DataHandler
from app.database_connection import DatabaseConnection

def thread_flask(db_conf):
    """Launch flask app in a thread"""
    app = Flask(__name__)
    data_handler = DataHandler(DatabaseConnection(db_conf))

    @app.route('/')
    def price_series():
        """Returns price series in json format"""
        return data_handler.get_price_series()

    app.run(debug=True, use_reloader=False,
            threaded=True, host='0.0.0.0')