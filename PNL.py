loss=20
profit=13
mb=3

brokerage=50
currentTrade=2000*5
maxloss=currentTrade*0.015
maxProfit=currentTrade*0.03
maxMBprofit=currentTrade*0.07

number_of_trades = loss+profit
total = (profit-mb)*maxProfit
total += (mb * maxMBprofit)
total -= loss*maxloss

print("Profit before taxes : " , total)

total -= number_of_trades*brokerage

print("After taxes" ) 

if total>0:
    print("Profit After taxes", total)
else:
    print("Loss after taxes",total)    
