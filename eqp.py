#!/bin/python3

import os
import sys
from operator import itemgetter

# Complete the function below.
def isIntFromStr(v):
    v = str(v).strip()
    return v=='0' or (v.rstrip('0').rstrip('.')).isdigit()

def processQueries(queries):
    # Write your code here.
    resp = [];qno = 0;prevtime=-1;
    mbook = [];symbn = 0;symst = {};# symbol storage which stores the index
    symbuy = []; symsell = [];done = [];

    for query in queries:
        q = query.split(",")
        flag = 0;stat = "";
        if(q[0] == 'N'):
            #check for duplicate order id
            orderid = q[1];
            for entry in mbook:
                if(entry["id"] == orderid):
                     flag = 1;#resp.append("id")
            if(not isIntFromStr(q[7])):
                 flag = 1;#resp.append("notint")
            ordrt = q[4];
            if(ordrt == 'I' or ordrt == 'M' or ordrt == 'L' ):
                flag += 0;
            else:
                flag = 1;
            ordrside = q[5];
            if(ordrside == 'B' or ordrside == 'S'):
                flag += 0;
            else:
                flag = 1;
            #checking for incorrect time
            timestamp = int(q[2])
            if(timestamp >= prevtime):
                prevtime = timestamp;
            else:
                flag = 1;
            # resp.append(str(timestamp))
            if(flag == 0):
                mbook.append({"id":q[1], "time":timestamp, "symb":q[3], "otype":q[4], "side":q[5], "price":q[6], "quantity":q[7]});
                #add it to its symbol's list
                symbl = q[3];#symbol
                if(symbl in symst):
                    symlnum = symst[symbl];
                else:
                    symlnum = symbn;
                    symbn += 1;#increase the count of number of unique keys-1
                    symst[symbl] = symlnum;
                    empty_list = []
                    symbuy.append(empty_list[:])
                    symsell.append(empty_list[:])
                # now symlnum stores the index for that symb
                notmarketorder = True;
                ordrqty = int(q[7]);
                oprice = float(q[6]);negprice = oprice*-1;
                if(ordrt == 'M'):
                    notmarketorder = False;
                if(ordrside == 'B'):
                    #buy order
                    symbuy[symlnum].append({"id":q[1], "time":timestamp, "notmarket":notmarketorder,"otype":q[4], "revprice":negprice, "price":oprice, "quantity":ordrqty});

                else:
                    #sale order
                    symsell[symlnum].append({"id":q[1], "time":timestamp, "notmarket":notmarketorder, "otype":q[4], "price":oprice, "quantity":ordrqty});



            if(flag == 0):
                stat = "Accept"
            else:
                stat = "Reject - 303 - Invalid order details"
            resp.append(orderid + " - " + stat)
            # resp.append(" - " + str(flag))
            qno += 1;
        elif(q[0] == 'A'):
            flag = 0;
            #checking for incorrect time

            ordrt = q[4];
            if(ordrt == 'I' or ordrt == 'M' or ordrt == 'L' ):
                flag += 0;
            else:
                flag = 1;
            ordrside = q[5];
            if(ordrside == 'B' or ordrside == 'S'):
                flag += 0;
            else:
                flag = 1;
            if(not isIntFromStr(q[7])):
                 flag = 1;#resp.append("notint")
            orderid = q[1];
            flag1 = 2;
            for entry in mbook:
                if(entry["id"] == orderid):
                     flag1 = 0;#resp.append("id")
            if(flag1 == 2):
                flag = 2;
            #check if order is completed
            for doned in done:
                if(orderid == doned):
                    flag = 2;
            ##
            timestamp = int(q[2])
            if(timestamp >= prevtime):
                prevtime = timestamp;
            else:
                flag = 1;

            if(flag == 0):
                for entry in mbook:
                    if(entry["id"] == orderid):
                        #check for others
                        if(entry["symb"] != q[3]):
                            flag = 1;
                        if(entry["otype"] != q[4]):
                            flag = 1;
                        if(entry["side"] != q[5]):
                            flag = 1;
                        orgqty = entry["quantity"]
                        break;
                #check further upon order
            if(flag == 0):
                #process the ammend
                amsym = q[3];
                amprice = float(q[6]);
                amqty = int(q[7]);
                #find the symn for symbol
                amsyn = symst[amsym];
                if(ordrside == 'B'):
                    for orders in symbuy[amsyn]:
                        if(orders["id"] == orderid):
                            #change price
                            orders["price"] = amprice;
                            if(orders["quantity"] >= amqty):
                                orders["quantity"] = amqty;
                            else:
                                #close order
                                orders["quantity"] = 0;
                    templist = [];
                    for orders in symbuy[amsyn]:
                        if(orders["quantity"] > 0):
                            templist.append(orders)
                        else:
                            done.append(orders["id"])
                    symsell[symbn] = templist;
                else:
                    for orders in symsell[amsyn]:
                        if(orders["id"] == orderid):
                            #change price
                            orders["price"] = amprice;
                            if(orders["quantity"] >= amqty):
                                orders["quantity"] = amqty;
                            else:
                                #close order
                                orders["quantity"] = 0;
                    templist = [];
                    for orders in symsell[amsyn]:
                        if(orders["quantity"] > 0):
                            templist.append(orders)
                        else:
                            done.append(orders["id"])
                    symsell[symbn] = templist;
            if(flag == 0):
                stat = " - AmmendAccept"
            elif(flag == 1):
                stat = " - AmmendReject - 101 - Invalid amendment details"
            elif(flag == 2):
                stat = " - AmmendReject - 404 - Order does not exist"
            resp.append(orderid + stat)
        elif(q[0] == 'M'):
            #match items
            # flag = 0;
            timestamp = int(q[1])
            if(timestamp >= prevtime):
                prevtime = timestamp;
            # else:
            #     flag = 1;

            if(len(q) == 2):
                #match everything
                #first sort all buy and sell lists
                for msym in sorted(symst.keys()):
                    symbn = symst[msym];
                    #sort buy list for that symbn
                    #revprice sorts in descending order
                    symbuy[symbn].sort(key = itemgetter('notmarket','revprice','time'));
                    #for sale we need only ascending order sort
                    symsell[symbn].sort(key = itemgetter('notmarket','price','time'));

                    #Now try to match buy and sells
                    #first try for Market orders
                    for orders in symbuy[symbn]:
                        if(orders["otype"] == 'M'):
                            #match it with sale orders
                            buyqty = orders["quantity"];
                            for sorder in symsell[symbn]:
                                if(buyqty <= sorder["quantity"]):
                                    #print match
                                    mstring = msym + '|' + orders["id"] + ',M,' + str(buyqty) + ','+"{0:.2f}".format(sorder["price"])  + '|' + "{0:.2f}".format(sorder["price"])+ ','+ str(buyqty) + ',L,' + sorder["id"];
                                    resp.append(mstring);
                                    #update the sale order quantity
                                    sorder["quantity"] = sorder["quantity"] - buyqty;
                                    #delete this market buy order LATER $$$$$$$$REMEMBER TO DO THIS$$$$$$$
                                    orders["quantity"] = 0;
                                    break;
                                else:
                                    buyqty -= sorder["quantity"]
                                    mstring = msym + '|' + orders["id"] + ',M,' + sorder["quantity"] + ','+"{0:.2f}".format(sorder["price"])  + '|' + "{0:.2f}".format(sorder["price"])+ ','+ sorder["quantity"] + ',L,' + sorder["id"];
                                    resp.append(mstring);
                                    #update the sale order quantity
                                    sorder["quantity"] = 0;
                                    #delete 0 quantity orders LATER $$$$$$$$REMEMBER TO DO THIS$$$$$$$
                            templist = [];
                            for orders in symsell[symbn]:
                                if(orders["quantity"] > 0):
                                    templist.append(orders)
                                else:
                                    done.append(orders["id"])
                            symsell[symbn] = templist;
                    #matching market sale orders
                    for orders in symsell[symbn]:
                        if(orders["otype"] == 'M'):
                            #match it with buy orders
                            sellqty = orders["quantity"];
                            for buyorder in symbuy[symbn]:
                                if(sellqty <= buyorder["quantity"]):
                                    #print match
                                    mstring = msym +  '|' + buyorder["id"] + ',L,' + str(sellqty) +',' + "{0:.2f}".format(buyorder["price"])  + '|' + "{0:.2f}".format(buyorder["price"])  +',' + str(sellqty)+ ',M,' + orders["id"]   ;
                                    resp.append(mstring);
                                    #update the sale order quantity
                                    buyorder["quantity"] = buyorder["quantity"] - sellqty;
                                    #delete this market buy order LATER $$$$$$$$REMEMBER TO DO THIS$$$$$$$
                                    orders["quantity"] = 0;
                                    break;
                                else:
                                    sellqty -= buyorder["quantity"]
                                    mstring = msym +  '|' + buyorder["id"] + ',L,' + buyorder["quantity"] +',' + "{0:.2f}".format(buyorder["price"])  + '|' + "{0:.2f}".format(buyorder["price"])  +',' + buyorder["quantity"] + ',M,' + orders["id"]   ;
                                    resp.append(mstring);
                                    #update the sale order quantity
                                    buyorder["quantity"] = 0;
                                    #delete 0 quantity orders LATER $$$$$$$$REMEMBER TO DO THIS$$$$$$$
                            templists = []
                            for orders in symbuy[symbn]:
                                if(orders["quantity"] > 0):
                                    templists.append(orders)
                                else:
                                    done.append(orders["id"])
                            symbuy[symbn] = templists;
                    #first remove 0 quantity buy and sell orders
                    templist = [];
                    for orders in symsell[symbn]:
                        if(orders["quantity"] > 0):
                            templist.append(orders)
                        else:
                            done.append(orders["id"])
                    symsell[symbn] = templist;
                    templists = []
                    for orders in symbuy[symbn]:
                        if(orders["quantity"] > 0):
                            templists.append(orders)
                        else:
                            done.append(orders["id"])
                    symbuy[symbn] = templists;
                    #now match regular buy and sell orders
                    for orders in symbuy[symbn]:
                        #match it with sale orders
                        maxbuy = orders["price"];
                        for sorder in symsell[symbn]:
                            if(maxbuy >= sorder["price"]):
                                #print match
                                minqty = min(orders["quantity"],sorder["quantity"]);
                                orders["quantity"] = orders["quantity"] - minqty;
                                sorder["quantity"] = sorder["quantity"] - minqty;
                                mstring = msym + '|' + orders["id"] + ',L,' + str(minqty) + ',' + "{0:.2f}".format(maxbuy) + '|' + "{0:.2f}".format(sorder["price"]) +',' + str(minqty) + ',L,' + sorder["id"];
                                resp.append(mstring);
                                #update the sale order quantity
                                sorder["quantity"] = sorder["quantity"] - minqty;
                                orders["price"] = orders["price"] - minqty;
                                #delete this market buy order LATER $$$$$$$$REMEMBER TO DO THIS$$$$$$$
                                if(orders["price"] <= 0):
                                    break;

                        templist = [];
                        for orders in symsell[symbn]:
                            if(orders["quantity"] > 0):
                                templist.append(orders)
                            else:
                                done.append(orders["id"])
                        symsell[symbn] = templist;
                    templists = [];
                    for orders in symbuy[symbn]:
                        if(orders["quantity"] > 0):
                            templists.append(orders)
                        else:
                            done.append(orders["id"])
                    symbuy[symbn] = templists;

            else:
                #match only symbol
                msym = q[2];
                symbn = symst[msym];
                #sort buy list for that symbn
                #revprice sorts in descending order
                symbuy[symbn].sort(key = itemgetter('notmarket','revprice','time'));
                #for sale we need only ascending order sort
                symsell[symbn].sort(key = itemgetter('notmarket','price','time'));
                symbn = symst[msym];
                #sort buy list for that symbn
                #revprice sorts in descending order
                symbuy[symbn].sort(key = itemgetter('notmarket','revprice','time'));
                #for sale we need only ascending order sort
                symsell[symbn].sort(key = itemgetter('notmarket','price','time'));

                #Now try to match buy and sells
                #first try for Market orders
                for orders in symbuy[symbn]:
                    if(orders["otype"] == 'M'):
                        #match it with sale orders
                        buyqty = orders["quantity"];
                        for sorder in symsell[symbn]:
                            if(buyqty <= sorder["quantity"]):
                                #print match
                                mstring = msym + '|' + orders["id"] + ',M,' + str(buyqty) +','+ "{0:.2f}".format(sorder["price"])+ '|' +"{0:.2f}".format(sorder["price"]) + ','+ str(buyqty) + ',L,' + sorder["id"];
                                resp.append(mstring);
                                #update the sale order quantity
                                sorder["quantity"] = sorder["quantity"] - buyqty;
                                #delete this market buy order LATER $$$$$$$$REMEMBER TO DO THIS$$$$$$$
                                orders["quantity"] = 0;
                                break;
                            else:
                                buyqty -= sorder["quantity"]
                                mstring = msym + '|' + orders["id"] + ',M,' + sorder["quantity"] +','+"{0:.2f}".format(sorder["price"])  + '|' + "{0:.2f}".format(sorder["price"])+ ',' + sorder["quantity"] + ',L,' + sorder["id"];
                                resp.append(mstring);
                                #update the sale order quantity
                                sorder["quantity"] = 0;
                                #delete 0 quantity orders LATER $$$$$$$$REMEMBER TO DO THIS$$$$$$$
                        templist = [];
                        for orders in symsell[symbn]:
                            if(orders["quantity"] > 0):
                                templist.append(orders)
                            else:
                                done.append(orders["id"])
                        symsell[symbn] = templist;
                #matching market sale orders
                for orders in symsell[symbn]:
                    if(orders["otype"] == 'M'):
                        #match it with buy orders
                        sellqty = orders["quantity"];
                        for buyorder in symbuy[symbn]:
                            if(sellqty <= buyorder["quantity"]):
                                #print match
                                mstring = msym +  '|' + buyorder["id"] + ',L,' + str(sellqty) +',' + "{0:.2f}".format(buyorder["price"])  + '|' + "{0:.2f}".format(buyorder["price"])  + ','+ str(sellqty)+ ',M,' + orders["id"]   ;
                                resp.append(mstring);
                                #update the sale order quantity
                                buyorder["quantity"] = buyorder["quantity"] - sellqty;
                                #delete this market buy order LATER $$$$$$$$REMEMBER TO DO THIS$$$$$$$
                                orders["quantity"] = 0;
                                break;
                            else:
                                sellqty -= buyorder["quantity"]
                                mstring = msym +  '|' + buyorder["id"] + ',L,' + buyorder["quantity"] + ',' + "{0:.2f}".format(buyorder["price"])  + '|' + "{0:.2f}".format(buyorder["price"])  +','+ buyorder["quantity"] + ',M,' + orders["id"]   ;
                                resp.append(mstring);
                                #update the sale order quantity
                                buyorder["quantity"] = 0;
                                #delete 0 quantity orders LATER $$$$$$$$REMEMBER TO DO THIS$$$$$$$
                        templists = []
                        for orders in symbuy[symbn]:
                            if(orders["quantity"] > 0):
                                templists.append(orders)
                            else:
                                done.append(orders["id"])
                        symbuy[symbn] = templists;
                #first remove 0 quantity buy and sell orders
                templist = [];
                for orders in symsell[symbn]:
                    if(orders["quantity"] > 0):
                        templist.append(orders)
                    else:
                        done.append(orders["id"])
                symsell[symbn] = templist;
                templists = []
                for orders in symbuy[symbn]:
                    if(orders["quantity"] > 0):
                        templists.append(orders)
                    else:
                        done.append(orders["id"])
                symbuy[symbn] = templists;
                #now match regular buy and sell orders
                for orders in symbuy[symbn]:
                    #match it with sale orders
                    maxbuy = orders["price"];
                    for sorder in symsell[symbn]:
                        if(maxbuy >= sorder["price"]):
                            #print match
                            minqty = min(orders["quantity"],sorder["quantity"]);
                            orders["quantity"] = orders["quantity"] - minqty;
                            sorder["quantity"] = sorder["quantity"] - minqty;
                            mstring = msym + '|' + orders["id"] + ',L,' + str(minqty) + ','+ "{0:.2f}".format(maxbuy) + '|' + "{0:.2f}".format(sorder["price"])+ ','+ str(minqty) + ',L,' + sorder["id"];
                            resp.append(mstring);
                            #update the sale order quantity
                            sorder["quantity"] = sorder["quantity"] - minqty;
                            orders["price"] = orders["price"] - minqty;
                            #delete this market buy order LATER $$$$$$$$REMEMBER TO DO THIS$$$$$$$
                            if(orders["price"] <= 0):
                                break;

                    templist = [];
                    for orders in symsell[symbn]:
                        if(orders["quantity"] > 0):
                            templist.append(orders)
                        else:
                            done.append(orders["id"])
                    symsell[symbn] = templist;
                for orders in symbuy[symbn]:
                    if(orders["quantity"] > 0):
                        templists.append(orders);
                    else:
                        done.append(orders["id"])
                symbuy[symbn] = templists;

    # print(symbuy)
    # print(symsell)
    return resp;



f = open("out.txt", 'w')
inp = open("input.txt",)
queries_size = int(inp.readline())
# f.write(str(queries_size))
queries = []
for _ in range(queries_size):
    queries_item = inp.readline()
    queries_item = queries_item.replace('\n','')
    queries.append(queries_item)

response = processQueries(queries)

f.write("\n".join(response))
# f.write("ssHewlldfso")
f.write('\n')

f.close()
