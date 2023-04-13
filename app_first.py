from flask import Flask, jsonify, request
# импорт логики роута
from api1 import api1_blueprint
import pandas as pd
import json


INPUT_CONFIG = 'config.json'
with open(INPUT_CONFIG, "r") as read_file:
    config = json.load(read_file)

base_parameters = config.copy()
base_parameters.pop('TABLES', None) # Оставляем только параметры


# инициалищация сервера
app = Flask(__name__)


# регистрация нового роутера из файла 
app.register_blueprint(api1_blueprint)

@app.route("/", methods=['GET', 'POST'] ) # я думаю что роуты должны быть по экранам, и каждую функцию писать под экран
def first_screen():
      if request.method == 'POST':
        input = request.get_json() # получаем json от фронта с данными

        setSize = input.get('setSize')
        clientsWHighestPropensityToBuy = input.get('clientsWHighestPropensityToBuy')
        probabilityOfrandomPurchase = input.get('probabilityOfrandomPurchase')
        
        revenueUsd = input.get('revenueUsd')
        communicationCost = input.get('communicationCost')
        conversionRateGrowth = input.get('conversionRateGrowth')
        conversionDepreciationRate = input.get('conversionDepreciationRate')


        clNumberProbPurch = pd.read_pickle(config['TABLES']['size2ProbFilePath']) # Отсортирован по возрастанию cl_number
        clNumberProbPurch = clNumberProbPurch[clNumberProbPurch['cl_number']>=clientsWHighestPropensityToBuy]
        probabilityOfPurchaseByTopClients = clNumberProbPurch.head(1)['precision'].values[0]

        probabilityUplift = probabilityOfPurchaseByTopClients/probabilityOfrandomPurchase

        creditCardSales = int(setSize*probabilityOfrandomPurchase)
        salesUplift = int(clientsWHighestPropensityToBuy*(conversionRateGrowth-1)*probabilityOfPurchaseByTopClients)
        revenueUpliftMonth = salesUplift*revenueUsd
        
        if conversionDepreciationRate==0:
          revenueUpliftYear = revenueUpliftMonth*12
        else:
          revenueUpliftYear = revenueUpliftMonth*(1-(1-conversionDepreciationRate)**12)/conversionDepreciationRate

        return jsonify(probabilityOfPurchaseByTopClients = probabilityOfPurchaseByTopClients, 
                       probabilityUplift = probabilityUplift, creditCardSales = creditCardSales,
                       salesUplift = salesUplift, revenueUpliftMonth = revenueUpliftMonth,
                       revenueUpliftYear = revenueUpliftYear) # возвращаем на фронт данные
      else:
        return jsonify(base_parameters) 


        # @app.route("/modelTraining", methods=['GET', 'POST'] )


    # Давайт сделаем так, на GET функция выдает весь список данных для каждого экрана, 
    # на POST запрос функция принимает новое значение поля, пересчитывает все остальные поля, возвращает новый список полей в JSON формате
        