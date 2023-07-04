import requests
import json
from bs4 import BeautifulSoup
import concurrent.futures
import threading

base_url = "https://unsplash.com/s/photos/"
lock = threading.Lock()

visited_category = set()
img_num_dict = {}
node_and_edge = {}

def get_related_category(search_category):
    global visited_category
    global node_and_edge
    global img_num_dict

    res = requests.get(base_url + search_category)
    bs4 = BeautifulSoup(res.text, "html.parser")
    # driver.get(base_url + search_category)
    
    # eles = bs4.select(".f9Vut div a") # 한국
    eles = bs4.select(".FqUkp div a")   # 영어
    try:
        img_num = bs4.select(".Uie4J")[0].text
    except:
        print(search_category)
        img_num = "NULL"

    # eles = driver.find_elements(By.XPATH, "//div[@class='f9Vut']/div/a")
    related_category = [cur.text for cur in eles]

    with lock:
        visited_category.add(search_category)
        related_newface_category = [cur for cur in related_category if cur not in visited_category]

        node_and_edge[search_category] = related_category
        img_num_dict[search_category] = img_num

        if len(visited_category) % 10 == 1:
            print("crawled_category_num : ", len(visited_category))
        elif len(visited_category) >= 20000:
            return []

    return related_newface_category

def recursive_get_category(not_visited_category_list):

    if not_visited_category_list != 0: 

        for category in not_visited_category_list:
            related_category = get_related_category(category)
            recursive_get_category(related_category)
    else:
        return

if __name__ == "__main__":
    thread_num = 7

    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_num) as executor:
        succ_list = executor.map(recursive_get_category, [["clothes"], ["cosmetic"], ["food"], ["Household goods"], ["interior"], ["Electronic products"], ["hobby"]])

    # Write the JSON string to a file
    with open('./category/nodes.txt', 'w',encoding="utf-8") as f:
        for cur in visited_category:
            f.write(cur)
            f.write("\n")

    with open("./category/edges.json", mode="w",encoding="utf-8") as f:
        json.dump(node_and_edge, f, ensure_ascii= False, indent=4)

    with open("./category/img_num_for_tag.json", mode="w",encoding="utf-8") as f:
        json.dump(img_num_dict, f, ensure_ascii= False, indent=4)
