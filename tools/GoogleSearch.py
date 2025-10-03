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


def getSearchResponse(keyword: str, DATA_DIR: str,
                      GOOGLE_API_KEY: str = api_key,
                      CUSTOM_SEARCH_ENGINE_ID: str = cx) -> list[str]:
    today = datetime.datetime.today().strftime("%Y%m%d")
    timestamp = datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S")

    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)

    page_limit = 10
    start_index = 1
    response = []
    urls: list[str] = []

    for n_page in range(0, page_limit):
        try:
            sleep(1)
            resp = service.cse().list(
                q=keyword,
                cx=CUSTOM_SEARCH_ENGINE_ID,
                num=10,
                start=start_index
            ).execute()
            response.append(resp)

            # URL 抽出：resp の 'items' リストから 'link' を取る
            items = resp.get("items", [])
            for it in items:
                link = it.get("link")
                if link:
                    urls.append(link)

            # 次のページインデックス
            next_q = resp.get("queries", {}).get("nextPage")
            if next_q and isinstance(next_q, list) and next_q:
                start_index = next_q[0].get("startIndex", None)
                if start_index is None:
                    break
            else:
                break

        except Exception as e:
            print("Search API error:", e)
            break

    # （オプション）レスポンス全体を json 保存する処理を残すか削るか
    save_response_dir = DATA_DIR
    out = {
        'snapshot_ymd': today,
        'snapshot_timestamp': timestamp,
        'response': response
    }
    jsonstr = json.dumps(out, ensure_ascii=False)
    with open(os.path.join(save_response_dir, 'response_' + today + '.json'), mode='w', encoding='utf-8') as response_file:
        response_file.write(jsonstr)

    # 最終的に URL リストを返す
    return urls


if __name__ == "__main__":
    # 動作確認用コード
    test_keyword = "ZnO 極性表面"
    test_data_dir = "/workspaces/PaperInterpreter/PhysRevB_68_245409"
    result_urls = getSearchResponse(test_keyword, test_data_dir)
    print("Search results:")
    for url in result_urls:
        print(url)
