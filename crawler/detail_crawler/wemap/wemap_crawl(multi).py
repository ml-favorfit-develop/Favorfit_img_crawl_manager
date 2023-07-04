# 데이터 저장 관련, 타임 딜레이
import re
import time
import json

# 디버그 크롬 실행용
import subprocess
import shutil
from selenium.webdriver.chrome.options import Options

# 셀레니움 웹드라이버 생성용
from selenium import webdriver as wb
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# 셀레니움 부가 기능 불러오기
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 크롬드라이버 자동설치용
import chromedriver_autoinstaller

# 병렬처리
import multiprocessing



# 썸네일 element를 관리하는 클래스
class thumbnail_master():
    driver = None
    action = None
    wait = None
    category_url = None
    thumb_elements = []
    # 카테고리당 목표하는 thumbnail의 개수입니다.
    vendor_num = 0

    def __init__(self, driver, action, wait, vendor_num):
        self.driver = driver
        self.action = action
        self.wait = wait
        self.vendor_num = vendor_num


    # 썸네일을 category_url을 기준으로 클래스에 업데이트 합니다.
    def update_thumbnails(self, category_url):
        self.category_url = category_url
        self.thumb_elements = self.get_thumb_elements()


    # 마우스 스크롤 관련 함수
    def scrolling(self):
        #이동 전 스크롤 위치
        before_location = self.driver.execute_script("return window.pageYOffset")

        while True:
            #현재 위치 + 500으로 스크롤 이동
            self.driver.execute_script("window.scrollTo(0,{})".format(before_location + 1000))
                
            #전체 스크롤이 늘어날 때까지 대기
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.item_img > img.motion-fade.in.loaded")))
            except:
                print("time out")
            time.sleep(0.3)
            
            #이동 후 스크롤 위치
            after_location = self.driver.execute_script("return window.pageYOffset")
            
            #이동후 위치와 이동 후 위치가 같으면(더 이상 스크롤이 늘어나지 않으면) 종료
            if before_location == after_location:
                break

            #같지 않으면 다음 조건 실행
            else:
                #이동여부 판단 기준이 되는 이전 위치 값 수정
                before_location = self.driver.execute_script("return window.pageYOffset")


    # 썸네일 elements들을 가져옵니다.
    def get_thumb_elements(self):
        
        thumb_elements = []
        self.driver.get(f"{self.category_url}")

        # 상품개수가 vendor_num 미만일 때 무한 반복하며 썸네일 element를 탐색합니다.
        while(len(thumb_elements) < self.vendor_num):
            

            # 위메프는 스크롤을 내려야 썸네일의 이미지 src가 로딩됩니다.
            self.scrolling()
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.item_img > img.motion-fade.in.loaded")))
            except:
                print("time out")
            

            # 가장 처음 3개의 썸네일은 광고입니다. 따라서 스킵합니다.
            thum_eles = self.driver.find_elements(By.CSS_SELECTOR, "div.list_conts_wrap > a")[3:]
            thums_ele = [
                        (thum_ele.find_element(By.CSS_SELECTOR,"img").get_attribute("src"), thum_ele.get_attribute("href")) 
                        for thum_ele in thum_eles
                        ]
            thumb_elements.extend(thums_ele)


            # 썸네일 개수가 모자라다면 next버튼을 눌러 다음 페이지로 넘어갑니다.
            try: 
                next_button =self.driver.find_element(By.CSS_SELECTOR,"a.ico.btn_next")
                next_button.click()
            except:
                print("페이지가 더이상 존재하지 않습니다.")
                break
     
        return thumb_elements
    
    # 썸네일 elements의 이미지들을 가져옵니다.
    def get_thumb_imgs(self):
        thumb_imgs = [thumb[0] for thumb in self.thumb_elements]
        return thumb_imgs
    
    # 썸네일 elements의 링크들을 가져옵니다.
    def get_thumb_links(self):
        thumb_links = [thumb[1] for thumb in self.thumb_elements]
        return thumb_links

