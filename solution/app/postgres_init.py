import sqlalchemy
from sqlalchemy import create_engine, MetaData
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
    title: Mapped[str]
    item_location: Mapped[str]
    starttime: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now)


def get_engine() -> sqlalchemy.engine.Engine:
    engine = create_engine(DB_ADDRESS, echo=False)
    if not database_exists(engine.url):
        create_database(engine.url)
    return engine


def create_items_table(engine: sqlalchemy.engine.Engine):
    metadata_obj = MetaData()
    metadata_obj.create_all(engine)


def insert_to_items(session_factory: sessionmaker):
    # TODO: Read real Data
    with session_factory() as session:
        for i in range(30):
            item = Items(
                category_id=60,
                title=f'Title_{i}',
                item_location=f'Address for {i}',
            )
            session.add(item)
        session.commit()


if __name__ == '__main__':
    engine = get_engine()
    create_items_table(engine)
    session_factory = sessionmaker(engine)
    insert_to_items(session_factory)
