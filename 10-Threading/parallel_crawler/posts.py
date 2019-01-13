import re
from lxml import etree
import requests
from threading import Thread
import time
import html
from mysql_manager import MysqlManager
from crawler import PostsCrawler

max_threads = 10
wait_duration = 20

mysql_mgr = MysqlManager(10)

def post_crawl_task(topic):
        # Get 1st page of this topic
        post_crawler = PostsCrawler()
        post_crawler.get_content(topic['url'], 1)
        posts = post_crawler.get_posts()

        # Get number of pages of this topic
        page_count = post_crawler.get_max_page()

        # Get the rest posts of this topic
        if page_count > 1:
            for i in range(2, page_count + 1):
                post_crawler.get_content(topic['url'], i)
                posts += post_crawler.get_posts()
                break
        
        # Insert post of a topic
        i = 1
        for p in posts:
            # print(p)
            # print("=============================", i, "=============================")
            # print("")

            # Compose the post object
            post = {}
            post['topic_id'] = topic['id']
            post['content'] = p
            post['post_index'] = i
            mysql_mgr.insert_post(post)

            i += 1
        
        # Mark this topic as finished downloading
        mysql_mgr.finish_topic(topic['id'])

def wait_tasks_done(pool):
    for t in pool:
        if not t.is_alive():
            pool.remove(t)
        else:
            t.join()

if __name__ == "__main__":
    
    start_tick = time.time()
    
    while True:
        pool = []
        # Get a topic to grab its content
        topic = mysql_mgr.dequeue_topic()

        if topic is None:
            wait_tasks_done(pool)
            exit(1)
        
        print(topic['title'])
        print(topic['url'])

        task = Thread(target=post_crawl_task, args=(topic,))
        task.start()
        pool.append(task)

        if len(pool) == max_threads:
            wait_tasks_done()
            duration_to_wait = time.time() - start_tick
            if duration_to_wait > 0 and duration_to_wait < wait_duration:
                time.sleep(duration_to_wait)
            start_tick = time.time()