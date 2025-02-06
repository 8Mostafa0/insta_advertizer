import pyautogui
from moves import drive
from python_imagesearch.imagesearch import *
from time import sleep
from random import randint
from data import settings

insta_url = "https://www.instagram.com/"
USERNAME = "b2rayng"
PASSWORD = "@Mm09020407808"
def main():
    d = drive()
    log = go_to_insta(d)
    if log:
        login(d)
        print("user login")
    else:
        print("user loged in ")
    me()
    go_to_explore(d)
    me()
    find_posts(d)
    while True:
        go_next_post(d)
        me()
        find_comment(d)
        me()
        like_post(d)
        me()
        sleep(6)


def like_post(d:drive):
    l = "imgs/like.png"
    pos_l = imagesearch(l)
    if pos_l[0] > 0:
        d.click(l)

def me():
    i = randint(2,10)
    sleep(i)


def find_comment(d:drive):
    c = "imgs/comment.png"
    p_c = "imgs/post_comment.png"
    pos_c = imagesearch(c)
    if pos_c[0] > 0:
        d.click(c)
        d.type("hello")
        pos_p = imagesearch(p_c)
        if pos_p[0] > 0:
            d.click(p_c)

def go_next_post(d:drive):
    n = "imgs/next.png"
    pos_n = imagesearch(n,0.7)
    if pos_n[0] > 0:
        d.click(n)
        print("load next Post")
        sleep(3)


def find_posts(d:drive):
    posts = "imgs/posts.png"
    pos_p = imagesearch(posts)
    if pos_p[0] > 0:
        d.click(posts)
        print("find post")
        sleep(2)

def go_to_explore(d:drive):
    ex = "imgs/explor.png"
    pos_e = imagesearch(ex)
    if pos_e[0] > 0 :
        d.click(ex)
        print("loading explore")
        sleep(4)

    


def login(d:drive):
    user_img = "imgs/username.png"
    posu = imagesearch(user_img)
    if posu[0]:
        d.click(user_img)
    d.type(USERNAME)
    d.key('tab')
    d.type(PASSWORD)
    d.key('tab')
    d.key('tab')
    d.key('enter')

def go_to_insta(d:drive):
    d.key_d('f6')
    d.key_u('f6')
    d.type(insta_url)
    d.key_d("enter")
    d.key_u("enter")
    sleep(3)
    need_login = False
    load = False
    while load is False:
        pos = imagesearch('imgs/login.png')
        posl = imagesearch('imgs/loged.png',0.7)
        if pos[0] > 0:
            load = True
            need_login = True
        elif posl[0] > 0 or posl[1] > 0:
            load = True
            need_login = False
        else:
            print("sleep for 1 sec")
            sleep(1)
    return need_login
    

if __name__ == "__main__":
    main()