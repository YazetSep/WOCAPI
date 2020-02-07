# heroku Password: 3b884db910a7ed97661a75d3203b101e7bf41248fb6c8b36d39ff02dc1556fd5
import os
import random
import string
from datetime import datetime

import bcrypt
from flask import jsonify, request
from flask_cors import CORS
from flask_jwt import JWT
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, jwt_optional
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from __init__ import app, db, Base
from config.herokudbconfig import pg_config
from models import Events, Users, Categories, EventAnalytics, Ranks

CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(password)s@%(host)s:%(port)s/%(dbname)s' % pg_config
app.config['SECRET_KEY'] = "THISISSECRET"
login_manager = LoginManager()
login_manager.init_app(app)
Session = sessionmaker(autoflush=False)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

url = "127.0.0.1"
upload_folder = '/var/www/html/upload'

if (not os.path.exists(upload_folder)):
    os.makedirs(upload_folder)
    app.config['upload_folder'] = upload_folder
else:
    app.config['upload_folder'] = upload_folder

Base.metadata.create_all(engine)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).filter(Users.id == int(user_id)).first()


def authenticate(email, password):
    user = db.session.query(Users).filter(Users.email == email).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        login_user(user)
        return user
    else:
        return 'bro what'


def identity(payload):
    user_id = payload['identity']
    return db.session.query(Users).filter(Users.email == user_id).first()


jwt = JWT(app, authenticate, identity)


# ---------------------------HELPER METHODS-------------------------------------------


def get_mobile_or_web_user():
    username = get_jwt_identity()
    user = None
    if username is not None:
        user = db.session.query(Users).filter(Users.email == username).first()
    else:
        pass
        # try:
        #     uid = request.args['uid']
        #     user = db.session.query(Users).filter(Users.id == int(uid)).first()
        # except KeyError:
        #     pass
    return user

def rankAssocAdmin(user):
    rank = db.session.query(Ranks).filter(Ranks.uid == user.id).first().rank
    return (rank == 1 or rank == 2)
# ---------------------------MOBILE API-----------------------------------------------

@app.route('/WhatsOnCampus/mobile/register', methods=['POST'])
def mobile_register():
    if request.method == 'POST':
        hashed_password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = Users(
            displayname=request.form['displayname'],
            email=request.form['email'],
            password=hashed_password,
            firstName=request.form['firstname'],
            lastName=request.form['lastname'],
            activated=0,
            dateOfBirth=None,
            dateCreated=datetime.utcnow()
        )
        db.session.add(new_user)
        db.session.commit()
        access_token = create_access_token(identity=request.form['email'], expires_delta=False)
        return jsonify(access_token=access_token, displayname=request.form['displayname']), 201
    else:
        return jsonify(response="Error has occured"), 500


@app.route('/WhatsOnCampus/mobile/login', methods=['POST'])
def mobile_login():
    email = request.form['email']
    password = request.form['password']
    user = db.session.query(Users).filter(Users.email == email).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        access_token = create_access_token(identity=email, expires_delta=False)
        ranks = [rank.rank for rank in user.rank]
        return jsonify(access_token=access_token, displayname=user.displayname, Rank=ranks), 201
    else:
        return jsonify(response="Invalid email or password"), 400


@app.route('/WhatsOnCampus/mobile/save/<eid>', methods=['POST'])
@jwt_required
def mobile_saved(eid):
    # extract user from access_token
    username = get_jwt_identity()
    user = db.session.query(Users).filter(Users.email == username).first()
    event = db.session.query(Events).filter(Events.eid == eid).first()  # TODO: Change this to get
    event_analytic = db.session.query(EventAnalytics).filter(EventAnalytics.eid == eid).first()
    if event in user.savedevents:
        user.savedevents.remove(event)
        event_analytic.saved_count -= 1
        db.session.commit()
        return jsonify(response='unsaved'), 201
    else:
        user.savedevents.append(event)
        event_analytic.saved_count += 1
        db.session.commit()
        return jsonify(response='saved'), 201


