import pandas as pd

prices = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
df = pd.DataFrame(prices)
ema10 = df.ewm(span=10,min_periods=0,adjust=True,ignore_na=False).mean()
print(ema10)
