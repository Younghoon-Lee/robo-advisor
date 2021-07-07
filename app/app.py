from flask import Flask, request, render_template, make_response
import os
from sqlalchemy import create_engine, text

dirname = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('sqlite+pysqlite:///'+dirname +
                       '/main.db', future=True, echo=True)


# configuration
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)


NUMBER_OF_QUESTIONS = 10


@app.route('/survey')
@app.route('/', methods=['GET'])
def survey():
    return render_template("index.html")


@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        total_score = 0
        for i in range(1, NUMBER_OF_QUESTIONS+1):
            if i == 4:
                period_score, invest_score = [], []

                if request.form.get('1') == 'on':
                    invest_score.append(6)
                    period_score.append(int(request.form.get('period1')))
                if request.form.get('2') == 'on':
                    invest_score.append(3)
                    period_score.append(int(request.form.get('period2')))
                if request.form.get('3') == 'on':
                    invest_score.append(1)
                    period_score.append(int(request.form.get('period3')))
                if invest_score:
                    total_score += max(period_score) + max(invest_score)
            elif i == 8 or i == 9:
                continue
            else:
                total_score += int(request.form.get('options'+str(i)))
        print(total_score)

        # 투자자성향 분류 1단계
        if total_score <= 14:
            user_type_level = 5  # 안정형
        elif total_score <= 19:
            user_type_level = 4  # 안정추구형
        elif total_score <= 24:
            user_type_level = 3  # 위험중립형
        elif total_score <= 29:
            user_type_level = 2  # 적극투자형
        else:
            user_type_level = 1  # 공격투자형

        # 투자자성향 분류 2단계
        investing_period = int(request.form['options9'])
        if investing_period == 1:
            if (user_type_level == 1) or (user_type_level == 2):
                user_type = "위험중립형"
            if (user_type_level == 3) or (user_type_level == 4):
                user_type = "안전추구형"
            else:
                user_type = "안정형"
        elif investing_period == 2:
            if (user_type_level == 1):
                user_type = "공격투자형"
            elif user_type_level == 2:
                user_type = "적극투자형"
            elif user_type_level == 3:
                user_type = "위험중립형"
            else:
                user_type = "안전추구형"
        elif investing_period == 3:
            if user_type_level == 1:
                user_type = "공격투자형"
            elif user_type_level == 2 or user_type_level == 3:
                user_type = "적극투자형"
            elif user_type_level == 4:
                user_type = "위험중립형"
            else:
                user_type = "안전추구형"
        elif investing_period == 4:
            if (user_type_level == 1) or (user_type_level == 2):
                user_type = "공격투자형"
            elif (user_type_level == 3):
                user_type = "적극투자형"
            else:
                user_type = "위험중립형"
        else:
            if (user_type_level == 5) or (user_type_level == 4):
                user_type = "위험중립형"
            else:
                user_type = "공격투자형"
        response = make_response(render_template(
            'result.html', user_type=user_type))
        response.set_cookie('user_type', user_type)

        if user_type == '안정형':
            return "Ineligible"

        return response
    else:
        return "Invalid Access"


@app.route('/optimize')
def optimize():
    user_type = request.cookies.get('user_type')
    if user_type == '공격투자형':
        user_type = '적극투자형'
    results, schema, assetType = [], {
        'assetType': None, 'weight': 0.0, 'items': []}, []

    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM {}".format(user_type)))
        for row in rows.mappings():
            temp = schema.copy()
            temp['items'] = []
            if row['assetType'] not in assetType:
                temp['assetType'] = row['assetType']
                temp['items'].append(row)
                assetType.append(row['assetType'])
                results.append(temp)
                continue
            for result in results:
                if result['assetType'] == row['assetType']:
                    result['items'].append(row)
                    break
        conn.commit()
    for result in results:
        result['weight'] = sum([item['targetWeight']
                               for item in result['items']])

    return render_template('optimize.html', results=results, user_type=user_type)


@app.route('/rebalance')
def rebalance():
    user_type = request.cookies.get('user_type')
    if user_type == "공격투자형":
        user_type = "적극투자형"
    results, schema, assetType = [], {
        'assetType': None, 'weightBefore': 0.0, 'weightAfter': 0.0, 'items': []}, []

    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM {}".format(user_type)))
        for row in rows.mappings():
            temp = schema.copy()
            temp['items'] = []
            if row['assetType'] not in assetType:
                temp['assetType'] = row['assetType']
                temp['items'].append(row)
                assetType.append(row['assetType'])
                results.append(temp)
                continue
            for result in results:
                if result['assetType'] == row['assetType']:
                    result['items'].append(row)
                    break
        conn.commit()
    for result in results:
        result['weightBefore'] = sum([item['beforeWeight']
                                      for item in result['items']])
        result['weightAfter'] = sum([item['afterWeight']
                                     for item in result['items']])
    return render_template('rebalance.html', results=results, user_type=user_type)


@app.route('/selection')
def selection():
    return render_template('selection.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
