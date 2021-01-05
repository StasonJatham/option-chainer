def get_options(symbol: str, expiration: str): 
    """
    get_options('TSLA','Jan 15')
    """
    expiry = expiration

    nasdaq_expiry = str(expiry.split(' ')[0]) +' '+ str(int(expiry.split(' ')[1]))
    today = date.today()
    formatted_date = today.strftime("%Y-%m")

    opt_details_list = [] 

    _from = str(formatted_date)+'-'+str(int(expiry.split(' ')[1]))
    _to   = str(formatted_date)+'-30'

    session = requests.session()
    ALL_CONTRATCS = [] 
    for offset in range(0,15):
        offset_scrape = 60 * offset

        options_url = "https://api.nasdaq.com:443/api/quote/"+str(symbol)+"/option-chain?assetclass=stocks&limit=60&offset="+str(offset_scrape)+"&fromdate="+str(_from)+"&todate="+str(_to)+"&excode=oprac&callput=callput&money=all&type=stad&lang=de"
        header = {"Connection": "close", "Accept": "application/json, text/plain, */*", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36", "Origin": "https://www.nasdaq.com", "Sec-Fetch-Site": "same-site", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": "https://www.nasdaq.com/", "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US,en;q=0.9,en-US;q=0.8,en;q=0.7"}
        resp = session.get(options_url, headers=header)

        if resp.status_code == 200:
            generic_options = json.loads(resp.content.decode("utf-8"))


            if generic_options['data']:
                current_symbol_price = generic_options['data']['lastTrade'].split(' ')[2].replace('$','')


                options = generic_options['data']['table']['rows']
                plus500_options_data = plus500_api(symbol)
                strike_list = [strike_o['strike'] for strike_o in plus500_options_data]
                # strike_list = [300,315,320]
                # if you want all strikes just remove strike list here and down there next comment 
                
                try:
                    for contract in options:
                        fmt_expiration = ""
                        if contract['expiryDate']:
                            this_year = dt.strptime(_from, '%Y-%m-%d').year
                            fmt_expirydate  = dt.strptime(contract['expiryDate'].strip()+' '+str(this_year), '%b %d %Y').strftime('%Y-%m-%d')
                            fmt_expiration = dt.strptime(expiration.strip()+' '+str(this_year), '%b %d %Y').strftime('%Y-%m-%d')
                        else:
                            fmt_expirydate = None

                        options_for_strike = {
                            'expirygroup'      : contract['expirygroup'],
                            'expirydate'       : fmt_expirydate,
                            'call_last'        : contract['c_Last'],
                            'call_change'      : contract['c_Change'],  
                            'call_bid'         : contract['c_Bid'],
                            'call_ask'         : contract['c_Ask'],
                            'call_volume'      : contract['c_Volume'], 
                            'call_openinterest': contract['c_Openinterest'], 
                            'strike'           : contract['strike'],
                            'put_last'         : contract['p_Last'],
                            'put_change'       : contract['p_Change'],
                            'put_bid'          : contract['p_Bid'],
                            'put_ask'          : contract['p_Ask'],
                            'put_volume'       : contract['p_Volume'],
                            'put_openinterest' : contract['p_Openinterest'],
                            'details'          : contract['drillDownURL'],
                            'drilldown'        : contract['drillDownURL'].split('/')[-1] if contract['drillDownURL'] else None,
                            'stats'            : {
                                'pct_from_price': "{:.2f}".format(((float(current_symbol_price)-float(contract['strike'])) / float(contract['strike'])) * 100) if contract['strike'] else 0,
                                'curr_underlying_price' : current_symbol_price
                            }
                        }
                        
                        
                        # remove the strike_list if statement here too 
                        if fmt_expiration:
                            if options_for_strike['expirydate'] == _from:
                                if str(options_for_strike['strike']).split('.')[0] in strike_list:
                                    ALL_CONTRATCS.append(options_for_strike)
                        else:
                            if options_for_strike['expirydate'] == expiration:
                                if str(options_for_strike['strike']).split('.')[0] in strike_list:
                                    ALL_CONTRATCS.append(options_for_strike) 

                       
                except TypeError:
                    return ALL_CONTRATCS
