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
def model_results_screen():
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

@app.route("/", methods=['POST'] ) # я думаю что роуты должны быть по экранам, и каждую функцию писать под экран
def ab_results_screen():
      if request.method == 'POST':
        input = request.get_json() # получаем json от фронта с данными

        topClientsForAb = input.get('topClientsForAb')
        oneAbGrSize = int(topClientsForAb/2)

        ab_results = pd.read_pickle('ab_test_results_from_1k_to_5k.pkl')
        ab_results = ab_results[ab_results['top']==oneAbGrSize]

        randContrGrSales = ab_results[ab_results['test_control']=='control_random'].sales.values[0]
        randTestGrSales = ab_results[ab_results['test_control']=='test_random'].sales.values[0]
        topTestGrSales = ab_results[ab_results['test_control']=='test_top_scores'].sales.values[0]
        topContrGrSales = ab_results[ab_results['test_control']=='control_top_scores'].sales.values[0]

        randPvalue  = ab_results[ab_results['test_control']=='control_random'].p_value.values[0]
        topPvalue  = ab_results[ab_results['test_control']=='control_top_scores'].p_value.values[0]

        return jsonify(randContrGrSales = randContrGrSales, randTestGrSales = randTestGrSales, 
                       topContrGrSales = topContrGrSales, topTestGrSales = topTestGrSales,
                       randPvalue = randPvalue, topPvalue = topPvalue)