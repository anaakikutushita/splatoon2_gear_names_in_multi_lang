"""SplatoonWikiからギア名の日英対応表をcsvファイルで取得する

"""

import csv
from pathlib import Path
import pprint
from time import sleep
import bs4
import requests

def main():
    # データソースが置いてあるだろうパスを設定
    data_path = Path('./gear_names.csv')

    # データソースのcsvが存在しなければ作成
    if not data_path.exists():
        with data_path.open('w') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow(['en','ja'])

    # データソースから辞書として読み込み
    data_dict = None
    with data_path.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)

        dict_list = [row for row in reader]

        data_dict = dict(zip([row['en'] for row in dict_list], [row['ja'] for row in dict_list]))

    # 全ギア一覧ページを読み込み
    res_all = requests.get('https://splatoonwiki.org/wiki/Checklist_of_gear_in_Splatoon_2')
    res_all.raise_for_status()

    # 個別ギアページへのaタグを取得
    soup_all = bs4.BeautifulSoup(res_all.text, "html.parser")
    a_tags = soup_all.select('#mw-content-text > div > table > tbody > tr > td > a')
    for a_tag in a_tags:
        # aタグからギア名を取得し、ギア名がデータソース中に存在するか確認
        if a_tag.string not in data_dict:
            # 存在しない場合はギアの個別ページを読み込み
            sleep(2)
            res_single = requests.get('https://splatoonwiki.org' + a_tag['href'])
            res_single.raise_for_status()

            pprint.pprint(a_tag['href'])
            # ギアの個別ページから日本語名を取得
            soup_single = bs4.BeautifulSoup(res_single.text, "html.parser")
            ja_name_raw = str(soup_single.select('#mw-content-text > div > table.wikitable.sitecolor-generic > tbody > tr:nth-child(2) > td:nth-child(2)'))
            ja_name_raw += str(soup_single.select('#mw-content-text > div > table.wikitable.sitecolor-s2 > tbody > tr:nth-child(2) > td:nth-child(2)'))

            # 正確に日本語名を取得するために加工
            exclude = ja_name_raw.find('<') + 1
            start = ja_name_raw.find('>', exclude) + 1
            end = ja_name_raw.find('<', exclude)
            pprint.pprint(ja_name_raw)
            ja_name = ja_name_raw[start:end]
            pprint.pprint(ja_name)

            # データソースの最終行に追加
            with data_path.open('a', encoding='utf-8') as f:
                pprint.pprint('adding...' + str([a_tag.string, ja_name]))
                writer = csv.writer(f, lineterminator='\n')
                writer.writerow([a_tag.string, ja_name])
        else:
            # 存在する場合は読みに行くのが無駄なのでスキップ
            pprint.pprint(a_tag.string + 'is already recorded.')


if __name__ == "__main__":
    main()
