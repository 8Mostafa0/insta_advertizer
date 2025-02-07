from moves import drive
from python_imagesearch.imagesearch import *
from time import sleep
from random import randint
from data import settings,reset_sets
from imgs import *
import comments

global log_func

sets = settings()

insta_url = "https://www.instagram.com/"
USERNAME = "b2rayng"
PASSWORD = "@Mm09020407808"
d = drive()

def start_adding(running,log):
    global log_func
    log_func = log
    sleep(1)
    log = go_to_insta(running)
    if log:
        login(running)
        log_func("user login")
    else:
        log_func("user loged in ")
    me()
    need_break = False
    while need_break is False and running.is_set():
        me()
        if sets['comments'] < sets['max_comments']:
            if sets['state'] != "like":
                state = find_state()
                log_func("state: ",state)
                if state == "error":
                    need_break = True
                    break
                elif state != "like":
                    change_state("like")
            me()
            comment_text = get_comment()
            post_comment(comment_text) 
            me()
            go_next_post()
        elif sets['likes'] < sets['max_likes']:
            if sets['state'] != "like":
                state = find_state()
                log_func("state: ",state)
                if state == "error":
                    need_break = True
                    break
                elif state != "like":
                    change_state("like")
            me()
            like_post()
            me()
            go_next_post()
        elif sets['follows'] < sets['max_follows']:
            if sets['state'] != "like":
                state = find_state()
                log_func("state: ",state)
                if state == "error":
                    need_break = True
                    break
                elif state != "follow":
                    change_state("follow")
            me()
            follow()
            me()
        

        if need_break:
            sleep(4000)
            reset_sets()
            start_adding(running)
    
    log_func("program stoped")

def find_state():
    log_func("find state")
    if imagesearch(error_image)[0] > 0:
        return "error"
    elif imagesearch(follow_button_image,0.99)[0] > 0:
        return "follow"
    elif imagesearch(like_image,0.99)[0] > 0 or imagesearch(post_comment_image)[0] > 0:
        return "like"
    elif imagesearch(posts_image,0.99)[0] > 0:
        return "explor"
    elif imagesearch(home_image,0.99)[0] > 0:
        return "home"

def change_state(expected_path:str):
    log_func("change state to ",expected_path)
    res = False
    if sets['state'] == "home":
        res = go_to(explor_image)
        if expected_path == "follow":
            x,y = d.center(follow_images)
            me()
            d.click(x-100,y)
            me()
            x1,y1 = d.center(followers_images)
            d.click(x1-100,y1)
        elif expected_path == "like" or expected_path == "comment":
            res = go_to(posts_image)
            if res is False:
                state = find_state()
                sets['state'] = state
                change_state(expected_path) 
    if sets['state'] == "like" or sets['state'] == "comment":
        res = go_to(home_image)
        me()
        if expected_path == "follow":
            res = go_to(explor_image)  if res else False
            if res is False:
                state = find_state()
                sets['state'] = state
                change_state(expected_path)
    elif sets['state'] == "follow":
        res = go_to(home_image)
        me()
        if expected_path == "like" or  expected_path == "comment":
            res = go_to(explor_image)  if res else False
            res = go_to(posts_image)  if res else False
            if res is False:
                state = find_state()
                sets['state'] = state
                change_state(expected_path)
    return res

def go_to(path:str,confidens:int=0.9):
    res = False
    p_path = imagesearch(path,confidens)
    if p_path[0] > 0 or p_path[1] > 0:
        d.click(path)
        res = True
    return res
        


def follow():
    follow_exist = True
    while follow_exist:
        follow_exist = go_to(follow_button_image)
        sets['follows'] +=1
    requested = True
    while requested:
        sets['follows'] -=1
        requested = go_to(requested_image)
        go_to(unfollow_button_immage)
    me()
    go_to(scroll_down_image)
    go_to(scroll_down_image)
    go_to(scroll_down_image)
    go_to(scroll_down_image)

def get_comment():
    global log_func
    comments_count = comments.count_comments()
    if comments_count > 0:
        i = randint(1,comments_count-1)
        log_func("comments_count : ",comments_count)
        text = comments.get_comment(i)
        if text is not None:
            return text
        else:
            log_func(i ," this id is none")
            return get_comment()
    else:
        return "سلام سلام"


def like_post():
    if sets['likes'] < sets['max_likes']:
        res = go_to(like_image)
        if res:
            sets['likes'] +=1

def me(start:int=1,end:int=3):
    i = randint(start,end)
    sleep(i)


def post_comment(comment:str):
    go_to(comment_image)
    me()
    d.type(comment)
    me()
    res = go_to(post_comment_image,0.8)
    print(res ," res of post comment ")

def go_next_post():
    go_to(next_post_image)
    sleep(3)


def find_posts():
    go_to(posts_image)
    sleep(2)

def go_to_explore():
    go_to(explor_image)
    sleep(4)

    


def login(running):
    global log_func
    res = go_to(username_image)
    if res:
        d.type(USERNAME)
        d.key('tab')
        d.type(PASSWORD)
        d.key('tab')
        d.key('tab')
        d.key('enter')
    elif res is False and running.is_set():
        me()
        login()
    

def go_to_insta(running):
    global log_func
    d.key_d('f6')
    d.key_u('f6')
    d.type(insta_url)
    d.key_d("enter")
    d.key_u("enter")
    sleep(3)
    need_login = False
    load = False
    while load is False:
        pos = imagesearch(is_need_login_image)
        posl = imagesearch(is_loged_image,0.7)
        if pos[0] > 0:
            load = True
            need_login = True
        elif posl[0] > 0 or posl[1] > 0:
            load = True
            need_login = False
        elif running.is_set():
            log_func("sleep for 1 sec")
            sleep(1)
        else:
            load = True
            need_login = True
            break
    return need_login
    
