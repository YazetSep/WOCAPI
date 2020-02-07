from flask import Blueprint 
from main import api 

events_api = Blueprint('events_api', __name__) 

class Events():

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
    @jwt_optional
    def get(): 
        user = get_mobile_or_web_user()
        try:
            # TODO: ENCAPSULATE THIS
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

    @jwt_optional
    def post(): 
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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))

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

    @jwt_optional
    def put(): 
        user = get_mobile_or_web_user()
        if user is None:
            return jsonify(msg='Forbidden'), 403
        eid = request.form['eid']


class UpdateEvent(eid):
    @jwt_required
    def __init__(self): 
        allowed = False
        past = True
        user = get_mobile_or_web_user()
        event = db.session.query(Events).get(eid)

        if not rankAssocAdmin(user):
            return jsonify(msg='Forbidden'), 403

        if event.postedUid == user.id:
            allowed = True

        if event.endTime > datetime.utcnow():
            past = False

    # first get the event data and make sure the user is the owner
    @jwt_required
    def get(eid): 
        if allowed:
            if past:
                return jsonify(success=True, past=past, response="This event has passed and cannot be edited",
                               Events=Events.build_event_dict(event, user)), 201
            else:
                return jsonify(success=True, past=past, Events=Events.build_event_dict(event, user)), 201
        else:
            return jsonify(success=False, response="This event does not exist or it's you're not the owner"), 400

    @jwt_required
    def put(eid):
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

            # CAN'T CHANGE IMAGE
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


class EventById():
    @jwt_optional
    def get(eid): 
        user = get_mobile_or_web_user()
        event = db.session.query(Events).get(eid)
        if event.endTime > datetime.utcnow():
            return jsonify(Events=Events.build_event_dict(event, user))
        else:
            return jsonify(msg='Event not found'), 404

class Categories():
    def get(): 
        categories = db.session.query(Categories).order_by(Categories.name).all()
        return jsonify(Categories=[category.name for category in categories])

api.add_resource(Events, '/events')
api.add_resource(UpdateEvent, '/event/update/<int:eid>')
api.add_resource(EventById, '/event/<int:eid>')
api.add_resource(Categories, '/categories')

