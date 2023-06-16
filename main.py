import os
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
import time
from math import floor
import pickle
import io
import requests
from PIL import Image

def create_a_cookie(driver: webdriver.Chrome | webdriver.Firefox | webdriver.Edge | webdriver.Safari):
    pickle.dump(driver.get_cookies(), open('session', 'wb'))
    

def get_image_urls(url: str) -> None:
    try:
        driver = webdriver.Chrome()
        driver.get(url=url)
        
        # create_a_cookie(driver=driver)
        for cookie in pickle.load(open('session', 'rb')):
            driver.add_cookie(cookie_dict=cookie)
        driver.refresh()
        time.sleep(5)
        
        pages_count = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/span[4]').get_attribute('innerHTML')
        clicks_count = floor(int(pages_count) / 2)-1
        for i in range(clicks_count):
            driver.find_element(By.XPATH, '/html/body/section[3]/div/div/div[2]/a[2]').click()
            time.sleep(.5)
        time.sleep(5)
        
        image_urls = []
        for request in driver.requests:
            if request.response:
                if (request.response.headers['Content-Type'] == 'image/jpeg') and (request.url.startswith('https://cdn-img.pocket.shonenmagazine.com/public/page/')):
                    image_urls.append(request.url)
        image_urls.sort()
        return image_urls
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()

def download_images(image_urls: list):
    for (index, image_url) in enumerate(image_urls, start=1):
        r = requests.get(image_url, stream=True)
        with Image.open(io.BytesIO(r.content)) as im:
            width = 240
            height = 344
            columns = 4
            rows = 5
            x = 0
            y = 0
            final_image = Image.new('RGB',im.size)
            blocks = []
            for i in range(rows):
                tmp = []
                for j in range(columns):
                    tmp.append(im.crop((x, y, x + width, y + height)))
                    x += width
                if rows == 3:
                    height = 2
                x = 0
                y += height
                blocks.append(tmp)
            width = 240
            height = 344

            
            for j in range(0, 4):
                for i in range(len(blocks)):
                    final_image.paste(blocks[i][j], (width*i, height*j, width*(i+1), height*(j+1)))
            if not os.path.exists('images'):
                os.makedirs('images')
            final_image.save(f'images/{index}.jpg')

def main() -> None:
    url = input("URL to manga webpage: ")
    if url.startswith("https://pocket.shonenmagazine.com"):
        urls = get_image_urls(url=url)
        download_images(urls)
    else:
        print("Only for https://pocket.shonenmagazine.com")

if __name__ == "__main__":
    main()
