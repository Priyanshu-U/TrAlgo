from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required,current_user
from datetime import  date,datetime
from dateutil.relativedelta import relativedelta
from jugaad_data.nse import stock_df,index_df
import pandas as pd
import numpy as np
from nsetools import Nse
import plotly.graph_objects as go
import plotly.io as pio
pio.templates.default = "plotly_dark"
from .models import Card,Bio,Pred
from . import db
import pytz
views = Blueprint('views', __name__)
nse = Nse()


def stonks(df):        
    returnVal=0
    df.drop(['SERIES', 
        'VWAP', '52W H', '52W L', 'VOLUME', 'VALUE', 'NO OF TRADES', 'SYMBOL'],inplace=True,axis=1)
    df=df[::-1]
    df=df.reset_index()
    pd.options.display.max_columns = None
    emadf = pd.DataFrame({'CLOSE':df['CLOSE']})
    emadf['EMA100'] = emadf['CLOSE'].ewm(span=100, min_periods=0, adjust=True).mean()
    emadf['EMA50'] = emadf['CLOSE'].ewm(span=50, min_periods=0, adjust=True).mean()
    ema100 = emadf['EMA100'].iloc[-1]
    ema50 = emadf['EMA50'].iloc[-1]
    rsidf = pd.DataFrame({'CLOSE':df['CLOSE']})
    def rma(x, n, y0):
        a = (n-1) / n
        ak = a**np.arange(len(x)-1, -1, -1)
        return np.r_[np.full(n, np.nan), y0, np.cumsum(ak * x) / ak / n + y0 * a**np.arange(1, len(x)+1)]
    n=14
    rsidf['change'] = rsidf['CLOSE'].diff()
    rsidf['change'][0] = 0
    rsidf['gain'] = rsidf.change.mask(rsidf.change < 0, 0.0)
    rsidf['loss'] = -rsidf.change.mask(rsidf.change > 0, -0.0)
    rsidf['avg_gain'] = rma(rsidf.gain[n+1:].to_numpy(), n, np.nansum(rsidf.gain.to_numpy()[:n+1])/n)
    rsidf['avg_loss'] = rma(rsidf.loss[n+1:].to_numpy(), n, np.nansum(rsidf.loss.to_numpy()[:n+1])/n)
    rsidf['rs'] = rsidf.avg_gain / rsidf.avg_loss
    rsidf['rsi_14'] = 100 - (100 / (1 + rsidf.rs))
    rsi = rsidf['rsi_14'][99]
    sodf = pd.DataFrame(df[-14::]) # get latest 14 days
    c = sodf['CLOSE'].iloc[-1]
    l = sodf['LOW'].min()
    h = sodf['HIGH'].max()
    so = (c-l)/(h-l) * 100
    delta = df['CLOSE'].diff()
    up = delta.clip(lower=0)
    down = -1*delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=True).mean()
    ema_down = down.ewm(com=13, adjust=True).mean()
    df['RSI'] = 100 - (100/(1 + (ema_up/ema_down)))
    if (ema50>ema100):
        returnVal+=1
    if (rsi<45):
        returnVal+=1
    if (so<20):
        returnVal+=1
    return returnVal
def chart(df,query):
    fig = go.Figure(data=[go.Candlestick(x=df['DATE'],
                open=df['OPEN'], high=df['HIGH'],
                low=df['LOW'], close=df['CLOSE'])])
   
    fig.update_layout(xaxis_rangeslider_visible=False,title= query+' Candlestick Plot')
    
    return fig
def nifty_chart(df):
    fig = go.Figure(data=[go.Candlestick(x=df['HistoricalDate'],
                open=df['OPEN'], high=df['HIGH'],
                low=df['LOW'], close=df['CLOSE'])
                     ])
    
    fig.update_layout(xaxis_rangeslider_visible=False,title='Nifty 50 Candlestick Plot')
    
    return fig
