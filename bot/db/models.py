import datetime
from copy import copy, deepcopy
from typing import Optional

from aiogram import types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from sqlalchemy import Column, Integer, Table, ForeignKey, VARCHAR, BigInteger, Date, select, Text, Boolean, \
    CursorResult, ScalarResult
from sqlalchemy.orm import relationship, sessionmaker, selectinload
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import check_password_hash

Base = declarative_base()

article_author_association = Table(
    'pharmacy_author',
    Base.metadata,
    Column('pharmacy_id', Integer, ForeignKey('pharmacies.id')),
    Column('author_id', Integer, ForeignKey('users.id'))
)

cart = Table(
    'cart',
    Base.metadata,
    Column('pharmacy_id', Integer, ForeignKey('pharmacies.id')),
    Column('medicine_id', Integer, ForeignKey('medicines.id'))
)


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    created = Column(Date, default=datetime.datetime.now())
    updated = Column(Date, onupdate=datetime.datetime.now())


class User(BaseModel):
    __tablename__ = 'users'

    user_id = Column(BigInteger, unique=True, nullable=True)
    username = Column(VARCHAR(120), nullable=True)
    fullname = Column(VARCHAR(32))
    password = Column(Text)
    passed_pwd = Column(Boolean)
    phone = Column(VARCHAR(32), unique=True)
    pharmacies = relationship('Pharmacy', secondary=article_author_association, back_populates='authors')
    lang = Column(VARCHAR(15))
    orders = relationship('Order', backref="author")

    def __str__(self) -> str:
        return f"<User: {self.user_id}>"


class Unautorized_User(BaseModel):
    __tablename__ = 'unautorized_user'
    user_id = Column(BigInteger, unique=True, nullable=True)
    username = Column(VARCHAR(120), nullable=True)
    fullname = Column(VARCHAR(32))
    lang = Column(VARCHAR(15))

    def __str__(self) -> str:
        return f"<User: {self.user_id}>"


class Pharmacy(BaseModel):
    __tablename__ = 'pharmacies'

    # ID поста
    inn = Column(VARCHAR(50), nullable=False)
    name = Column(VARCHAR(50), nullable=False)
    district = Column(VARCHAR(50), nullable=False)
    director = Column(VARCHAR(50))
    phone = Column(VARCHAR(50))
    authors = relationship('User', secondary=article_author_association, back_populates='pharmacies')
    medicines = relationship('Medicine', secondary=cart, back_populates='pharmacies')
    orders = relationship('Order', backref="pharmacy")


class Medicine(BaseModel):
    __tablename__ = 'medicines'
    name = Column(VARCHAR(100), unique=True)
    price = Column(Integer, default=0)
    pharmacies = relationship('Pharmacy', secondary=cart, back_populates='medicines')
    orders = relationship('Order', backref="medicine")


class Order(BaseModel):
    __tablename__ = 'orders'
    quantity = Column(Integer, default=0)
    leftover = Column(Integer, default=0)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    pharmacy_id = Column(Integer, ForeignKey('pharmacies.id'))
    medicine_id = Column(Integer, ForeignKey('medicines.id'))


async def get_user(user_id: int, session: sessionmaker) -> bool:
    """

    :param user_id:
    :param session:
    :return:
    """

    async with session() as session:
        result = await session.execute(
            select(User).filter(User.user_id == user_id).options(selectinload(User.pharmacies)))
        # result2 = await session.execute(
        #     select(Pharmacy).options(selectinload(Pharmacy.authors)))
        res: User = result.scalar()
        # res2: Pharmacy = result2.scalar()
        # res.pharmacies.append(res2)
        # print(res.pharmacies)
        # print(res2.id)
        # await session.commit()
        if res:
            if res.passed_pwd:
                return True
    return False


async def get_user_phone(session: sessionmaker, phone: str = None, password=None,
                         message: types.Message = None) -> bool:
    """

    :param session:
    :param phone:
    :param password:
    :param message:
    :return:
    """

    async with session() as session:
        result = await session.execute(
            select(User).filter(User.phone.like(phone)).options(selectinload(User.pharmacies)))
        res: User = result.scalar()

        if res is None:
            return False

        if password:
            check_pw = check_password_hash(str(res.password), password)

            if check_pw:
                res.passed_pwd = True
                res.username = message.from_user.username
                res.fullname = message.from_user.full_name
                res.user_id = message.from_user.id
                await session.commit()
                return True
        else:
            return True


