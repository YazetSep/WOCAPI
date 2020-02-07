import datetime

from flask_login import UserMixin
from sqlalchemy import ForeignKey, Table
from sqlalchemy.orm import relationship

from __init__ import db, Base

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
    displayname = db.Column('displayname', db.String(50), nullable=False)
    email = db.Column('email', db.String(50), nullable=False)
    password = db.Column('password', db.String(200), nullable=False)
    firstName = db.Column('first', db.String(50), nullable=True)
    lastName = db.Column('last', db.String(50), nullable=True)
    activated = db.Column('activated', db.Boolean, nullable=False)
    dateOfBirth = db.Column('dateofbirth', db.Date, nullable=True)
    dateCreated = db.Column('datecreated', db.DateTime, default=datetime.datetime.utcnow())

    savedevents = relationship('Events', secondary=savedevents_table)
    rsvp = relationship('Events', secondary=rsvp_table)

    rank = relationship('Ranks', backref='users')

    @staticmethod
    def build_user_dict(user):
        # rank = user.rank
        result = {'uid': user.id, 'displayname': user.displayname, 'email': user.email,
                  'activated': user.activated}  # , 'rank': rank
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
    def build_event_dict(event, user):
        saved = False
        if user is not None:
            eids = [event.eid for event in user.savedevents]
            saved = True if event.eid in eids else False

        posted_by = event.postedBy.displayname
        result = {
            'eid': event.eid,
            'title': event.title,
            'briefDescription': event.briefDescription,
            'dateTimestamp': event.startTime,
            'startHour': event.startTime,
            'endHour': event.endTime,
            'imageurl': event.imageurl,
            'place': event.place,
            'categoryName': event.categoryname,
            'contactEmail': event.contactEmail,
            'postedBy': posted_by,
            'fullDescription': event.fullDescription,
            'contactPhone': event.contactPhone,
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
    def buld_analytic_dict(analytic):

        result = {
            'event': Events.build_event_dict(analytic.event, None),
            'views': analytic.views,
            'saved_count': analytic.saved_count,
            'rsvp_count': len(analytic.event.rsvp)
        }
        return result
