import pandas as pd
from sqlalchemy import create_engine, text
import lxml.objectify as lxml_objectify
import os

database_url = os.environ(['DATABASE_URL'])



def read_db(query):
    """
    function to execute query to database and return a pandas dataframe
    :param query: query to be execute
    :return: data frame
    """
    engine = create_engine(database_url, echo=True)
    df = pd.read_sql_query(query, engine)
    return df


def write_db(tbl_name, df):
    """
    function to write a dataframe to a database
    :param tbl_name: Table name of the database
    :param df: data frame to be insert
    :return:
    """
    engine = create_engine(database_url, echo=True)
    print("Writing database")
    print(df)
    df.to_sql(tbl_name, con=engine, if_exists='replace', index=False)
    return


def write_db_uniq(db_tbl_name, df):
    """
    function to update database
    :param db_tbl_name:
    :param df:
    :return:
    """

    query = "SELECT * from " + db_tbl_name + ";"
    engine = create_engine(database_url, echo=True)
    db_df = pd.read_sql_query(query, engine)
    print("Database dataframe")
    print(db_df.columns)
    print(df.columns)
    print(db_df.columns.intersection(df.columns).all())

    if db_df.columns.intersection(df.columns).all():
        print("Merging table")
        db_to_write = pd.concat([db_df, df], ignore_index=True)
        print(db_to_write)
    else:
        print("Column name not matched")
    # deduplicate
    db_to_write = db_to_write.drop_duplicates()
    print("Writing table")
    db_to_write.to_sql(db_tbl_name, con=engine, if_exists='replace', index=False)
    return


def write_db_from_csv(tbl_name, path):
    """
    function to overwrite database with data from csv
    """
    df = pd.read_csv(path)
    write_db(tbl_name, df)
    return


def write_db_from_csv_uniq(tbl_name, path):
    """
    function to merge database with data from csv
    """
    df = pd.read_csv(path)
    write_db_uniq(tbl_name, df)
    return


def get_lxml_root(str):
    root = lxml_objectify.fromstring(str)
    return root.FlexStatements.FlexStatement


if __name__ == '__main__':
    my_query = '''
    SELECT * from xx;
    '''
    df = read_db(my_query)
    print(df)

    write_db_uniq('xx', df)