async def get_lang(user_id, session: sessionmaker):
    async with session() as session:
        user = await session.execute(select(User).filter_by(user_id=int(user_id)))
        user = user.scalar()

        if user:
            return user.lang
        else:
            user = await session.execute(select(Unautorized_User).filter_by(user_id=int(user_id)))
            user = user.scalar()

            if user:
                print('here')
                return user.lang


async def save_pharmacy(data: dict, session, message):
    async with session() as session:
        pharmacy = Pharmacy(inn=data['inn'], name=data['name'],
                            district=data['district'], director=data['fio_director'],
                            phone=data['phone']
                            )
        session.add(pharmacy)
        result = await session.execute(
            select(User).filter(User.user_id == message.from_user.id).options(selectinload(User.pharmacies)))
        user = result.scalar()
        user.pharmacies.append(pharmacy)
        await session.commit()


async def get_medicine(session: sessionmaker, data: dict):
    async with session() as session:
        query: CursorResult = await session.execute(
            select(Medicine).filter(Medicine.name.ilike(f'%{data["med_name"]}%')))
        medicine = query.scalars().all()
        if medicine:
            kb_generator = [[KeyboardButton(text=x.name)] for x in medicine]
            kb_generator.append([KeyboardButton(text='back')])
            kb = ReplyKeyboardMarkup(keyboard=kb_generator, resize_keyboard=True, row_width=1, one_time_keyboard=True)
            return kb
        return False


async def get_ordered_medicine(session: sessionmaker, data: dict):
    async with session() as session:
        query: CursorResult = await session.execute(
            select(Order).join(Pharmacy, Order.pharmacy_id == Pharmacy.id).filter\
                (Pharmacy.name == data['pharmacy'], Pharmacy.district == data['district']).options(selectinload(Order.medicine)))
        order = query.scalars()
        if order:
            kb_generator = [[KeyboardButton(text=x.medicine.name)] for x in order]
            kb_generator.append([KeyboardButton(text='back')])
            kb = ReplyKeyboardMarkup(keyboard=kb_generator, resize_keyboard=True, row_width=1, one_time_keyboard=True)
            return kb
        return False


async def update_leftover_in_order(session: sessionmaker, data: dict):
    async with session() as session:
        # query1: CursorResult = await session.execute(
        #     select(Pharmacy).filter_by(name=data['pharmacy'], district=data['district']))
        # pharmacy: Pharmacy = query1.scalar()
        query: CursorResult = await session.execute(
            select(Order).join(Medicine, Order.medicine_id == Medicine.id).join(Pharmacy, Order.pharmacy_id == Pharmacy.id).filter(Pharmacy.name == data['pharmacy'],
                                                                                                                                   Pharmacy.district == data['district'],
                                                                                  Medicine.name == \
                                                                                  data['medicine'],
                                                                                  Order.user_id == data['user_id']).options(
                selectinload(Order.medicine)))
        order: Order = query.scalar()
        if order is not None:
            order.leftover = int(data['left'])
            await session.commit()
            return True
        else:
            return False


async def add_to_cart(session: sessionmaker, data: dict):
    async with session() as session:
        query1: CursorResult = await session.execute(
            select(Pharmacy).filter_by(name=data['pharmacy'], district=data['district']))
        query2: CursorResult = await session.execute(
            select(Medicine).filter(Medicine.name.ilike(f'%{data["med_name"]}%')).options(
                selectinload(Medicine.pharmacies)))


        pharmacy: Pharmacy = query1.scalar()
        medicine: Medicine = query2.scalar()

        query: CursorResult = await session.execute(
            select(Order).join(Medicine, Order.medicine_id == Medicine.id).filter(Order.pharmacy_id == pharmacy.id,
                                                                                  Order.medicine_id == \
                                                                                  medicine.id), Order.user_id == data['user_id'])

        order = query.scalar()

        if order:
            order.quantity += int(data['med_quantity'])
            await session.commit()
        else:
            order = Order(quantity=int(data['med_quantity']), user_id=data['user_id'], pharmacy_id=pharmacy.id,
                          medicine_id=medicine.id)
            session.add(order)
            await session.commit()

 # import  jpype
 #  import  asposecells
 #  jpype.startJVM()
 #  from asposecells.api import Workbook
 #  workbook = Workbook("2023-11-25.xlsx")
 #  workbook.save("2023-11-25.pdf")
 #  jpype.shutdownJVM()