from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from sqlalchemy.ext.declarative import declarative_base

win = '✧'
pl  = '☑'
ls  = '✞'
lv  = '♥'


Base = declarative_base()


class Countries(Base):
    __tablename__ = 'countries'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    # user = relationship('User', back_populates='loc')
    cities = relationship('Cities', back_populates='country', cascade="all, delete, delete-orphan")


class Cities(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey('countries.id'))
    name = Column(String)
    country = relationship('Countries', back_populates='cities')
    # users = relationship('User', back_populates='city')

    currencies = relationship('Currencies', back_populates='city')
    # slots = relationship('Slots', back_populates='city')


class Currencies(Base):
    __tablename__ = 'currencies'

    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.id'))
    name = Column(String)
    city = relationship('Cities', back_populates='currencies')
    # users = relationship('User', back_populates='city')

    slots = relationship('Slots', back_populates='currency')


class Slots(Base):
    __tablename__ = 'slots'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    currency_id = Column(Integer, ForeignKey('currencies.id'))
    # city_id = Column(Integer, ForeignKey('cities.id'))

    date = Column(String)

    currency = relationship('Currencies', back_populates='slots')
    users = relationship('User', back_populates='slot')
    # city = relationship('Cities', back_populates='slots')


class Amount(Base):
    __tablename__ = 'amount'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    user = relationship('User', back_populates='amount')


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    # user_id = Column(Integer, unique=True)
    slot_id = Column(Integer, ForeignKey('slots.id'))
    amount_id = Column(Integer, ForeignKey('amount.id'))

    tname = Column(String)  # telegram name
    tid = Column(Integer)  # telegram name
    # score = Column(Integer, default=0)
    # skill = Column(String)
    date = Column(DateTime, default=datetime.utcnow())
    slot = relationship('Slots', back_populates='users')
    amount = relationship('Amount', back_populates='user')

    def __repr__(self):
        return "<User(name='%s', city='%s', id='%s')>" % (
            self.tname, self.city.name, self.tid)
    # group_id = Column(Integer, ForeignKey('group.id'))
    # payment = Column(Integer)

    # @staticmethod
    # def authed(user_id):
    #     if session.query(User).filter(User.user_id == user_id).all():
    #         return True
    #
    #     return False
    #
    # def get_most_recent(self, pos=0):
    #     most = None
    #     for plus in self.pluses:
    #         ok = plus.done if pos else 1
    #         if not most or plus.date > most.date and ok:
    #             most = plus
    #     return most

    # def score(self):
    #     return session.query(Tablo).filter_by(user_id=self.id). \
    #         filter_by(done=1).count()
    #
    # def show_stat(self):
    #     pluses = self.score()
    #     head = f"{pl} <b>Success days</b>: <code>{pluses}</code>\n" \
    #            f"{lv} <b>Lives</b>: <code>{self.lives}</code>\n\n" \
    #            f"{win} Completed games: <code>{self.wins}</code>\n" \
    #            f"{ls} Loosed games: <code>{self.looses}</code>\n\n"
    #     recent = self.get_most_recent()
    #     if recent:
    #         left = recent.date + timedelta(hours=24) - datetime.utcnow()
    #         mins = (left.seconds // 60) % 60
    #         h = left.seconds // 3600
    #         head += f"<b>Last plus:</b>\n<code>{recent.date.strftime('%Y-%m-%d')}</code>\n" \
    #                 f"<b>Left:</b> <code>{h}h {mins}m</code>"
    #     return head
    #
    #
    # def show_short_stat(self):
    #     pluses = self.score()
    #     head = f"@{self.name} " \
    #            f"{pl}<code>{pluses}</code>  " \
    #            f"{lv}<code>{self.lives}</code>  " \
    #            f"{win}<code>{self.wins}</code>  " \
    #            f"{ls}<code>{self.looses}</code>\n"
    #     return head
    #
    # def in_game_days(self):
    #     return session.query(Tablo).filter_by(user_id=self.id).count()
    #
    # def add_one(self, pos=1):
    #     self.pluses.append(Tablo(done=pos))
    #     session.add(self)
    #     session.commit()
    #

# class Locations(Base):
#     __tablename__ = 'locations'
#
#     id = Column(Integer, primary_key=True)
#     country = Column(String)
#     city = Column(String)
#     user = relationship('User', back_populates='loc')
#
#
#
# class Notify(Base):
#     __tablename__ = 'notify'
#
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('users.id'))
#     seen = Column(Integer)
#     typeof = Column(String)
#     user = relationship('User', back_populates='notify')
#
#
# class Group(Base):
#     __tablename__ = 'group'
#
#     id = Column(Integer, primary_key=True)
#     name = Column(Integer)
#     date_of_start = Column(String)
#     days = Column(Integer)
#     play_mode = Column(String)
#
#     users = relationship("User", back_populates='group')