@app.route('/WhatsOnCampus/mobile/rsvp/<eid>', methods=['POST'])
@jwt_required
def mobile_rsvp(eid):
    username = get_jwt_identity()
    user = db.session.query(Users).filter(Users.email == username).first()
    event = db.session.query(Events).filter(Events.eid == eid).first()  # TODO: Change this to get

    if user in event.rsvp:
        user.rsvp.remove(event)
        db.session.commit()
        return jsonify(response="un-rsvp")
    else:
        user.rsvp.append(event)
        db.session.commit()
        return jsonify(response="rsvp")


@app.route('/WhatsOnCampus/mobile/save/list')
@jwt_required
def mobile_saved_id_list():
    username = get_jwt_identity()
    user = db.session.query(Users).filter(Users.email == username).first()
    saved_events_list = [saved_event.eid for saved_event in user.savedevents]
    return jsonify(response=saved_events_list)


@app.route('/WhatsOnCampus/mobile/savedevents/')
@jwt_required
def mobile_savedevents():
    username = get_jwt_identity()
    user = db.session.query(Users).filter(Users.email == username).first()
    saved_events = []
    for event in user.savedevents:
        if event.endTime >= datetime.utcnow():
            saved_events.append(event)
    saved_events.sort(key=lambda Events: Events.startTime)
    saved_events = [Events.build_event_dict(event, user) for event in saved_events]
    return jsonify(Events=saved_events)


# ---------------------------------GENERAL API------------------------------


@login_required
@app.route('/')
def home():
    return "Welcome to What's on Campus!"


@app.route('/WhatsOnCampus/ranks/')
@jwt_required
def getRanks():
    username = get_jwt_identity()
    user = db.session.query(Users).filter(Users.email == username).first()
    ranks = [rank.rank for rank in user.rank]
    return jsonify(Ranks=ranks)


