import time
import json
import concurrent.futures
from selenium import webdriver as wb
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


# with open("./스콥_target_tags.json", encoding="utf-8", mode="r") as f:
#     search_words = list(json.load(f))

search_words = ['#portrait',
 'air conditioning',
 'alcohol',
 'apprentice',
 'apprenticeship',
 'architecture black and white',
 'aubergine',
 'banana',
 'base makeup',
 'bean',
 'beauty',
 'beauty product',
 'beauty salon',
 'beer',
 'beer glass',
 'billboards',
 'birthday party',
 'blogging',
 'blood pressure',
 'bottle',
 'business center',
 'cafe',
 'capsule',
 'ceramic',
 'civil engineering',
 'clean',
 'cocktail',
 'coffee cup',
 'computer',
 'computer hardware',
 'computer keyboard',
 'confectionery',
 'contraception',
 'contraceptive',
 'corner',
 'cosmetic',
 'cosmetic cream',
 'cosmetics bottle',
 'crisp',
 'css',
 'cup',
 'customer care',
 'dark mode wallpaper',
 'data',
 'datum',
 'desktop background',
 'desktop computer',
 'desktop wallpaper',
 'desktop wallpapers',
 'dessert',
 'digital marketing',
 'drink',
 'egg',
 'eggplant',
 'electronic chip',
 'face cream',
 'face makeup',
 'feminine product',
 'fingering',
 'food market',
 'food_photography',
 'foundation bottle',
 'fruit',
 'gaming',
 'gelato',
 'glass',
 'glass bottle',
 'glasses frame',
 'google',
 'google chromebook',
 'grain',
 'hand model',
 'headset',
 'hiv',
 'hydration',
 'iud',
 'jar',
 'juicy',
 'kaffee',
 'keyboard',
 'kiwi',
 'lamp post',
 'laptop wallpaper',
 'laranja',
 'latte',
 'light fixture',
 'linkedin banner',
 'lipstick',
 'liquid foundation',
 'lotion',
 'macbook',
 'make',
 'make up artist',
 'make up face',
 'make-up',
 'makeup brush',
 'makeup foundation',
 'makeup product',
 'makeup products',
 'manicure',
 'mascara',
 'masturbation',
 'mechanical keyboard',
 'medication',
 'medicine',
 'melon',
 'method',
 'microsoft',
 'microsoft logo',
 'minimal wallpaper',
 'miss swiss',
 'mock up',
 'mock-up',
 'moisturiser',
 'moisturizer',
 'mug',
 'mug mockup',
 'nail polish',
 'nails',
 'nature flower',
 'nature zen',
 'newsletters',
 'night cream',
 'onion ring',
 'online',
 'organic',
 'pc',
 'pepper',
 'pepsi',
 'pharma',
 'pharmaceutical',
 'pharmacist',
 'pharmacy',
 'pill',
 'planet',
 'polish',
 'product',
 'product photo',
 'protein',
 'pub',
 'radiologist',
 'remedy',
 'reproductive',
 'retro gaming',
 'ripe',
 'rooftop bar',
 'saucer',
 'seo',
 'serum',
 'sex ed',
 'sex education',
 'shampoo',
 'shampoo bottle',
 'shelf',
 'skin',
 'skin care',
 'skin care products',
 'skincare',
 'slice',
 'social media',
 'soda',
 'spice',
 'spicy',
 'spray',
 'stainless steel',
 'storage',
 'strawberry',
 'sunglasses',
 'sweet',
 'switch',
 'table lamp',
 'tap',
 'tea',
 'the home depot',
 'tile roof',
 'tissue',
 'travel makeup',
 'treatment',
 'tumblr background',
 'unporn',
 'upward',
 'vagina',
 'vegan',
 'video gaming',
 'warehouse',
 'watermelon',
 'website background',
 'weight loss',
 'working',
 'zero waste']
search_words = [(cur, 8000)for cur in search_words]

base_url = "https://unsplash.com/s/photos/"
Null_url = "https://unsplash.com/plus?referrer=%2Fphotos%2Ffr7sfo99PB8"

class get_sel_img():
    
    driver = None
    wait = None
    action = None
    search_word = "Temp Name"

    def __init__(self, search_word):
        option = Options()
        option.add_experimental_option('excludeSwitches', ['enable-logging'])
        option.add_argument('--headless')
        
        self.driver = wb.Chrome(options=option)
        self.wait = WebDriverWait(self.driver, 10)
        self.action = ActionChains(self.driver)
        self.driver.implicitly_wait(10)
        self.search_word = search_word

    def get_imgs(self, max_imgs):
        
        self.driver.get(base_url + self.search_word)
        more_button = self.driver.find_element(By.CSS_SELECTOR,"#app > div > div:nth-child(3) > div:nth-child(4) > div > div > button")
        more_button.click()
        
        self.scrolling(max_imgs)
        eles = self.driver.find_elements(By.XPATH, "//figure[@itemprop='image']")
        
        with open(f"./outputs/unsplash_tag_url_8000/{self.search_word}.json", mode="w", encoding="utf-8") as w:
            w.write("[")
            eles_length = len(eles) -1
            for idx, cur in enumerate(eles):
                temp_dict = {
                            "index": idx,
                            "search_word": self.search_word,
                            "describe": cur.find_element(By.CSS_SELECTOR, "div > div > a img").get_attribute("alt"),
                            "thum": cur.find_element(By.CSS_SELECTOR, "div > div > a img").get_attribute("src"),
                            "real": cur.find_element(By.CSS_SELECTOR, "div > div > div > div:nth-child(2) > div > a").get_attribute("href")
                            } 
                json.dump(temp_dict, w, ensure_ascii=False, indent=4)
                if idx != eles_length:
                    w.write(",\n")
            w.write("]")

    
    def write_json(self, dict_list):
        with open(f"./outputs/unsplash_detect_product_url/{self.search_word}.json", mode="w", encoding="utf-8") as w:
            json.dump(dict_list, w, ensure_ascii=False, indent=4)
        print(f"{self.search_word} is done!")
        return True

    # 마우스 스크롤 관련 함수
    def scrolling(self, max):
        aft_ele = len(self.driver.find_elements(By.XPATH, "//a[@rel='nofollow']"))
        while True:

            if aft_ele > max: break
            
            bef_ele = aft_ele
            #현재 위치 + 500으로 스크롤 이동
            self.driver.execute_script(f"window.scrollTo(0,document.body.scrollHeight - 1500)")

            print(f"{self.search_word} over {bef_ele}" )
            for _ in range(60):
                aft_ele = len(self.driver.find_elements(By.XPATH, "//a[@rel='nofollow']"))
                # print(bef_ele, aft_ele)
                if bef_ele == aft_ele:
                    before_location = self.driver.execute_script("return window.pageYOffset")
                    self.driver.execute_script(f"window.scrollTo(0,{before_location + 100})")
                    time.sleep(0.5)
                else:
                    break
            
            if bef_ele == aft_ele : 
                break

    def close_driver(self):
        self.driver.close()
        print(self.search_word, "closed!")
        return True
    
def crawl_process(search_word):
    search_word, max_imgs = search_word
    print(f"start {search_word}!")
    img_geter = get_sel_img(search_word)
    imgs_url = img_geter.get_imgs(max_imgs = max_imgs)
    # img_geter.write_json(imgs_url)
    img_geter.close_driver()

if __name__ == "__main__":
    
    num_processes = 6
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
        executor.map(crawl_process, search_words)


    
