from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('tam.html')


@app.route('/today_biztrip')
def today_biztrip():
    return render_template('today_biztrip.html')


@app.route('/tam_chart')
def tam_chart():
    return render_template('tam_chart.html')


if __name__ == '__main__':
    app.run(debug=True)