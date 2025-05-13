import os
import glob
import tqdm
import json
import pytz
from datetime import datetime
import math

def set_timestamp(file: str, ctime: float, atime: float):
    """アクセス日時 と 更新日時 を変更"""
    os.utime(path=file, times=(ctime, atime))

def read_json(metadata_json):
    """jsonファイルの読み込み"""
    with open(metadata_json, 'r', encoding='utf-8') as f:
        d = json.load(f)
    return d

def get_timestamp(image_file, json_file):
    """
    指定された画像ファイルに対応するjsonファイルの情報に基づいてタイムスタンプを書き換える
    """
    if not os.path.exists(json_file):
        print(f"警告: 対応するJSONファイルが見つかりません: {json_file}")
        return

    try:
        d = read_json(json_file)
        if "photoTakenTime" in d and "formatted" in d["photoTakenTime"]:
            formatted_time_str = d["photoTakenTime"]["formatted"]
            utc_timezone = pytz.utc
            photo_taken_datetime = utc_timezone.localize(datetime.strptime(formatted_time_str, "%Y/%m/%d %H:%M:%S UTC"))
            photo_taken_timestamp = photo_taken_datetime.timestamp()
            set_timestamp(image_file, photo_taken_timestamp, photo_taken_timestamp)
            print(f"タイムスタンプを変更しました: {image_file}")
        else:
            print(f"警告: JSONファイルに必要な情報が含まれていません: {json_file}")
    except json.JSONDecodeError as e:
        print(f"エラー: JSONファイルの読み込みに失敗しました ({json_file}): {e}")
    except ValueError as e:
        print(f"エラー: 日付形式の解析に失敗しました ({json_file}): {e}")
    except OSError as e:
        print(f"エラー: タイムスタンプの変更に失敗しました ({image_file}): {e}")

def change_timestamp_in_target_dir(target_dir):
    """
    指定されたディレクトリ内の全てのjsonファイルを検索し、
    同名で末尾に1文字追加されたjpg/jpeg/heicファイルを検索してタイムスタンプを書き換える
    """
    json_files = glob.glob(os.path.join(target_dir, "**", "*.json"), recursive=True)

    for json_file in tqdm.tqdm(json_files):
        base_name_json = os.path.splitext(os.path.basename(json_file))[0]
        dirname = os.path.dirname(json_file)

        # 同名 + 1文字のjpg/jpeg/heicファイルを検索
        potential_image_patterns = [
            os.path.join(dirname, f"{base_name_json}?.jpg"),
            os.path.join(dirname, f"{base_name_json}?.jpeg"),
            os.path.join(dirname, f"{base_name_json}?.heic"),
            os.path.join(dirname, f"{base_name_json}?.HEIC"),
        ]

        matched_image_files = []
        for pattern in potential_image_patterns:
            matched_image_files.extend(glob.glob(pattern))

        if matched_image_files:
            # 最初に見つかったファイルを処理 (複数該当する場合は要検討)
            image_file = matched_image_files[0]
            get_timestamp(image_file, json_file)
        else:
            print(f"警告: 対応する画像ファイルが見つかりません (同名 + 1文字): {json_file}")

if __name__ == "__main__":
    import sys
    args = sys.argv

    if len(args) == 2:
        target = args[1]
        if os.path.isfile(target):
            if target.lower().endswith(".json"):
                base_name_json = os.path.splitext(os.path.basename(target))[0]
                dirname = os.path.dirname(target)
                potential_image_patterns = [
                    os.path.join(dirname, f"{base_name_json}?.jpg"),
                    os.path.join(dirname, f"{base_name_json}?.jpeg"),
                    os.path.join(dirname, f"{base_name_json}?.heic"),
                    os.path.join(dirname, f"{base_name_json}?.HEIC"),
                ]
                matched_image_files = []
                for pattern in potential_image_patterns:
                    matched_image_files.extend(glob.glob(pattern))

                if matched_image_files:
                    image_file = matched_image_files[0]
                    print("before")
                    print(get_timestamp(image_file))
                    print("<change timestamp>")
                    get_timestamp(image_file, target)
                    print("after")
                    result = get_timestamp(image_file)
                    if result:
                        print(result)
                else:
                    print(f"警告: 対応する画像ファイルが見つかりません (同名 + 1文字): {target}")
            elif target.lower().endswith((".jpeg", ".jpg", ".heic", ".mp4", ".mov")):
                # 単一の画像ファイルが指定された場合は、以前のロジックでJSONを検索
                matching_json = get_timestamp(target)
                if matching_json:
                    print("before")
                    print(get_timestamp(target))
                    print("<change timestamp>")
                    get_timestamp(target, matching_json)
                    print("after")
                    result = get_timestamp(target)
                    if result:
                        print(result)
                else:
                    print(f"警告: 対応するJSONファイルが見つかりません: {target}")
            else:
                print("エラー: サポートされていないファイル形式です。jpeg、jpg、heic、mp4、mov、または json ファイルを指定してください。")
        elif os.path.isdir(target):
            change_timestamp_in_target_dir(target)
        else:
            print(f"エラー: 指定されたパス '{target}' はファイルまたはディレクトリではありません。")
    else:
        print("使用方法: python timestamp.py <ファイルパスまたはディレクトリパス>")

# 単一ファイル指定時の処理で使用
def find_matching_json(media_file):
    """
    メディアファイル名に基づいて対応する可能性のあるJSONファイルを探索する (MP4 supplemental metadata 対応)
    """
    base_name_media, ext_media = os.path.splitext(media_file)
    dirname = os.path.dirname(media_file)

    potential_json_patterns = [
        f"{base_name_media}.json",
        f"{base_name_media}.supp.json",
        f"{base_name_media}*.json",
        f"{base_name_media}*.supp.json",
        f"{base_name_media}.supplemental-metadata.json",
    ]

    found_json = None
    for pattern in potential_json_patterns:
        json_files = glob.glob(os.path.join(dirname, pattern))
        if json_files:
            found_json = json_files[0]
            break
    return found_json

def get_timestamp(file):
    """作成日時、更新日時、アクセス日時を取得"""
    try:
        ct_u = os.path.getctime(file)
        ct_d = datetime.fromtimestamp(math.floor(ct_u))#日時表記に変換
        mt_u = os.path.getmtime(file)
        mt_d = datetime.fromtimestamp(math.floor(mt_u))
        at_u = os.path.getatime(file)
        at_d = datetime.fromtimestamp(math.floor(at_u))
        return ct_d, mt_d, at_d
    except OSError as e:
        print(f"エラー: {file} - {e}")
        return None, None, None