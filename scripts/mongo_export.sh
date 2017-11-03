#!/usr/bin/bash
declare -a arr=("BTC-ETH" "BTC-LTC" "BTC-NEO" "USDT-BTC")

for i in "${arr[@]}"
do
   echo "Exporting $i"
   docker exec franklin_mongo_1 mongoexport --db franklin --collection $i --type=csv --fields MarketName,High,Low,Volume,Last,BaseVolume,Bid,Ask,OpenBuyOrders,OpenSellOrders,PrevDay,Created --out /tmp/dumps/$i.csv
done
