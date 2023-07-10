import os
import json
import csv
import time
import requests
import concurrent.futures
import re
import hashlib
import numpy as np
import wget
import threading
from pymongo import MongoClient, errors

lock = threading.Lock()
base_path = os.path.dirname("/media/mlfavorfit/sda/product_img/")
fail_count = 0


client = MongoClient("mongodb://localhost:27018/")
db = client['DBproduct_eng']
collection = db['product_detection_data']


def extract_DBField_from_path(path):
    pattern = r'/([^/]+)/([^/]+)/([^/]+)/([^/]+)/([^/]+)/([^/]+)'
    matches = re.match(pattern, path)

    if matches:
        result = matches.groups()

    return {"start_path":f"{result[0]}/{result[1]}", "HDD_name":f"{result[2]}", "middle_path":f"{result[3]}", "tag":f"{result[4]}", "file_name":f"{result[5]}"}

def check_url_is_img(url):
    try:
        response = requests.get(url, allow_redirects=True)
        content_type = response.headers.get('content-type')

        if 'image' in content_type.lower():
            pattern = r'/(\w+)$'
            match = re.search(pattern, content_type)
            return response, match.group(1)
        
        return False
    
    except Exception as e:
        print(f"An error occurred while checking URL: {url}. Error: {e}")
        return False


def get_img_hash_and_ext(url):
    res, ext = check_url_is_img(url)

    if res == False: raise Exception

    img_vector = np.asarray(bytearray(res.content), dtype=np.uint8)
    img_bytes = img_vector.tobytes()

    hash_object = hashlib.sha256(img_bytes)
    hash_value = hash_object.hexdigest()

    return hash_value, ext


def save_file(url, file_name):
    
    try:
        hash_value, ext = get_img_hash_and_ext(url)
        field_dict = extract_DBField_from_path(file_name)

        document = {
            "hash":hash_value,
            "file_name":field_dict["file_name"],
            "tag":[field_dict["tag"]],
            "HDD_name":field_dict["HDD_name"],
            "start_path":field_dict["start_path"],
            "middle_path":field_dict["middle_path"],
            "source":"unsplash",
            "label":None,
            "ext":ext,
        }

        try:
            collection.insert_one(document)
            wget.download(url, os.path.split(file_name)[0] + field_dict["file_name"])
            
        except errors.DuplicateKeyError as e:
            doc = collection.update_one({'hash': hash_value}, {'$push': {'tag': field_dict["tag"]}})
            
            if doc.raw_result["updatedExisting"]:
                # print('DB HASH INDEX DUPLE! in ', field_dict["tag"])
                return "DUPLE"
            else:
                print("unknown error")
                raise Exception
            
    except:
        return "ERROR"
    
    return "SUCCESS"
    


def download_img(img_tuple, path, file_name):
    thum_url, real_url = img_tuple

    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except:
        pass
    
    real_status = save_file(real_url, path + file_name)

    if real_status == "SUCCESS":
        return 1
    elif real_status == "DUPLE":
        return 3
    elif real_status == "ERROR":
        pass
    
    thum_status = save_file(thum_url, path + file_name)
    
    if thum_status  == "SUCCESS":
        return 2
    elif thum_status == "DUPLE":
        return 3
    elif thum_status == "ERROR":
        pass

    return 0

    
def get_path(category):
    direcotr_name = re.split('[<>]', category)
    path_list = [re.sub(f'[\\/:\*\?"<>|\s]', '', cur) for cur in direcotr_name]

    result = "/"
    for cur in path_list: result += cur + "/"
    
    return result

def apply_regex(text):
    return re.sub(f'[\\/:\*\?"<>|\s]', '', text)

    
# 리스트의 길이를 N개로 분할하고자 하는 길이로 나눕니다. 병렬처리를 위한 함수입니다.
def split_list(lst, n):

    size = len(lst) // n
    result = []

    for i in range(n):
        result.append(lst[i*size:(i+1)*size])
    return result

if __name__ == "__main__":


    num_processes = 8
    num_threads = 2
    start_time = time.time()

    url_jsonfile_path = "../url_crawler/output/unsplash_tag_url_8000/"
    file_list = os.listdir(url_jsonfile_path)

    continue_skip = True
    # continue_skip = False
    last_category = "presentation.json"
    
    for file in file_list:
        if continue_skip:
            
            if file == last_category:
                continue_skip = False

            print(file, "skip")
            continue

        print(file)
        start_time = time.time()




        with open(url_jsonfile_path + file, mode="r", encoding="utf-8") as f:
            vendor_list = json.load(f)

        img_url_list = [(cur["thum"], cur["real"]) for cur in vendor_list]

        img_length = len(img_url_list)
        path = get_path(vendor_list[0]["search_word"])

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_processes) as executor:
            succ_list = executor.map(download_img, 
                                    img_url_list,   # image url
                                    [base_path + path] * img_length, # path
                                    [str(cur["index"]) + "_" + apply_regex(cur["describe"])[:5] for cur in vendor_list])    # filename
            




        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(" 걸린시간: ", elapsed_time)

        fail_count = 0
        total_count = 0
        real_count = 0 
        thum_count = 0
        dupl_count = 0

        for cur in list(succ_list):
            total_count += 1

            if cur == 1:
                real_count += 1
            elif cur == 2:
                thum_count += 1
            elif cur == 3:
                dupl_count += 1
            else:
                fail_count += 1
        
        if total_count == 0: continue

        print("failed num : ", fail_count,"/",total_count, f" {round(fail_count/total_count*100, 2)}%", "thum num : ", thum_count, "real num : ", real_count, "dupl num : ", dupl_count)
        print("------------------------------------------------------------------------------------")

        with open('monitoring_0706.txt', mode='a', encoding="utf-8") as f:
            f.write(f'{file},{total_count},{fail_count},{round(fail_count/total_count*100, 2)}%,{elapsed_time},{thum_count},{real_count},{dupl_count}\n')
