from sqlalchemy import create_engine, Table, Column, Integer, String
from sqlalchemy import MetaData, DateTime
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
import datetime
from config import DB_ADDRESS


class Base(DeclarativeBase):
    pass


class Items(Base):
    __tablename__ = 'items'
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int]
    location_id: Mapped[int]
    title: Mapped[str]
    description: Mapped[str]
    item_location: Mapped[str]
    starttime: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now)


def get_engine():
    engine = create_engine(DB_ADDRESS, echo=True)
    if not database_exists(engine.url):
        create_database(engine.url)
    return engine


def create_items_table(engine):
    metadata_obj = MetaData()
    _ = Table(
        'items',
        metadata_obj,
        Column('id', Integer, primary_key=True),
        Column('category_id', Integer),
        Column('location_id', Integer),
        Column('title', String),
        Column('description', String),
        Column('item_location', String),
        Column('starttime', DateTime, default=datetime.datetime.now)
    )

    metadata_obj.create_all(engine)


def insert_to_items(session_factory):
    # TODO: Read real Data?
    with session_factory() as session:
        for i in range(30):
            item = Items(
                category_id=42,
                location_id=7001,
                title=f'Title_{i}',
                description=f'Description for {i}',
                item_location=f'Address for {i}',
            )
            session.add(item)
        session.commit()


if __name__ == '__main__':
    engine = get_engine()
    create_items_table(engine)
    session_factory = sessionmaker(engine)
    insert_to_items(session_factory)
