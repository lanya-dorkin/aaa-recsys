import datetime
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, BIGINT, String, MetaData, DateTime
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
import pandas as pd
from tqdm import tqdm
from config import DB_ADDRESS


class Base(DeclarativeBase):
    pass


class Items(Base):
    __tablename__ = 'items'
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int]
    title: Mapped[str]
    item_location: Mapped[str]
    starttime: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now)


def get_engine() -> sqlalchemy.engine.Engine:
    engine = create_engine(DB_ADDRESS)
    if not database_exists(engine.url):
        create_database(engine.url)
    return engine


def create_items_table(engine):
    metadata_obj = MetaData()
    _ = Table(
        'items',
        metadata_obj,
        Column('id', BIGINT, primary_key=True),
        Column('category_id', Integer),
        Column('title', String),
        Column('item_location', String),
        Column('starttime', DateTime, default=datetime.datetime.now)
    )
    metadata_obj.create_all(engine)


def insert_to_items(session_factory: sessionmaker):
    items = pd.read_parquet('data/to_postgres.parquet')
    session = session_factory()
    for idx, item in tqdm(items.iterrows(), mininterval=5, total=len(items)):
        item = Items(
            id=item['item_id'],
            category_id=item['category_id'],
            title=item['title'],
            item_location=str(item['location_id']),
        )
        try:
            session.add(item)
            if idx % 1000 == 0:
                session = session_factory()
                session.commit()
        except Exception as e:
            session.rollback()
            print(e)


if __name__ == '__main__':
    engine = get_engine()
    create_items_table(engine)
    session_factory = sessionmaker(engine)
    print('start process of inserting items')
    insert_to_items(session_factory)
