


from flask import Flask, jsonify, request
from flask_cors import CORS

from routes import model_result, ab_results,  fin_effect
 

import random
import pandas as pd
import json

INPUT_CONFIG = 'config.json'
with open(INPUT_CONFIG, "r") as read_file:
    config = json.load(read_file)

base_parameters = config.copy()
base_parameters.pop('TABLES', None) 


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


app.register_blueprint(model_result)
app.register_blueprint(ab_results)
app.register_blueprint(fin_effect)


@app.route("/", methods=['GET', 'POST'] ) 
def responseExample():
      if request.method == 'POST':
        print(request.get_json()) 

# здесь твои вычисления 

        return jsonify(ProbabilityOfPurchase = 3000, DatasetSizeClients=200) # возвращаем на фронт данные
      else:
        return '<p>GET REQUEST<p>'


        # @app.route("/modelTraining", methods=['GET', 'POST'] )