def mlmodel():
    df = index_df(symbol="NIFTY 50", from_date=date(2016,1,1),to_date=date(2021,6,30))
    df=df[::-1]
    training_set=df.iloc[:,6:7].values
    from sklearn.preprocessing import MinMaxScaler
    sc = MinMaxScaler(feature_range=(0, 1))
    scaled_training_set = sc.fit_transform(training_set)
    X_train = []
    y_train = []
    for i in range(60,len(scaled_training_set)):
        X_train.append(scaled_training_set[i-60:i,0:training_set.shape[1]])
        y_train.append(scaled_training_set[i,0])
    X_train, y_train = np.array(X_train), np.array(y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    y_train= y_train.reshape(-1,1)
    from keras.models import Sequential
    from keras.layers import Dense
    from keras.layers import LSTM
    from keras.layers import Dropout
    regressor = Sequential()
    regressor.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units=50, return_sequences=True))
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units=50, return_sequences=True))
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units=50))
    regressor.add(Dropout(0.2))
    regressor.add(Dense(units=1))
    regressor.compile(optimizer='adam', loss='mean_squared_error')
    regressor.fit(X_train, y_train, epochs=1, batch_size=32)
    df_test = index_df(symbol="NIFTY 50", from_date=date(2021,7,1),to_date=date.today())
    df_test = df_test.iloc[::-1]
    # real_stock_prices = df_test.iloc[:,6:7].values
    df_total = pd.concat((df["CLOSE"],df_test["CLOSE"]),axis = 0)
    inputs = df_total[len(df_total)-len(df_test)-60:].values
    inputs = inputs.reshape(-1,1)
    inputs = sc.transform(inputs)
    X_test = []
    for i in range(60,inputs.shape[0]):
        X_test.append(inputs[i-60:i,0])
    X_test= np.array(X_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    predicted_stock_price = regressor.predict(X_test)
    predicted_stock_price = sc.inverse_transform(predicted_stock_price)
    next_data = [inputs[len(inputs)-60:len(inputs+1),0]]
    next_data = np.array(next_data)
    next_data = np.reshape(next_data,(next_data.shape[0],next_data.shape[1],1))
    pridiction = regressor.predict(next_data)
    pridiction = sc.inverse_transform(pridiction)
    print (pridiction)
    return pridiction


@views.route('/')
def index():
    return render_template('index.html',user=current_user)

@views.route('/contributers')
# @login_required
def about():
    return render_template('contributers.html',user=current_user)

@views.route('/stock',methods=['GET','POST'])
# @login_required
def stock():
    query=""
    data=pd.DataFrame()
    res=-1
    check=0
    if request.method == 'POST':
        query=request.form.get('query').upper()

        if nse.is_valid_code(query)==False:
            flash('Invalid Stock Code',category='error')
            return render_template('stonks.html',query=query,data=data,res=res,check=check,user=current_user)
        elif nse.is_valid_code(query)==True:
            data=stock_df(symbol=query, from_date=date.today()-relativedelta(months=6),to_date=date.today(), series="EQ")
            res=stonks(data) 
            check=1
            if current_user.is_authenticated:
                IST=pytz.timezone('Asia/Kolkata')
                card=Card(query_in=query,user_id=current_user.id,type="Stonk",date=datetime.now(IST).strftime('%d-%m-20%y'),time=datetime.now(IST).strftime('%H:%M:%S'),res=res)  
                db.session.add(card)
                db.session.commit()
                
            return render_template('stonks.html',query=query,res=res,chart=chart(data,query).to_html(),check=check,user=current_user)
        
    return render_template('stonks.html',query=query,data=data,res=res,check=check,user=current_user)
   
@views.route('/nifty',methods=['GET','POST'])
# @login_required
def nifty():
    data=index_df(symbol="NIFTY 50", from_date=date.today()-relativedelta(months=6),to_date=date.today()) 
    if current_user.is_authenticated:
        IST=pytz.timezone('Asia/Kolkata')
        card=Card(query_in="NIFTY 50",user_id=current_user.id,type="Nifty",date=datetime.now(IST).strftime('%d-%m-%Y'),time=datetime.now(IST).strftime('%H:%M:%S'))    
        db.session.add(card)
        db.session.commit()  
    

    return render_template('nifty.html',chart=nifty_chart(data).to_html(),user=current_user)

@views.route('/profile',methods=['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        data=request.form.get('bio')
        bio=Bio(user_id=current_user.id,data=data)
        # print(data)
        # print(bio.data)
        db.session.add(bio)
        db.session.commit()
    return render_template('profile.html',user=current_user)

@views.route('/delete/<int:id>')
@login_required
def delete_note(id):
    delete_note=Bio.query.get_or_404(id)
    try:    
        db.session.delete(delete_note)
        db.session.commit()
        return redirect(url_for('views.profile'))
    except:
        return "error"

@views.route('/deletehistory')
@login_required
def delete_history():
    if current_user.is_authenticated:
        delete_history=Card.query.filter_by(user_id=current_user.id).all()
        for i in delete_history:
            db.session.delete(i)
            db.session.commit()
        return redirect(url_for('views.profile'))
    else:
        return redirect(url_for('views.index'))
  

@views.route('/nifty/prediction')
@login_required
def prediction():
    # if Pred has an entry for today
    t=Pred.query.filter_by(date=str(date.today())).first()
    if t is not None:
        pred=t.data
    else:
        pred=str(mlmodel()[0,0])
        t=Pred(date=str(date.today()),data=pred)
        db.session.add(t)
        db.session.commit()
    return render_template('prediction.html',pred=pred,user=current_user)