# 썸네일의 링크로 접속해 이미지들을 저장합니다.
def search_imgs(thumb_links):

    # 포트번호와 썸네일 링크들을 할당합니다.
    port, thumb_links = thumb_links

    # 새로운 드라이버를 생성합니다.
    # wait = WebDriverWait(driver, 3)
    options = Options()
    options.add_argument(f"--user-data-dir=C:/Users/mlfav/for_webcrawl/scop_crawl/chrome-data{port}")
    options.add_argument("--disable-extensions")
    driver = wb.Chrome(options=options)
    driver.implicitly_wait(5)
    print(port, "open")


    # 특정 url에 오류가 있으면 skip합니다.
    # 셀레니움은 웹페이지 자체 결함으로 인한 무한 로딩을 탐지하지 못합니다. 아쉽지만 이 방법밖에 없는 것 같습니다.
    skip_url = ["https://front.wemakeprice.com/product/818132030"]
    
    # 상품 URL 내의 이미지를 탐색하고 list로 반환합니다.
    imgs_data = []
    for thumb_link in thumb_links:

        # skip url일 경우 스킵합니다.
        if thumb_link in skip_url : imgs_data.append([]); continue

        # url을 open하고 이미지를 긁어오는 일련의 과정입니다. 에러발생시 빈 리스트를 리턴합니다.
        try:
            driver.execute_script(f"window.open('{thumb_link}','_self');")
            time.sleep(0.5)
            
            driver.execute_script("window.scrollTo(0, 3000);")
            img_elements = driver.find_elements(By.CSS_SELECTOR, "div.deal_detailimg img")
            imgs_list = [ele.get_attribute('src') for ele in img_elements]

            imgs_data.append(imgs_list)
            driver.switch_to.window(driver.window_handles[-1])

        except:
            print(thumb_link, "에서 에러가 발생했습니다.")
            imgs_data.append([])

    return imgs_data

# 데이터 저장
def save_data(file_name, datas):
    with open(f"./output/{file_name}",'w') as f:
        json.dump(datas, f, ensure_ascii=False, indent=4)


# 초기 드라이버를 디버거 모드로 생성합니다.
def set_init_driver(url):
    init_url = url

    try:
        shutil.rmtree(r"c:\chrometemp")  #쿠키 / 캐쉬파일 삭제
    except FileNotFoundError:
        pass

    # 디버거 크롬 구동
    subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"') 
    option = Options()
    option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    # 크롬 드라이버가 없을 경우 자동 설치합니다.
    chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
    try:
        driver = wb.Chrome(f'./{chrome_ver}/chromedriver.exe', options=option)
    except:
        chromedriver_autoinstaller.install(True)
        driver = wb.Chrome(f'./{chrome_ver}/chromedriver.exe', options=option)
    
    wait = WebDriverWait(driver, 10)
    action = ActionChains(driver)
    driver.implicitly_wait(10)

    driver.get(init_url)

    return driver, wait, action


# 드라이버 닫기
def close_driver(driver):
    driver.close()

# 리스트의 길이를 N개로 분할하고자 하는 길이로 나눕니다. 병렬처리를 위한 함수입니다.
def split_list(lst, n):

    size = len(lst) // n
    result = []

    for i in range(n):
        result.append(lst[i*size:(i+1)*size])
    return result


# 메인함수
if __name__ == '__main__':


    # 위메프 카테고리 url json파일을 엽니다.    ex: {"브랜드패션<브랜드 여성의류<원피스": "https://front.wemakeprice.com/category/division/2100334"}
    with open('Wemap_Category_url.json', encoding="utf-8") as json_file:
        category_dict = json.load(json_file)
    category_list = list(category_dict.items())


    # skip_category를 지정합니다. 해당 카테고리부터 크롤링을 시작합니다.
    skip_bool = False
    skip_category = "브랜드패션<브랜드 쥬얼리/시계<아동용 쥬얼리"


    # 드라이버와 부가기능을 초기화합니다. init URL도 넣어줘야합니다만 어떤 사이트든 상관은 없습니다.
    driver, wait, action = set_init_driver("https://front.wemakeprice.com/main")
    

    # 썸네일 관리자 클래스를 생성합니다.
    thumbnail_master = thumbnail_master(driver, wait, action, vendor_num=1000)


    # 카테고리를 순환하며 크롤링을 시작합니다.
    for category in category_list:

        category, category_url = category

        if skip_bool == False:
            if skip_bool == False and category != skip_category:
                continue
            else:
                skip_bool = True

        print(category)

        # 썸네일 img와 link를 불러옵니다.
        thumbnail_master.update_thumbnails(category_url=category_url)
        thumb_imgs = thumbnail_master.get_thumb_imgs()
        thumb_links = thumbnail_master.get_thumb_links()
        

        # 프로세서 개수를 입력합니다. thumb_links에 포트번호도 함께 할당합니다.
        processor_num = 5
        thumb_links = split_list(thumb_links, processor_num)
        thumb_links = [[9223 + idx, cur]for idx, cur in enumerate(thumb_links)]



        # 병렬처리를 시작합니다.
        with multiprocessing.Pool(processes= processor_num) as pool :
            imgs_data = pool.map(search_imgs, thumb_links)


        # 데이터를 전처리하고 저장합니다.
        imgs_data_test = []
        for cur in imgs_data:
            for a in cur:
                imgs_data_test.append(a)
        datas_for_out = [{'category':category, 'thumbnail':thumb_imgs[idx], 'imgs':cur} for idx, cur in enumerate(imgs_data_test)]

        print(len(datas_for_out))

        if len(datas_for_out) != 0:
            file_name = category.replace("/","").replace("<", "-")
            save_data(f"{file_name}_datas.json", datas_for_out)

        print("----------------------------------------------------------------")


    close_driver(driver)
