from flask import Flask, render_template
import logging
# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')


#logging.basicConfig(filename='LogFiles/logs.log',
#                    encoding='utf-8', 
#                    format='%(asctime)s %(levelname)-8s %(message)s',
#                    level=logging.DEBUG,
#                    datefmt='%Y-%m-%d %H:%M:%S')

# Sample HTTP error handling
#@app.errorhandler(404)
#def not_found(error):
#    return render_template('404.html'), 404

# Import a module 
from app import zipfile
