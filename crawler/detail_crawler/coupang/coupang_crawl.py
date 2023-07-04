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


# 크롤링 관리 클래스
class crawl_master():
    init_url = ""
    action = None
    wait = None
    driver = None
    option = None
    chrome_ver = None
    skip_category = ""

    # 디버그 크롬 드라이버 생성 및 열기
    def __init__(self, url = "https://www.coupang.com/", skip_category = ""):
        try:
            shutil.rmtree(r"c:\chrometemp")  #쿠키 / 캐쉬파일 삭제
        except FileNotFoundError:
            pass
        subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"') # 디버거 크롬 구동
        self.option = Options()
        self.option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
        try:
            self.driver = wb.Chrome(f'./{self.chrome_ver}/chromedriver.exe', options=self.option)
        except:
            chromedriver_autoinstaller.install(True)
            self.driver = wb.Chrome(f'./{self.chrome_ver}/chromedriver.exe', options=self.option)
        
        self.init_url = url
        
        self.wait = WebDriverWait(self.driver, 7)
        self.action = ActionChains(self.driver)
        self.skip_category = skip_category
        self.driver.implicitly_wait(10)
        self.driver.get(self.init_url)


    # 현재 윈도우 핸들이 정상적인지 확인
    def check_window_handel(self, handle_index):
        counter = 0
        result_bool = True

        while(len(self.driver.window_handles) != handle_index + 1): 
            time.sleep(0.3)

            if counter > 30:
                result_bool = False
                print(f"{handle_index}번 window handle이 없습니다.")
                break
            else:
                counter += 1
                continue
            
        return result_bool
    

    # 데이터 저장
    def save_data(self, datas):
        file_name = f"{datas[0]['category']}_datas.json"

        with open(f"./output/{file_name}",'w') as f:
            json.dump(datas, f, ensure_ascii=False, indent=4)


    # 데이터 파일 이름 수정 정규표현식
    def regex_apply(self, string):
        pattern = re.compile(r'^([^<]+)')  # 첫 번째 '<' 이전까지 문자열 추출
        match = pattern.search(string.strip())
        return match.group(1)
    

    # 썸네일 element를 탐색하고, 썸네일과 연결된 url을 순환하면서 이미지 src 추출
    def search_img(self, category_str):
        
        img_datas = []
        thums_ele = []
        time.sleep(2)

        # 썸네일 element를 일정 개수 이상 가져올 때까지 재시도
        while(len(thums_ele) <= 35):
            self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            thums_ele = self.driver.find_elements(By.CSS_SELECTOR, "a.baby-product-link")

        # 썸네일 elements 순환
        for idx, thum_ele in enumerate(thums_ele):


            # 썸네일 이미지 get
            thum_img = thum_ele.find_element(By.CSS_SELECTOR,"img").get_attribute("src")
            # 썸네일 링크 get
            thum_link = thum_ele.get_attribute("href")
            

            # 썸네일 링크 open, 제대로 open될 때까지 윈도우 핸들 기반 wait
            window_handle_bool = False
            while(not window_handle_bool):
                self.driver.execute_script("window.open(arguments[0],'_blank');", thum_link)
                window_handle_bool = self.check_window_handel(2)
            self.driver.switch_to.window(self.driver.window_handles[2])


            # 상품 상세 이미지 탐색, 없을 경우 에러 발생
            try:
                self.driver.execute_script("window.scrollTo(0, 2000);")
                vendor_page = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.vendor-item")))
            except:
                print('\nCss selector 이미지 결과값이 없습니다.')
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[1])
                continue
            imgs_ele = vendor_page.find_elements(By.CSS_SELECTOR, "img")


            # 카테고리, 썸네일, 상품 상세 이미지 딕셔너리의 리스트로 반환
            imgs = []
            for img in imgs_ele:
                imgs.append(img.get_attribute('src'))

            if len(imgs) != 0 : 
                img_datas.append({"category":category_str,"thumbnail":thum_img,"imgs":imgs})


            # 상품 윈도우 핸들 닫기
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[1])

        return img_datas


    # 크롤링 실행
    def run_crawl(self, category_list):


        # skip_category 불러오기
        skip_bool = False
        skip_category = self.skip_category


         # skip_category부터 크롤링 시작
        for category, c_url in category_list:

            datas_for_json = []
            if skip_bool == False:
                if skip_bool == False and category != skip_category:
                    continue
                else:
                    skip_bool = True

            print(category)


            # 윈도우 핸들 기반 창이 제대로 열릴 때까지 대기
            window_handle_bool = False
            while(not window_handle_bool):
                self.action.key_down(Keys.CONTROL).click(self.driver.find_element(By.CSS_SELECTOR, "div")).key_up(Keys.CONTROL).perform()
                window_handle_bool = self.check_window_handel(1)
            self.driver.switch_to.window(self.driver.window_handles[1])


            # 상품 1000개의 데이터가 모일 때까지 search_img실행, Next Page로 URL 이동
            cur_page = 1
            self.driver.get(f"{c_url}?page={cur_page}")

            img_datas_total = []
            while(len(img_datas_total) < 1000):

                # 에러 발생 시 
                img_datas_page = []
                try:
                    img_datas_page = self.search_img(category)
                except:
                    print(f"{category}의 {cur_page}페이지에서 오류가 발생했습니다.")
                    pass

                img_datas_total.extend(img_datas_page)

                cur_page += 1
                self.driver.get(f"{c_url}?page={cur_page}")
                while(len(self.driver.window_handles) != 2): continue
                
                print(len(img_datas_total))
            
            # 데이터 json으로 저장
            datas_for_json.extend(img_datas_total)

            if len(datas_for_json) != 0:
                file_name = category.replace("/","").replace(">", "-")
                self.save_data(f"{file_name}", datas_for_json)

            # 썸네일 페이지 윈도우 핸들 종료
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

            print("\n---------------------------------")




# 메인함수
if __name__ == '__main__':

    # 쿠팡 카테고리 url 파일 오픈 및 list화   ex: {"패션의류/잡화>여성패션>의류": "https://www.coupang.com/np/categories/498704"}
    with open('Coupang_Categoty_url.json', encoding="utf-8") as json_file:
        category_dict = json.load(json_file)
    category_list = list(category_dict.items())


    # skip_category 설정, 해당 카테고리부터 크롤링을 실행합니다.
    skip_category = "패션의류/잡화>남성패션>속옷/잠옷"


    # crawl_master 클래스 생성
    # init url과 skip_category를 넣어줘야 합니다.
    crawl_master = crawl_master("https://www.coupang.com/", skip_category)


    # 실행
    # category_list를 넣어줘야 합니다.
    crawl_master.run_crawl(category_list)

