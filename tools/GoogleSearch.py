from dotenv import load_dotenv
import os
import datetime
import json

from time import sleep
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# .env ファイルを探して読み込む（デフォルトは実行ディレクトリかプロジェクトルート）
load_dotenv('/workspaces/PaperInterpreter/.github/.env')

# 読み込んだ環境変数を取得
api_key = os.getenv("GOOGLE_API_KEY")
cx = os.getenv("GOOGLE_CSE_ID")
if api_key is None or cx is None:
    raise RuntimeError("Google API key or CX missing in environment")


def getSearchResponse(keyword: str, DATA_DIR: str, GOOGLE_API_KEY: str = api_key, CUSTOM_SEARCH_ENGINE_ID: str = cx):
    today = datetime.datetime.today().strftime("%Y%m%d")
    timestamp = datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S")

    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)

    page_limit = 10
    start_index = 1
    response = []
    for n_page in range(0, page_limit):
        try:
            sleep(1)
            response.append(service.cse().list(
                q=keyword,
                cx=CUSTOM_SEARCH_ENGINE_ID,
                lr='lang_ja',
                num=10,
                start=start_index
            ).execute())
            start_index = response[n_page].get("queries").get("nextPage")[
                0].get("startIndex")
        except Exception as e:
            print(e)
            break

    # レスポンスをjson形式で保存
    save_response_dir = DATA_DIR
    out = {'snapshot_ymd': today, 'snapshot_timestamp': timestamp, 'response': []}
    out['response'] = response
    jsonstr = json.dumps(out, ensure_ascii=False)
    with open(os.path.join(save_response_dir, 'response_' + today + '.json'), mode='w') as response_file:
        response_file.write(jsonstr)
