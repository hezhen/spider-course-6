from board_list import BoardListCrawler
from board_articles import BoardArticleListCrawler
from article import ArticleCrawler

board_list_crawler = BoardListCrawler()
board_article_crawler = BoardArticleListCrawler()
article_crawler = ArticleCrawler()

boards = []

def get_article_posts(url):
    c = articleCrawler.get_pagination_content(url, 1)
    total_pages = articleCrawler.get_total_pages(c)
    posts = articleCrawler.get_posts(c)
    print(total_pages)
    if total_pages > 1:
        for i in range(2, total_pages + 1):
            c = articleCrawler.get_pagination_content(i)
            posts.append(articleCrawler.get_posts(c))

# Get all boards
for i in range(0,10):
    c = boardListCrawler.get_pagination_content(i)
    boards.append(boardListCrawler.get_board_list(c))

    # Get article list of board
    for board in boards:
        url = boards['board_url']
        content = boardArticleListCrawler.get_pagination_content(url, 1)
        articles = boardArticleListCrawler.get_article_list(content)
        total_pages_of_board = boardArticleListCrawler.get_total_pages(content)
        for article in articles:
            get_article_posts(article['article_url'])
        for i in range(2, total_pages_of_board+1):
            articles = boardArticleListCrawler.get_article_list(content)
            for article in articles:
                get_article_posts(article['article_url'])