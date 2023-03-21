from flask import Flask, jsonify, request
# исправить два импорта в один
app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'] ) # я думаю что роуты должны быть по экранам, и каждую функцию писать под экран
def responseExample():
      if request.method == 'POST':
        print(request.get_json()) # получаем json от фронта с данными

# здесь твои вычисления 

        return jsonify(ProbabilityOfPurchase = 3000, DatasetSizeClients=200 ....) # возвращаем на фронт данные
      else:
        return '<p>GET REQUEST<p>'


        # @app.route("/modelTraining", methods=['GET', 'POST'] )


    # Давайт сделаем так, на GET функция выдает весь список данных для каждого экрана, 
    # на POST запрос функция принимает новое значение поля, пересчитывает все остальные поля, возвращает новый список полей в JSON формате
        