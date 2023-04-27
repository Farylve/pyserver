# обычно на бэке в этом файле только ссылки на рабочие файлы


from flask import Flask, jsonify, request
from flask_cors import CORS
# импортируем model_result = Blueprint(...) из файла
from routes import model_result, ab_results 
 

import random
import pandas as pd
import json

INPUT_CONFIG = 'config.json'
with open(INPUT_CONFIG, "r") as read_file:
    config = json.load(read_file)

base_parameters = config.copy()
base_parameters.pop('TABLES', None) # Оставляем только параметры


# функция запуска сервера, может быть только одна в проекте 
app = Flask(__name__)
CORS(app)

# Регистрирует какая функция будет при запросе на  '/', то есть на https://abitmore.ai/
app.register_blueprint(model_result)
app.register_blueprint(ab_results)


@app.route("/", methods=['GET', 'POST'] ) # я думаю что роуты должны быть по экранам, и каждую функцию писать под экран
def responseExample():
      if request.method == 'POST':
        print(request.get_json()) # получаем json от фронта с данными

# здесь твои вычисления 

        return jsonify(ProbabilityOfPurchase = 3000, DatasetSizeClients=200) # возвращаем на фронт данные
      else:
        return '<p>GET REQUEST<p>'


        # @app.route("/modelTraining", methods=['GET', 'POST'] )


    # Давайт сделаем так, на GET функция выдает весь список данных для каждого экрана, 
    # на POST запрос функция принимает новое значение поля, пересчитывает все остальные поля, возвращает новый список полей в JSON формате
        