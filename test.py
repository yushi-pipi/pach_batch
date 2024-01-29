import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions, ui
import re
import ast
import os
import time
from dataclasses import dataclass, field


@dataclass
class PachiMachine:
    id: int
    end_time: str
    end_point: int
    hit_log: dict = field(default=None)


def scraping_get_pachi_info(url: str, machine_kind: str):

    # LINK先への移動
    def move_link(link_text):
        # LINK_TEXT：完全一致、PARTIAL_LINK_TEXT：部分一致
        browser.find_element(By.PARTIAL_LINK_TEXT, link_text).click()
        print(browser.title)  # 移動確認用

    # <script>内のhtml要素からvar dataの値を配列として取得

    def get_graph_datalist_in_script(xpath='//*[@id="Main-Contents"]/script[9]'):
        script = browser.find_element(By.XPATH, xpath)
        javascript_code = script.get_attribute("innerHTML")
        # 正規表現を使用して変数dataの値を抽出
        match = re.search(r'\bvar\s+data\s*=\s*(.*?);\s*',
                          javascript_code, re.DOTALL)
        if match:
            data_string = match.group(1)
            # 取得した文字列をPythonのリストとして評価
            data_list = ast.literal_eval(data_string)
            # 結果を出力
            # print("data変数の値:", data_list)
        else:
            print("data変数が見つかりませんでした")

        return data_list

    # docker使用時のwebdriver設定 ###################################################
    options = webdriver.ChromeOptions()
    options.add_argument('--lang=ja-JP')
    options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36')
    

    max_retries = 3
    retry_delay = 5

    for _ in range(max_retries):
        try:
            browser = webdriver.Remote(
                command_executor=os.environ["SELENIUM_URL"],
                options=options
            )
            break  # If no error occurs, exit the loop
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Retrying in 10 seconds...")
            time.sleep(retry_delay)
    else:
        print("Max retries exceeded. Unable to create webdriver.")

    #################################################################################

    # ローカル実行時のwebdriver設定 ###################################################
    #CHROMEDRIVER = "./chromedriver.exe"
    # ドライバー指定でChromeブラウザを開く
    #chrome_service = fs.Service(executable_path=CHROMEDRIVER)
    #browser = webdriver.Chrome(service=chrome_service)
    #################################################################################

    browser.implicitly_wait(5)  # 要素が見つからるまで最大　引数秒待つ
    browser.get(url)
    print(url)

    try:
        if len(browser.find_elements(By.XPATH, "//button[text()='利用規約に同意する']")):
            # 利用規約への同意が必要な場合には同意処理を入れる
            browser.find_element(
                By.XPATH, "//button[text()='利用規約に同意する']").click()

        if len(browser.find_elements(By.XPATH, '//*[@id="gn_interstitial_close_icon"]')):
            # 広告がある場合
            browser.get(url)
        # ----- ここまでが店舗トップへの移動処理 -----

        # 店舗トップ -> 機種一覧
        move_link("機種別で探す")

        # 機種一覧 -> 個別機種ページ
        move_link(machine_kind)

        # 個別機種ページ -> 台番号
        unit_table = browser.find_element(By.CLASS_NAME, "tablesorter")
        unit_body = unit_table.find_element(By.TAG_NAME, "tbody")  # テーブルの情報を取得
        units = unit_body.find_elements(By.TAG_NAME, "tr")  # 各行の情報を取得

        dai_id_list = []
        count = 0
        for unit in units:
            # 1行ずつ解体
            unit_informations = unit.find_elements(By.TAG_NAME, "td")
            dai_id_list.append(unit_informations[1].text)

        pachi_machine_info_list = []
        # 台ごとの詳細情報取得用　繰り返し文
        for id in dai_id_list:
            # TODO:台番号をクリック(数字が重複するとバグるかも)
            # 各台の詳細情報まで移動
            browser.find_element(By.LINK_TEXT, id).click()

            # TODO: テーブル情報取得処理 ####################################################
            # 台の詳細テーブル情報の取得を行う
            #################################################################################

            # グラフ情報取得処理 ############################################################
            ep = get_graph_datalist_in_script(
                '//*[@id="Main-Contents"]/script[9]')[-1][-1]
            print(f"台番号:{id}")
            print(f"日ごとの最終値:{ep}")
            #################################################################################

            # データ収集
            pachi_machine_info_list.append(PachiMachine(
                id=id, end_time=ep[0], end_point=ep[1]))

            browser.back()
            count += 1
            if count > 2:
                break

    except (Exception):
        import traceback
        traceback.print_exc()

    browser.quit()  # ブラウザを閉じる
    return pachi_machine_info_list


url = 'https://daidata.goraggio.com/'

# TODO:店舗、機種は自動取得機能が必要であれば改修する(いまのところ手動指定)
shop_ids = ["100946"]  # TODO:店舗とIDのdictの方がわかりやすければ変更
#machine_kinds = ["P新世ｴｳﾞｧ15未来への咆哮", "P大海物語5 MTE2"]
machine_kinds = ["P新世ｴｳﾞｧ15未来への咆哮"]

result = {sid: {mk: scraping_get_pachi_info(os.path.join(
    url, sid), mk) for mk in machine_kinds} for sid in shop_ids}
print(result)