@app.route('/WhatsOnCampus/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        formDisplayname = request.form['displayname']
        formEmail = request.form['email']
        formFName = request.form['firstname']
        formLName = request.form['lastname']
        hashed_password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        newUser = Users(
            displayname=formDisplayname,
            email=formEmail,
            password=hashed_password,
            firstName=formFName,
            lastName=formLName,
            activated=0,
            dateOfBirth=None,
            dateCreated=datetime.utcnow()
        )

        # check if user exists
        checkUser = db.session.query(Users).filter(Users.email == formEmail).first()
        checkEmail = db.session.query(Users).filter(Users.displayname == formDisplayname).first()
        if checkUser or checkEmail:
            return jsonify(success=False, response="User already exists"), 409
        else:
            db.session.add(newUser)
            db.session.commit()
            login_user(newUser)
            return jsonify(success=True, User=Users.build_user_dict(newUser)), 201
    else:
        return jsonify(success=False, response="Error has occured"), 500


@app.route('/WhatsOnCampus/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = db.session.query(Users).filter(Users.email == email).first()  # TODO: Change this to get
    passw = bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8'))
    if user and passw:
        logged = login_user(user)
        ranks = [rank.rank for rank in user.rank]
        return jsonify(success=logged, User=Users.build_user_dict(user), Ranks=ranks), 201
    else:
        return jsonify(success=False, response="Wrong email or password"), 400


@login_required
@app.route('/WhatsOnCampus/logout')
def logout():
    logout_user()
    return jsonify(response="Logged out"), 201


@login_required
@app.route('/WhatsOnCampus/loggeduser')
def loggeduser():
    return 'The current user is ' + current_user.displayname


@login_required
@app.route('/WhatsOnCampus/users/<int:uid>', methods=['GET', 'PUT'])
def getUserById(uid):
    # if request.method == 'GET':
    #     return UserHandler().getUserById(uid)
    pass


@app.route('/WhatsOnCampus/changepassword', methods=['POST'])
@jwt_required
def changePassword():
    currentPassword = request.form['currentPassword']
    newPassword = request.form['newPassword']
    confirmPassword = request.form['confirmPassword']

    username = get_jwt_identity()
    user = db.session.query(Users).filter(Users.email == username).first()

    if currentPassword != newPassword:
        if len(newPassword) >= 8:
            if user and bcrypt.checkpw(currentPassword.encode('utf-8'), user.password.encode('utf-8')):
                if newPassword == confirmPassword:
                    hashed_password = bcrypt.hashpw(newPassword.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    user.password = hashed_password
                    db.session.commit()

                    return jsonify(success=True, response="Successfully changed password!"), 201
                else:
                    return jsonify(success=False, response="Confirm password doesn't match new password"), 400
            else:
                return jsonify(success=False, response="Invalid current password"), 400
        else:
            return jsonify(success=False, response="New password requires at least 8 characters"), 400
    else:
        return jsonify(success=False, response="New password is equal to current password"), 400


@app.route('/WhatsOnCampus/activate', methods=['POST'])
def activateAccount():
    return True


@app.route('/WhatsOnCampus/resetpassword', methods=['POST'])
def resetPassword():
    #Person inputs their email
    #A confirmation code is sent to email with random code for confirmation
    #If code hasn't expired.
    #Person inputs new password. Password gets updated
    return jsonify(msg="reset pass")


@app.route('/WhatsOnCampus/events', methods=['GET', 'POST'])
@jwt_optional
def getEvents():
    # events = [Events.build_event_dict(event) for event in db.session.query(Events).all()]
    # return jsonify(Events=events)

    """
    FOR MOBILE CLIENTS:
        TOKEN MUST BE SENT IF SAVE_FLAG FEATURE WANTS TO BE USED


    If method == GET
        Returns a list of events ordered by start time

        ?page=<int> is required
        example: /events?page=1
        page must start at 1, will return the first 10 events.

        To filter by categories add the following: ?category=<String>
        example: /events?page=1&category=engineering
        (order doesn't matter)

        if succesful, will return json with the following format:
        [Events={
            [{
            EVENT VARIABLES HERE
            }]
        }]

    if method == POST
        Body must contain the event variables.
        Datetimes must contain timezone
        returns json containing success and the newly created event


    """

    if request.method == 'GET':
        user = get_mobile_or_web_user()
        try:
            category_name = None
            if 'category' in request.args:
                category_name = request.args['category']
            page = int(request.args['page']) - 1
            if category_name is None:
                events = [Events.build_event_dict(event, user) for event in
                          db.session.query(Events).filter(Events.endTime > datetime.utcnow()).
                              order_by('starttimestamp').limit(10).offset(page * 10)]
            else:
                events = [Events.build_event_dict(event, user) for event in db.session.query(Events).
                    filter(Events.categoryname == category_name, Events.endTime > datetime.utcnow()).
                    order_by('starttimestamp').limit(10).offset(page * 10)]
            return jsonify(Events=events), 200
        except (KeyError, ValueError) as e:
            # log exception
            return jsonify(msg='Malformed request'), 400

    elif request.method == 'POST':
        user = get_mobile_or_web_user()

        if not rankAssocAdmin(user):
            return jsonify(response='You are NOT ALLOWED'), 400
        else:
            startTime = datetime.strptime(request.form['starttimestamp'], '%Y-%m-%d %H:%M:%S.%f%z')
            endTime = datetime.strptime(request.form['endtimestamp'], '%Y-%m-%d %H:%M:%S.%f%z')

            startTime = startTime.utcfromtimestamp(startTime.timestamp())
            endTime = endTime.utcfromtimestamp(endTime.timestamp())

            ftitle = request.form['title']
            fimage = request.files['imageurl']
            fbriefDescription = request.form['briefdescription']
            ffullDescription = request.form['fulldescription']
            fstartTime = startTime
            fendTime = endTime
            fplace = request.form['place']
            fcategoryname = request.form['categoryname']  # foreign key
            fcontactEmail = request.form['contactemail']  # user email
            fcontactPhone = request.form['contactphone']

            file = fimage
            extension = os.path.splitext(file.filename)[1]
            rand = ''.join(
                random.choices(string.ascii_letters + string.digits, k=5))  # Generate random stuff to make name unique
            f_name = rand + extension
            f_name = f_name.replace(" ", "").strip()
            file.save(os.path.join(app.config['upload_folder'], f_name))

            newEvent = Events(
                title=ftitle,
                imageurl='/upload/' + f_name,
                briefDescription=fbriefDescription,
                fullDescription=ffullDescription,
                startTime=fstartTime,  # fstartTime,//convert these to datetime
                endTime=fendTime,  # fendTime,
                place=fplace,
                categoryname=fcategoryname,
                contactEmail=fcontactEmail,
                contactPhone=fcontactPhone,
                postedUid=user.id,
                postedTimeStamp=datetime.utcnow()
            )

            new_event_analytic = EventAnalytics(event=newEvent)

            checkTitle = db.session.query(Events).filter(Events.title == ftitle).first()
            checkUid = db.session.query(Events).filter(Events.postedUid == user.id).first()

            if checkTitle and checkTitle.postedUid == user.id:
                return jsonify(success=False, response="You already posted an event with this title"), 400
            else:
                db.session.add(newEvent)
                db.session.add(new_event_analytic)
                db.session.commit()
                return jsonify(success=True, Event=Events.build_event_dict(newEvent, user)), 201
                # Event=Events.build_user_dict(newEvent)

    elif request.method == 'PUT':
        user = get_mobile_or_web_user()
        if user is None:
            return jsonify(msg='Forbidden'), 403
        eid = request.form['eid']


@app.route('/WhatsOnCampus/event/update/<int:eid>', methods=['GET', 'PUT'])
@jwt_required
def UpdateEvent(eid):
    allowed = False
    past = True
    user = get_mobile_or_web_user()
    event = db.session.query(Events).get(eid)

    if not rankAssocAdmin(user):
        return jsonify(msg='Forbidden'), 403

    if event.postedUid == user.id:
        allowed = True

    if event.endTime > datetime.utcnow():
        past=False

    #first get the event data and make sure the user is the owner
    if request.method == 'GET':
        if allowed:
            if past:
                return jsonify(success=True,  past=past, response="This event has passed and cannot be edited", Events=Events.build_event_dict(event, user)), 201
            else:
                return jsonify(success=True, past=past, Events=Events.build_event_dict(event, user)), 201
        else:
            return jsonify(success=False, response="This event does not exist or it's you're not the owner"), 400
    elif request.method == 'PUT':
        if allowed and not past:
            startTime = datetime.strptime(request.form['starttimestamp'], '%Y-%m-%d %H:%M:%S.%f%z')
            endTime = datetime.strptime(request.form['endtimestamp'], '%Y-%m-%d %H:%M:%S.%f%z')

            startTime = startTime.utcfromtimestamp(startTime.timestamp())
            endTime = endTime.utcfromtimestamp(endTime.timestamp())

            ftitle = request.form['title']
            fbriefDescription = request.form['briefdescription']
            ffullDescription = request.form['fulldescription']
            fstartTime = startTime
            fendTime = endTime
            fplace = request.form['place']
            fcategoryname = request.form['categoryname']  # foreign key
            fcontactEmail = request.form['contactemail']  # user email
            fcontactPhone = request.form['contactphone']


            #CAN'T CHANGE IMAGE
            # file = fimage
            # extension = os.path.splitext(file.filename)[1]
            # rand = ''.join(
            #     random.choices(string.ascii_letters + string.digits, k=5))  # Generate random stuff to make name unique
            # f_name = ftitle + rand + extension
            # f_name = f_name.replace(" ", "").strip()
            # file.save(os.path.join(app.config['upload_folder'], f_name))




            event.title = ftitle
            # event.imageurl = '/upload/' + f_name
            event.briefDescription = fbriefDescription
            event.fullDescription = ffullDescription
            event.startTime = fstartTime  # fstartTime,//convert these to datetime
            event.endTime = fendTime  # fendTime,
            event.place = fplace
            event.categoryname = fcategoryname
            event.contactEmail = fcontactEmail
            event.contactPhone = fcontactPhone

            db.session.commit()
            return jsonify(success=True), 201
        else:
            return jsonify(success=False, response="You're not allowed to edit this event"), 400

@app.route('/WhatsOnCampus/event/<int:eid>', methods=['GET'])
@jwt_optional
def getEventById(eid):
    user = get_mobile_or_web_user()
    event = db.session.query(Events).get(eid)
    if event.endTime > datetime.utcnow():
        return jsonify(Events=Events.build_event_dict(event, user))
    else:
        return jsonify(msg='Event not found'), 404


@app.route('/WhatsOnCampus/users/events', methods=['GET'])
@jwt_required
def get_events_by_user():
    user = get_mobile_or_web_user()
    rank = db.session.query(Ranks).filter(Ranks.uid == user.id).first().rank

    if rank == 1 or rank == 2:
        events = [Events.build_event_dict(event, user) for event in
                  db.session.query(Events).filter(Events.postedUid == user.id).
                      order_by('starttimestamp')]
        return jsonify(Events=events), 200
    else:
        return jsonify(success=False, response="Forbidden"), 403


@app.route('/WhatsOnCampus/categories')
def getCategories():
    categories = db.session.query(Categories).order_by(Categories.name).all()
    return jsonify(Categories=[category.name for category in categories])


@app.route('/WhatsOnCampus/events/search/<string:search>')
def getEventsBySearch(search):
    # return EventHandler().getEventsBySearch(search)
    pass


# A POST with the uid adds or removes a saved event to a user
# A GET with the uid verifies if the user have saved an event
@login_required
@app.route('/WhatsOnCampus/events/save/<int:eid>', methods=['GET', 'POST'])
def saveEvent(eid):
    # TODO: CRITICAL CRITICAL NO ACTUAL AUTHENTICATION GOING ON  HERE
    # TODO: LOGGED IN USER IN REQUEST MUST BE VERIFIED
    # TODO: ANYONE CAN ACCESS THIS BY ENTERING THE UID IN POST
    if request.method == 'GET':
        try:
            uid = request.args['uid']
        except KeyError:
            return jsonify(response='Malformed request'), 400
        user = db.session.query(Users).filter(Users.id == uid).first()
        saved_events_list = [saved_event.eid for saved_event in user.savedevents]
        return jsonify(response=saved_events_list)

    if request.method == 'POST':
        uid = request.form['uid']
        user = db.session.query(Users).filter(Users.id == uid).first()  # TODO: Change this to get
        event = db.session.query(Events).filter(Events.eid == eid).first()  # TODO: Change this to get
        event_analytic = db.session.query(EventAnalytics).filter(EventAnalytics.eid == eid).first()
        if event:
            if event in user.savedevents:
                user.savedevents.remove(event)
                event_analytic.saved_count -= 1
                db.session.commit()
                return jsonify(response='unsaved'), 201
            else:
                user.savedevents.append(event)
                event_analytic.saved_count += 1
                db.session.commit()
                return jsonify(response='saved'), 201
        else:
            return jsonify(response='error doesn\'t exist'), 409


@login_required
@app.route('/WhatsOnCampus/users/<int:uid>/events/saved', methods=['GET'])
def savedEvents(uid):
    # TODO: CRITICAL CRITICAL NO ACTUAL AUTHENTICATION GOING ON  HERE
    # TODO: LOGGED IN USER IN REQUEST MUST BE VERIFIED
    # TODO: ANYONE CAN ACCESS THIS BY ENTERING THE UID IN URL
    user = db.session.query(Users).filter(Users.id == uid).first()  # TODO: Change this to get

    saved_events = []
    for event in user.savedevents:
        if event.endTime > datetime.utcnow():
            saved_events.append(event)
    saved_events.sort(key=lambda Events: Events.startTime)
    saved_events = [Events.build_event_dict(event, user) for event in saved_events]
    return jsonify(Events=saved_events)


@app.route('/WhatsOnCampus/events/analytics', methods=['GET'])
@jwt_required
def postedEvents():
    username = get_jwt_identity()
    user = db.session.query(Users).filter(Users.email == username).first()
    events_analytics = db.session.query(EventAnalytics).filter(Events.postedBy == user)

    events_analytics_dict = [EventAnalytics.buld_analytic_dict(analytic) for analytic in events_analytics]
    return jsonify(Events=events_analytics_dict)


# --------------------------ANALYTICS API----------------------------------------


@app.route('/WhatsOnCampus/events/<int:eid>/view')
def viewedEvent(eid):
    event_analytic = db.session.query(EventAnalytics).filter(EventAnalytics.eid == eid).first()
    event_analytic.views += 1
    db.session.commit()

    return jsonify(msg='success'), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
