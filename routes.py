
from flask import Flask, jsonify, request, Blueprint


import random
import pandas as pd
import json


INPUT_CONFIG = 'config.json'
with open(INPUT_CONFIG, "r") as read_file:
    config = json.load(read_file)

base_parameters = config.copy()
base_parameters.pop('TABLES', None) 

model_result = Blueprint("model_result", __name__)
ab_results = Blueprint("ab_results", __name__)
fin_effect = Blueprint("fin_effect", __name__)


@model_result.route("/api/modelResult", methods=['GET', 'POST'])

def model_results_screen():
      if request.method == 'POST':
        input = request.get_json()

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





@ab_results.route("/api/abResults", methods=['POST'])
def ab_results_screen():
      if request.method == 'POST':
        input = request.get_json()

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
        response = {
    'randContrGrSales': randContrGrSales,
    'randTestGrSales': randTestGrSales,
    'topContrGrSales': topContrGrSales,
    'topTestGrSales': topTestGrSales,
    'randPvalue': randPvalue,
    'topPvalue': topPvalue
}

        return json.dumps(response, default=str)

      


      
@fin_effect.route("/api/finEffect", methods=['POST'])

def fin_effect_screen():
      if request.method == 'POST':
        input = request.get_json() 
        setSize = input.get('setSize')
        topClientsForAb = input.get('topClientsForAb')
        topContrGrSales = input.get('topContrGrSales')
        randContrGrSales = input.get('randContrGrSales')
        topTestGrSales = input.get('topTestGrSales')

        contrTestSize = topClientsForAb/2
        
        probRandPilot = random.uniform(0.97, 1.03) * randContrGrSales/contrTestSize
        probTopPilot = random.uniform(0.97, 1.03) * topContrGrSales/contrTestSize
        probTopPilotTest = random.uniform(0.85, 1.1) * topTestGrSales/contrTestSize

        growthSalesTopToRandPilot = probTopPilot/probRandPilot
        conversionRateGrowthPilot = probTopPilotTest/probTopPilot

        communicationCost = input.get('communicationCost')
        revenueUsd = input.get('revenueUsd')
        conversionDepreciationRate = input.get('conversionDepreciationRate')
        monProdSalesPilot = int(setSize*probRandPilot)
        monTopProdSalesUpliftPilot = int((probTopPilotTest-probTopPilot)*topClientsForAb)
        revUpliftMonthPilot = int(monTopProdSalesUpliftPilot*revenueUsd - topClientsForAb*communicationCost)
        revUpliftYearPilot = monTopProdSalesUpliftPilot*revenueUsd * (1 - (1-conversionDepreciationRate)**12) / (conversionDepreciationRate) - 12*topClientsForAb*communicationCost

        return jsonify(probRandPilot = probRandPilot, probTopPilot = probTopPilot, 
                       growthSalesTopToRandPilot = growthSalesTopToRandPilot, conversionRateGrowthPilot = conversionRateGrowthPilot,
                       monProdSalesPilot = monProdSalesPilot, monTopProdSalesUpliftPilot = monTopProdSalesUpliftPilot, 
                       revUpliftMonthPilot = revUpliftMonthPilot, revUpliftYearPilot = revUpliftYearPilot)
      