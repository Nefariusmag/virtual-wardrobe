from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import PasswordType
import config


psqlconnect = f'postgresql://{config.db_login}:{config.db_password}@{config.db_host}:5432/{config.db_name}'
engine = create_engine(psqlconnect, echo=False)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(PasswordType(
        schemes=[
            'pbkdf2_sha512',
            'md5_crypt'
        ],
        deprecated=['md5_crypt']
    ))
    email = Column(String)
    # todo add true format for geo column
    geo = Column(String)
    clothes = relationship('Clothes')

    def __init__(self, name, password, email, geo):
        self.name = name
        self.password = password
        self.email = email
        self.geo = geo

    def __repr__(self):
        return f'<User({self.name},{self.password},{self.email},{self.geo})>'

    def get_id_from_name(self):
        return self.id


def get_object_by_name(name):
    assert type(name) is str
    # todo fix getting only first value from list
    for user_id in session.query(User.id).filter(User.name == name):
        return user_id


class Clothes(Base):
    __tablename__ = 'clothes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    type = Column(String)
    top = Column(Boolean)
    bottom = Column(Boolean)
    upper = Column(Boolean)
    lower = Column(Boolean)
    temperature_min = Column(Integer)
    temperature_max = Column(Integer)

    def __init__(self, user_id, name, type, top, bottom, upper, lower, temperature_min, temperature_max):
        self.user_id = user_id
        self.name = name
        self.type = type
        self.top = top
        self.bottom = bottom
        self.upper = upper
        self.lower = lower
        self.temperature_min = temperature_min
        self.temperature_max = temperature_max

    def __repr__(self):
        return f'<Clothes({self.user_id},{self.name},{self.type},{self.top},{self.bottom},{self.upper},{self.lower},{self.temperature_min},{self.temperature_max})>'


def get_clothes_in_temperature(user_id, temperature):
    # todo add check user_id on number
    assert type(temperature) is int
    clothes_in_temperature = []
    for thing_in_temperature in session.query(Clothes).filter(Clothes.user_id == user_id).filter(
            Clothes.temperature_min <= temperature).filter(Clothes.temperature_max >= temperature):
        clothes_in_temperature.append(thing_in_temperature.name)
    return clothes_in_temperature


Base.metadata.create_all(engine)


def add_test_data():
    session.add_all([User('Дима', 'qwerty12345', 'nefariusmag@gmail.com', '55.785280, 37.634209'),
                     User('Дима2', 'qwerty12345', 'nefariusmag@gmail.com', '55.785280, 37.634209'),
                     User('Дима3', 'qwerty12345', 'nefariusmag@gmail.com', '55.785280, 37.634209'),
                     Clothes(3, 'Шапка межсезонная', 'Шапка', True, False, True, False, 0, 15),
                     Clothes(3, 'Куртка', 'Куртка', True, False, True, False, -10, 5),
                     Clothes(3, 'Джинсы', 'Штаны', True, False, False, True, 5, 20),
                     Clothes(3, 'Ботинки', 'Обувь', True, False, False, True, -5, 15),
                     Clothes(3, 'Майка алкоголичка', 'Футболка', False, True, True, False, -10, 25),
                     Clothes(3, 'Шарф', 'Шарф', True, False, False, False, -25, 5),
                     Clothes(3, 'Рубашка', 'Рубашка', False, True, False, False, -5, 20)])
    session.commit()

# Select clothes for user in temperature
#
# user_id = get_object_by_name('Дима3')
# print(get_clothes_in_temperature(user_id, -10))

# alex = User('Алекс', 'qwerty12345', 'nefariusmag@gmail.com', '55.785280, 37.634209')
# session.add(alex)
# session.commit()
# print(alex.get_id_from_name())
