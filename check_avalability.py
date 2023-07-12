import requests
import datetime
import warnings

index = 0
failed = 0

def check(apikey, proxies=None):
    print('Key: ' + apikey) 
    subscription_url = "https://api.openai.com/v1/dashboard/billing/subscription"
    headers = {
        "Authorization": "Bearer " + apikey,
        "Content-Type": "application/json"
    }
    subscription_response = requests.get(
        subscription_url, headers=headers, proxies=proxies, verify=False)
    if subscription_response.status_code == 200:
        data = subscription_response.json()
        total = data.get("hard_limit_usd")
    else:
        failed += 1
        print("Usage: Error")
        print()

    start_date = (datetime.datetime.now() -
                  datetime.timedelta(days=99)).strftime("%Y-%m-%d")
    end_date = (datetime.datetime.now() +
                datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    billing_url = f"https://api.openai.com/v1/dashboard/billing/usage?start_date={start_date}&end_date={end_date}"
    billing_response = requests.get(
        billing_url, headers=headers, proxies=proxies, verify=False)
    if billing_response.status_code == 200:
        data = billing_response.json()
        total_usage = data.get("total_usage") / 100
        daily_costs = data.get("daily_costs")
        days = min(5, len(daily_costs))
        recent = f"##### 最近{days}天使用情况  \n"
        for i in range(days):
            cur = daily_costs[-i-1]
            date = datetime.datetime.fromtimestamp(
                cur.get("timestamp")).strftime("%Y-%m-%d")
            line_items = cur.get("line_items")
            cost = 0
            for item in line_items:
                cost += item.get("cost")
            recent += f"\t{date}\t{cost / 100} \n"
    else:
        failed += 1
        print("Usage: Error")
        print()

    print(f"Usage: {total_usage:.2f}/{total:.2f}")
    print()

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    with open('user_info.csv', 'r') as file:
        for line in file:
            if len(line) < 51:
                continue
            apikey = line.strip()[-51:]
            index += 1
            print(f'{index}.')
            proxies = {
                'http': 'http://127.0.0.1:7890',
                'https': 'http://127.0.0.1:7890'
            }
            check(apikey, proxies)
    print(f'Total: {index}')
    print(f'Success: {index - failed}')
    print(f'Failed: {failed}')
