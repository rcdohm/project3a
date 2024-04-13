from flask import Flask, render_template, request, url_for, flash, redirect, abort
import csv
import requests
import matplotlib.pyplot as plt

# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True

#flash  the secret key to secure sessions
app.config['SECRET_KEY'] = 'your secret key'

def get_symbols():
    # open the file in read mode
    filename = open('stocks.csv', 'r')
    
    # creating dictreader object
    file = csv.DictReader(filename)
    
    # creating empty lists
    symbols = []
    name = []
    sector = []
    
    # iterating over each row and append
    # values to empty list
    for col in file:
        symbols.append(col['Symbol'])
        name.append(col['Name'])
        sector.append(col['Sector'])

    return symbols

def query_alpha_vantage(symbol, function, start_date, end_date):
    api_key = "S5VR8PZPBBLCAN6J" 
    base_url = "https://www.alphavantage.co/query"

    params = {
        "function": function,
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": "full",  # Retrieve full data for the range selected
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    return data 

@app.route('/', methods = ['GET','POST'])
def index():
    symbols = get_symbols()
    choice = ""
    interval = "5min"
    
    selectedSymbol = request.form.get("symbol")
    selectedTimeSeries = request.form.get("timeseries")
    selectedStyle = request.form.get("style")
    selectedStartDate = request.form.get("date-start")
    selectedEndDate = request.form.get("date-end")
    
    

    if choice != "Time Series (5min)":
        data = query_alpha_vantage(selectedSymbol, selectedTimeSeries, selectedStartDate, selectedEndDate)
        
    else:
        data = query_alpha_vantage_intraday(selectedSymbol,selectedTimeSeries,selectedStartDate,selectedEndDate,interval)

    

        
    if selectedTimeSeries == "TIME_SERIES_INTRADAY":
        choice = "Time Series (5min)"
    elif selectedTimeSeries == "TIME_SERIES_DAILY":
        choice = "Time Series (Daily)"
    elif selectedTimeSeries == "TIME_SERIES_WEEKLY":
        choice = "Weekly Time Series"
    elif selectedTimeSeries == "TIME_SERIES_MONHTLY":
        choice = "Monthly Time Series"

    
    

    dates = []
    values = []
    for date, value in data[choice].items():
        if selectedStartDate <= date <= selectedEndDate:
         dates.append(date)
         values.append(float(value["4. close"]))  # Assuming closing price is needed

    #Plot the graph
    plot_graph(dates, values, selectedStyle)
    
    
    
    return render_template('index.html',stock_symbols=symbols,selectedSymbol=selectedSymbol,selectedTimeSeries=selectedTimeSeries,data=data,selectedStyle=selectedStyle)



def plot_graph(dates, values, chart_type):
    plt.figure(figsize=(10, 6))
    if chart_type == "1":
        plt.bar(dates, values)
    elif chart_type == "2":
        plt.plot(dates,values)
    plt.title(f"Stock Data ({chart_type})")
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/images/plot.png')

    #return render_template('index.html', url='/static/images/plot.png')

def query_alpha_vantage_intraday(symbol, function, start_date, end_date, interval):
    api_key = "S5VR8PZPBBLCAN6J" 
    base_url = "https://www.alphavantage.co/query"

    params = {
        "function": function,
        "symbol": symbol,
        "apikey": api_key,
        "interval": interval,
        "outputsize": "full",  # Retrieve full data for the range selected
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    return data

app.run(host="0.0.0.0")