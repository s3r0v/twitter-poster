from time import sleep
from seleniumwire import webdriver
from threading import Thread
from random import randint
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def file_to_array(file):
    arr = []
    with open(file) as f:
        while True:
            line = f.readline()
            if not line:
                break
            arr.append(line.strip())
    return arr


def delete_last_line(file):
    with open(file, "r+", encoding="utf-8") as file:

        file.seek(0, os.SEEK_END)

        pos = file.tell() - 1

        while pos > 0 and file.read(1) != "\n":
            pos -= 1
            file.seek(pos, os.SEEK_SET)

        if pos > 0:
            file.seek(pos, os.SEEK_SET)
            file.truncate()


def choose_users():
    global users
    global users_count
    u = ""
    try:
        for i in range(users_count):
            u += f"{users[i]} "
            u.remove(users[i])
        print(u)
        return u
    except Exception():
        u = ""
        for user in users:
            u+=f"{user} "
        print(u)
        return u


def main(messages):
    options = webdriver.FirefoxOptions()

    try:
        proxy = file_to_array("proxies.txt")[randint(0, len(file_to_array("proxies.txt")) - 1)]
        print(proxy)
        proxy_options = {'proxy': {'http': "http://" + proxy,
                                   'https': "https://" + proxy,
                                   'no_proxy': proxy}}
        driver = webdriver.Firefox(seleniumwire_options=proxy_options, options=options)
    except Exception as e:
        print(e)
        driver = webdriver.Firefox(options=options)

    driver.implicitly_wait(15)

    # Login to twitter
    for message in messages:
        while True:
            try:
                acc = file_to_array("accs.txt")[-1]
                delete_last_line("accs.txt")
                break
            except Exception:
                pass


        usr = acc.split(":")[0]
        pwd = acc.split(":")[1]
        media = [f"media/{item}" for item in os.listdir("media")]
        media.remove(media[0])
        try:
            driver.get("https://twitter.com/i/flow/login")
            sleep(2)

            elem = driver.find_element_by_xpath("//input")
            elem.send_keys(usr)

            elem = driver.find_element_by_xpath("//*[text()='Далее']")
            elem.click()

            sleep(.5)

            elem = driver.find_element_by_xpath("//input[@type='password']")
            elem.send_keys(pwd)

            sleep(.5)

            c = driver.find_element_by_xpath("//*[text()='Войти']")
            c.click()

            sleep(2)
            # Enter the text we want to post to twitter and the image
            print(choose_users())
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, '//div[@class="notranslate public-DraftEditor-content"]'))).send_keys(message+choose_users())
            """for m in media:
                element = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, '//input[@type="file"]')))
                driver.execute_script("arguments[0].style.display = 'block';", element)
                element.send_keys(os.getcwd() + m)"""

            driver.find_element_by_xpath("//*[text()='Tweet']").click()
            # Get the 'Post' button and click on it
            sleep(2)
            driver.close()
        except Exception as e:
            print(e)
            continue


def divide_threads(threads, texts):
    thrd = []
    for i in range(threads):
        thrd.append([])
        for j in range(len(texts) // threads):
            thrd[i].append(texts[j])
            texts.remove(texts[j])

    for text in texts:
        thrd[-1].append(text)
    return thrd


if __name__ == '__main__':
    threads = int(input("Сколько потоков?: "))
    timer = int(input("Сколько секунд ждать?: "))
    users_count = int(input("Сколько пользователей должно быть отмечено?: "))

    users = file_to_array("users.txt")
    proxies = file_to_array("proxies.txt")
    accs = file_to_array("accs.txt")
    text_files = [f"texts/{item}" for item in os.listdir("texts")]
    texts = []

    for file in text_files:
        with open(file) as f:
            texts.append(f.read())

    for i in range(threads):
        Thread(target=main, args=(divide_threads(threads, texts)[i]), ).start()
