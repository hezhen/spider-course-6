import mysql.connector
from mysql.connector import errorcode
from mysql.connector import pooling
import time 

import re

class MysqlManager:
    
    dbconfig = {
        "database": "weibo",
        "user":     "root",
        "password": "password",
        "host":     "localhost"
    }

    TABLES = {}
    TABLES['post'] = (
        "CREATE TABLE `post` ("
        "  `id` int AUTO_INCREMENT,"
        "  `url` varchar(1024) NOT NULL,"
        "  `title` varchar(128) NOT NULL,"
        "  `author_id` varchar(32) NOT NULL,"
        "  `content1` varchar(200) NOT NULL,"
        "  `content2` varchar(200) NOT NULL DEFAULT 'new',"
        "  `comment_cnt` int NOT NULL DEFAULT 0,"
        "  `like_cnt` int NOT NULL DEFAULT 0,"
        "  `repost_cnt` int NOT NULL DEFAULT 0,"
        "  `publish_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,"
        "  `queue_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,"
        "  PRIMARY KEY (`id`),"
        "  UNIQUE (`url`)"
        ") ENGINE=InnoDB")

    TABLES['picture'] = (
        "CREATE TABLE `picture` ("
        "  `id` int NOT NULL,"
        "  `post_id` int NOT NULL default 0,"
        "  `url` varchar(1024) NOT NULL,"
        "  UNIQUE (`url`), "
        "  UNIQUE (`post_id`, `id`) "
        ") ENGINE=InnoDB")

    TABLES['comment'] = (
        "CREATE TABLE `comment` ("
        "  `author_id` varchar(64) NOT NULL,"
        "  `text` varchar(32) NOT NULL,"
        "  `post_id` int NOT NULL, "
        "  `publish_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP"
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

    def get_table_column_keys(create_table_sql):
        s = re.findall(r'\((.*)\)', create_table_sql)[0]
        keys = re.findall(r'\s\`(.*?)\`\s', s)
        return keys

    def combine_insert_sql( table_name, data):
        # auto extract columns
        columns = self.get_table_column_keys(self.TABLES[table_name])

        sql0 = 'INSERT INTO ' + table_name + '('
        sql1 = 'VALUES ('

        for col in columns:
            if col in data:
                sql0 += col + ', '
                sql1 += "'" + data[col] + "', "

        sql0 = sql0[:-2]
        sql1 += ')'
        sql1 = sql1[:-2]
        return sql0 + ') ' + sql1

    # return False if topic already exist, True otherwise        
    def insert_data(self, data, table_name):
        con = self.cnxpool.get_connection()
        cursor = con.cursor()
        try:
            self.combine_insert_sql(table_name, data)
            print(sql)
            cursor.execute((sql))
            con.commit()
            return True
        except mysql.connector.Error as err:
            # print('insert_topic() ' + err.msg)
            # print("Aready exist!")
            return False
        finally:
            cursor.close()
            con.close()

if __name__ == "__main__":
    mysql_mgr = MysqlManager(8)