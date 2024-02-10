import os
from datetime import datetime
import json
import math

def set_timestamp(file:str , ctime:float, atime:float):
    # アクセス日時 と 更新日時 を変更
    os.utime(path=file, times=(ctime, atime))

def read_json(metadata_json):
    # jsonファイルの読み込み
    with open(metadata_json) as f:
        d = json.load(f)
    return d


def get_timestamp(file):
    #作成日時を取得
    ct_u=os.path.getctime(file)
    ct_d=datetime.fromtimestamp(math.floor(ct_u))#日時表記に変換
    #更新日時を取得
    mt_u=os.path.getmtime(file)
    mt_d=datetime.fromtimestamp(math.floor(mt_u))
    #アクセス日時を取得
    at_u=os.path.getatime(file)
    at_d=datetime.fromtimestamp(math.floor(at_u))
    return ct_d, mt_d, at_d

def chage_timestamp(metadata_json):
    '''
    jsonファイルの情報に合わせてタイムスタンプを書き換え
    '''
    # 格納されているディレクトリを取得
    dirname = os.path.dirname(metadata_json)
    # json読み込み
    d = read_json(metadata_json)
    # 入力形式に変更
    ctime = float(d["photoTakenTime"]["timestamp"])
    mtime = float(d["creationTime"]["timestamp"])
    # 対象ファイルを取得
    target_file = os.path.join(dirname, d["title"])
    set_timestamp(target_file, ctime, mtime)


if __name__=="__main__":
    import sys
    args = sys.argv
    file=args[1]
    print("before")
    print(get_timestamp(file))
    print("<change timstamp>")
    print("after")
    chage_timestamp(file+".json")
    print(get_timestamp(file))