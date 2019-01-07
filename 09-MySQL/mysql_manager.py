import mysql.connector
from mysql.connector import errorcode
from mysql.connector import pooling
import time 

class MysqlManager:
    
    dbconfig = {
        "database": "smth",
        "user":     "root",
        "password": "password",
        "host":     "localhost"
    }

    TABLES = {}
    TABLES['topic'] = (
        "CREATE TABLE `topic` ("
        "  `id` varchar(16) NOT NULL,"
        "  `title` varchar(128) NOT NULL,"
        "  `url` varchar(1024) NOT NULL,"
        "  `author_id` varchar(32) NOT NULL,"
        "  `author_name` varchar(32) NOT NULL,"
        "  `status` char(20) NOT NULL DEFAULT 'new',"
        "  `publish_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, "
        "  `queue_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, "
        "  `done_time` timestamp NOT NULL DEFAULT '1970-01-02 00:00:00' ON UPDATE CURRENT_TIMESTAMP, "
        "  PRIMARY KEY (`id`),"
        "  UNIQUE (`url`)"
        ") ENGINE=InnoDB")

    TABLES['board'] = (
        "CREATE TABLE `board` ("
        "  `name` varchar(64) NOT NULL,"
        "  `url` varchar(1024) NOT NULL,"
        "  `status` char(20) NOT NULL DEFAULT 'new',"
        "  `num_artciles` int(11) NOT NULL,"
        "  `num_posts` int(11) NOT NULL,"
        "  PRIMARY KEY (`name`),"
        "  UNIQUE (`url`)"
        ") ENGINE=InnoDB")

     TABLES['post'] = (
        "CREATE TABLE `post` ("
        "  `topic_id` varchar(16) NOT NULL,"
        "  `content` varchar(10240) NOT NULL,"
        "  `post_index` int(11) NOT NULL,"
        "  `page_index` int(11) NOT NULL,"
        "  `author_id` varchar(32) NOT NULL,"
        "  `author_name` varchar(32) NOT NULL,"
        "  `status` char(20) NOT NULL DEFAULT 'new',"
        "  `publish_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, "
        "  PRIMARY KEY (`topic_id`), "
        "  UNIQUE(`topic_id`, `post_index`) "
        ") ENGINE=InnoDB")

    def __init__(self, max_num_thread):
        try:
            cnx = mysql.connector.connect(host=self.dbconfig['host'], user=self.dbconfig['user'], password=self.dbconfig['password'])
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print('Create Error ' + err.msg)
            exit(1)

        cursor = cnx.cursor()

        try:
            cnx.database = self.dbconfig['database']
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                self.create_database(cursor)
                cnx.database = self.dbconfig['database']
                self.create_tables(cursor)
            else:
                print(err)
                exit(1)
        finally:
            cursor.close()
            cnx.close()

        self.cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_name = "mypool",
                                                          pool_size = max_num_thread,
                                                          **self.dbconfig)


    def create_database(self, cursor):
        try:
            cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(self.dbconfig['database']))
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))
            exit(1)

    def create_tables(self, cursor):
        for name, ddl in self.TABLES.items():
            try:
                cursor.execute(ddl)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print('create tables error ALREADY EXISTS')
                else:
                    print('create tables error ' + err.msg)
            else:
                print('Tables created')


    def insert_board(self, url, name, num_artciles, num_posts):
        con = self.cnxpool.get_connection()
        cursor = con.cursor()
        try:
            sql = "INSERT INTO board(url, name, num_artciles, num_posts) VALUES ('{}', '{}', '{}', '{}' )".format(url, name, num_artciles, num_posts)
            # print(sql)
            cursor.execute((sql))
        except mysql.connector.Error as err:
            print('enqueue_url() ' + err.msg)
            # print("Aready exist!")
            return
        finally:
            cursor.close()
            con.close()

    # return False if topic already exist, True otherwise        
    def insert_topic(self, id, title, url, author_id, author_name, publish_time):
        con = self.cnxpool.get_connection()
        cursor = con.cursor()
        try:
            sql = "INSERT INTO board(id, title, url, author_id, author_name, publish_time) " 
                "VALUES ('{}', '{}', '{}', '{}', '{}', '{}' )".format(id, title, url, author_id, author_name, publish_time)
            # print(sql)
            cursor.execute((sql))
            return True
        except mysql.connector.Error as err:
            # print('enqueue_url() ' + err.msg)
            # print("Aready exist!")
            return False
        finally:
            cursor.close()
            con.close()

    # return False if topic already exist, True otherwise        
    def insert_post(self, topic_id, content, post_index, page_index, author_id, author_name, publish_time):
        con = self.cnxpool.get_connection()
        cursor = con.cursor()
        try:
            sql = "INSERT INTO board(topic_id, content, post_index, page_index, author_id, author_name, publish_time) " 
                "VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}' )".format(topic_id, content, post_index, page_index, author_id, author_name, publish_time)
            # print(sql)
            cursor.execute((sql))
            return True
        except mysql.connector.Error as err:
            # print('enqueue_url() ' + err.msg)
            # print("Aready exist!")
            return False
        finally:
            cursor.close()
            con.close()

    def dequeue_topic(self):
        con = self.cnxpool.get_connection()
        cursor = con.cursor(dictionary=True)
        try:
            con.start_transaction()
            const_id = "%.9f" % time.time()
            update_query = ("UPDATE topic SET status='{}' WHERE status='new' LIMIT 1".format(const_id))
            cursor.execute(update_query)

            query = ("SELECT `url` FROM topic WHERE status='{}'".format(const_id))
            cursor.execute(query)
            con.commit()

            row = cursor.fetchone()
            if row is None:
                return None
            return row['url']
        except mysql.connector.Error as err:
            print('dequeueUrl() ' + err.msg)
            return None
        finally:
            cursor.close()
            con.close()
    
    def dequeue_batch_topics(self, size):
        con = self.cnxpool.get_connection()
        cursor = con.cursor(dictionary=True)
        try:
            con.start_transaction()
            const_id = "%.9f" % time.time()
            update_query = ("UPDATE topic SET status='{}' WHERE status='new' LIMIT {}".format(const_id, size))
            cursor.execute(update_query)

            query = ("SELECT `url` FROM topic WHERE status='{}'".format(const_id))
            cursor.execute(query)
            con.commit()

            rows = cursor.fetchall()
            if rows is None:
                return None
            return rows
        except mysql.connector.Error as err:
            print('dequeueUrl() ' + err.msg)
            return None
        finally:
            cursor.close()
            con.close()

    def finish_topic(self, index):
        con = self.cnxpool.get_connection()
        cursor = con.cursor()
        try:
            # we don't need to update done_time using time.strftime('%Y-%m-%d %H:%M:%S') as it's auto updated
            update_query = ("UPDATE topic SET `status`='done' WHERE `id`=%d") % (index)
            cursor.execute(update_query)
        except mysql.connector.Error as err:
            # print('finishUrl() ' + err.msg)
            return
        finally:
            cursor.close()
            con.close()

if __name__ == "__main__":
    mysql_mgr = MysqlManager(8)
    print(mysql_mgr.dequeue_batch_urls(10))