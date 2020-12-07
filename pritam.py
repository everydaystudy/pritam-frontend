from flask import Flask, render_template
from flask import request, redirect, url_for
import requests
import json
import datetime
import time


app = Flask(__name__)


backend_url = "165.244.244.229:8001"

def return_date_of_week(d):

    y = d.year

    w = d.isocalendar()[1] - 2 # as it starts with 0 and you want week to start from sunday
    if w < 0:
        w = 0

    startdate = time.asctime(time.strptime('%d %d 0' % (y, w), '%Y %W %w')) 
    startdate = datetime.datetime.strptime(startdate, '%a %b %d %H:%M:%S %Y') 
    dates = [startdate.strftime('%Y-%m-%d')] 
    for i in range(1, 7): 
        day = startdate + datetime.timedelta(days=i)
        dates.append(day.strftime('%m/%d')) 

    dates = dates[1:6]

    return dates


@app.route('/tams', methods=['GET', 'POST'])
def tam_main():

    division = request.args.get('division')
    team = request.args.get('team')
    today = request.args.get('today')

    if division == None:
        division = "제조/개발DX솔루션"

    if team == None:
        team = "AI솔루션"

    if today == None:
        today = datetime.datetime.today().strftime('%Y-%m-%d')

    d = datetime.datetime.strptime(today, '%Y-%m-%d')
    dates = return_date_of_week(d)

    d7 = (d + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    dplusseven = datetime.datetime.strptime(d7, '%Y-%m-%d')

    nextweek = return_date_of_week(dplusseven)
    inputdates = dates + nextweek

    url_items = "http://%s/tam_data?division=%s&team=%s&today=%s" % (backend_url, division, team, today)
    response = requests.get(url_items)
    tam_data = json.loads(response.text)

    url_items = "http://%s/tam_data?division=%s&team=%s&today=%s" % (backend_url, division, team, d7)
    response = requests.get(url_items)
    next_tam_data = json.loads(response.text)

    attend_data = []
    destn_data = []
    for i in range(len(tam_data)):
        attend_data.append([tam_data[i][3][0], tam_data[i][4][0], tam_data[i][5][0], tam_data[i][6][0], tam_data[i][7][0],
                           next_tam_data[i][3][0], next_tam_data[i][4][0], next_tam_data[i][5][0], next_tam_data[i][6][0], next_tam_data[i][7][0]])

        destn_data.append([tam_data[i][3][1], tam_data[i][4][1], tam_data[i][5][1], tam_data[i][6][1], tam_data[i][7][1],
                           next_tam_data[i][3][1], next_tam_data[i][4][1], next_tam_data[i][5][1], next_tam_data[i][6][1], next_tam_data[i][7][1]])

    return render_template('tam.html', tam_data=tam_data, 
                                       dates=dates, 
                                       formdata=[division, team, today],
                                       inputdates=inputdates, 
                                       attend_data=attend_data, 
                                       destn_data=destn_data, 
                                       data_cnt=len(tam_data))


@app.route('/today_info', methods=['GET', 'POST'])
def today_info():

    division = request.args.get('division')
    team = request.args.get('team')
    today = request.args.get('today')

    if division == None:
        division = "제조/개발DX솔루션"

    if team == None:
        team = "AI솔루션"

    if today == None:
        today = datetime.datetime.today().strftime('%Y-%m-%d')

    # Business Trip Member
    url_items = "http://%s/today_biztrip?division=%s&team=%s&today=%s" % (backend_url, division, team, today)
    response = requests.get(url_items)
    biztrip_lst = json.loads(response.text)

    # Work from Home Member
    url_items = "http://%s/today_wfh?division=%s&team=%s&today=%s" % (backend_url, division, team, today)
    response = requests.get(url_items)
    wfh_lst = json.loads(response.text)

    return render_template('today_info.html', biztrip_lst=biztrip_lst, wfh_lst=wfh_lst, formdata=[division, team, today])


@app.route('/tam_chart', methods=['GET', 'POST'])
def tam_chart():

    division = request.args.get('division')
    team = request.args.get('team')
    today = request.args.get('today')

    if division == None:
        division = "제조/개발DX솔루션"

    if team == None:
        team = "AI솔루션"

    if today == None:
        today = datetime.datetime.today().strftime('%Y-%m-%d')

    # Work from Home Rate
    url_items = "http://%s/wfh_rate?division=%s&team=%s&today=%s" % (backend_url, division, team,today)
    response = requests.get(url_items)
    wfh_rate_lst = json.loads(response.text)

    return render_template('tam_chart.html', wfh_rate_lst=wfh_rate_lst, formdata=[division, team, today])


@app.route('/data_post', methods=['GET', 'POST'])
def data_post():

    if request.method == "POST":
        data = request.form.to_dict(flat=True)

    requests.post("http://%s/update_data" % backend_url, data=json.dumps(data))

    return redirect(url_for('tam_main'))


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
