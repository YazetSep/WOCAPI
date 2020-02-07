import bcrypt
import datetime

from flask_login import UserMixin
from sqlalchemy import ForeignKey, Table
from sqlalchemy.orm import relationship

from main import Base
from __init__ import db

savedevents_table = Table('savedevents', Base.metadata,
                          db.Column('eid', db.Integer, ForeignKey('events.eid'), nullable=False),
                          db.Column('uid', db.Integer, ForeignKey('users.uid'), nullable=False)
                          )

rsvp_table = Table('rsvp', Base.metadata,
                   db.Column('eid', db.Integer, ForeignKey('events.eid'), nullable=False),
                   db.Column('uid', db.Integer, ForeignKey('users.uid'), nullable=False)
                   )


class Categories(Base):
    __tablename__ = 'categories'
    name = db.Column('name', db.String(50), primary_key=True)
    events = relationship('Events')

    @staticmethod
    def build_cat_dict(category):
        result = {'name': category.name}
        return result


class Users(UserMixin, Base):
    __tablename__ = 'users'
    id = db.Column('uid', db.Integer, primary_key=True)
    display_name = db.Column('displayname', db.String(50), nullable=False)
    email = db.Column('email', db.String(50), nullable=False, unique=True)
    password = db.Column('password', db.String(200), nullable=False)
    first_name = db.Column('first', db.String(50), nullable=True)
    last_name = db.Column('last', db.String(50), nullable=True)
    activated = db.Column('activated', db.Boolean, nullable=False)
    date_of_birth = db.Column('dateofbirth', db.Date, nullable=True)
    date_created = db.Column('datecreated', db.DateTime, default=datetime.datetime.utcnow())

    saved_events = relationship('Events', secondary=savedevents_table)
    rsvp = relationship('Events', secondary=rsvp_table)

    rank = relationship('Ranks', backref='users')

    def add_or_remove_saved_event(self, event):
        if event in self.savedevents:
            self.savedevents.remove(event)
            saved = False
        else:
            self.savedevents.append(event)
            saved = True
        db.session.commit()
        return saved

    def rsvp_or_unrsvp(self, event):
        if self in event.rsvp:
            self.rsvp.remove(event)
            db.session.commit()
            rsvp = False
        else:
            self.rsvp.append(event)
            db.session.commit()
            rsvp = True
        return rsvp

    @staticmethod
    def get_user_by_email(email):
        return db.session.query(Users).filter(Users.email == email).first()

    @staticmethod
    def create_user(data):
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = Users(
            displayname=data['displayname'],
            email=data['email'],
            password=hashed_password,
            firstName=data['firstname'],
            lastName=data['lastname'],
            activated=0,
            dateOfBirth=None
        )
        db.session.add(new_user)
        db.session.commit()

    def build_user_dict(self):
        # rank = user.rank
        result = {'uid': self.id, 'displayname': self.displayname, 'email': self.email,
                  'activated': self.activated}  # , 'rank': rank
        return result


class Ranking(Base):
    __tablename__ = 'ranking'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class Ranks(Base):
    __tablename__ = 'ranks'
    id = db.Column('id', db.Integer, primary_key=True)
    uid = db.Column('uid', db.Integer, ForeignKey(Users.id))
    rank = db.Column('rank', db.Integer, ForeignKey(Ranking.id))

    user = relationship('Users')
    ranking = relationship('Ranking')

    @staticmethod
    def build_rank_dict(rank):
        result = {'rank': rank.rank}
        return result


class Events(Base):
    __tablename__ = 'events'
    eid = db.Column('eid', db.Integer, primary_key=True)
    title = db.Column('title', db.String(50), nullable=False)
    imageurl = db.Column('imageurl', db.String(300), nullable=True)
    briefDescription = db.Column('briefdescription', db.String(240), nullable=False)
    fullDescription = db.Column('fulldescription', db.String)
    startTime = db.Column('starttimestamp', db.DateTime, nullable=False)
    endTime = db.Column('endtimestamp', db.DateTime, nullable=False)
    place = db.Column('place', db.String(50), nullable=False)
    categoryname = db.Column(db.String, ForeignKey(Categories.name), nullable=False)
    contactEmail = db.Column('contactemail', db.String(50))
    contactPhone = db.Column('contactphone', db.String(50))
    postedUid = db.Column('postedby', db.Integer, ForeignKey(Users.id))  # USER FOREIGN KEY
    postedTimeStamp = db.Column('postedtimestamp', db.DateTime, default=datetime.datetime.utcnow())

    postedBy = relationship('Users', foreign_keys='Events.postedUid')
    rsvp = relationship('Users', secondary=rsvp_table)

    @staticmethod
    def get_event_by_id(eid):
        return db.session.query(Events).filter(Events.eid == eid).first()

    def build_event_dict(self, user):
        saved = False
        if user is not None:
            eids = [self.eid for event in user.savedevents]
            saved = self.eid in eids

        posted_by = self.postedBy.displayname
        result = {
            'eid': self.eid,
            'title': self.title,
            'briefDescription': self.briefDescription,
            'dateTimestamp': self.startTime,
            'startHour': self.startTime,
            'endHour': self.endTime,
            'imageurl': self.imageurl,
            'place': self.place,
            'categoryName': self.categoryname,
            'contactEmail': self.contactEmail,
            'postedBy': posted_by,
            'fullDescription': self.fullDescription,
            'contactPhone': self.contactPhone,
            'saved': saved
        }
        return result


class EventAnalytics(Base):
    __tablename__ = 'eventanalytics'
    id = db.Column('id', db.Integer, primary_key=True)
    eid = db.Column('event', db.Integer, ForeignKey(Events.eid))
    views = db.Column('views', db.Integer, default=0)
    saved_count = db.Column('saved_count', db.Integer, default=0)

    event = relationship('Events', foreign_keys='EventAnalytics.eid')

    @staticmethod
    def get_event_analytic_by_id(eid):
        return db.session.query(EventAnalytics).filter(EventAnalytics.eid == eid).first()

    @staticmethod
    def buld_analytic_dict(analytic):

        result = {
            'event': Events.build_event_dict(analytic.event, None),
            'views': analytic.views,
            'saved_count': analytic.saved_count,
            'rsvp_count': len(analytic.event.rsvp)
        }
        return result
