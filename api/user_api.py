from flask import Blueprint
from flask_jwt_extended import jwt_required
from main import api 

user_api = Blueprint('user_api', __name__) 

class Saved():
    @jwt_required
    def post(eid): 
        # extract user from access_token
        username = get_jwt_identity()
        user = Users.get_user_by_email(username)
        event = Events.get_event_by_id(eid)
        saved = user.add_or_remove_saved_event(event)
        response = jsonify(response='saved'), 201 if saved else jsonify(response='unsaved'), 201
        return response

class RSVP():
    @jwt_required
    def post(eid):
        username = get_jwt_identity()
        user = Users.get_user_by_email(username)
        event = Events.get_event_by_id(eid)
        rsvp = user.add_or_remove_saved_event(event)
        response = jsonify(response='rsvp'), 201 if rsvp else jsonify(response='un-rsvp'), 201
        return response

class SavedList():
    @jwt_required
    def get():
        username = get_jwt_identity()
        user = Users.get_user_by_email(username)
        saved_events_list = [saved_event.eid for saved_event in user.savedevents]
        return jsonify(response=saved_events_list)

class SavedEvents():
    @jwt_required
    def get(): 
        username = get_jwt_identity()
        user = Users.get_user_by_email(username)
        saved_events = []
        for event in user.savedevents:
            if event.endTime >= datetime.utcnow():
                saved_events.append(event)
        saved_events.sort(key=lambda Events: Events.startTime)
        saved_events = [event.build_event_dict(user) for event in saved_events]
        return jsonify(Events=saved_events)

class Ranks():
    @jwt_required
    def get(): 
        username = get_jwt_identity()
        # TODO: ENCAPSULATE THE GET USER QUERY
        user = Users.get_user_by_email(username)
        ranks = [rank.rank for rank in user.rank]
        return jsonify(Ranks=ranks)

class EventsByUser():
    @jwt_required
    def get(): 
        user = get_mobile_or_web_user()
        rank = db.session.query(Ranks).filter(Ranks.uid == user.id).first().rank

        if rank == 1 or rank == 2:
            events = [Events.build_event_dict(event, user) for event in
                      db.session.query(Events).filter(Events.postedUid == user.id).
                          order_by('starttimestamp')]
            return jsonify(Events=events), 200
        else:
            return jsonify(success=False, response="Forbidden"), 403

api.add_resource(Saved, '/save/<eid>') 
api.add_resource(rsvp, '/rsvp/<eid>')
api.add_resource(saved_list, '/save/list') 
api.add_resource(saved_events, '/savedevents')
api.add_resource(Ranks, '/ranks')
api.add_resource(EventsByUser,'/users/events')

#TODO: TO DELETE 
## A POST with the uid adds or removes a saved event to a user
## A GET with the uid verifies if the user have saved an event
#@login_required
#@app.route('/events/save/<int:eid>', methods=['GET', 'POST'])
#class saveEvent(eid):
#    # TODO: CRITICAL CRITICAL NO ACTUAL AUTHENTICATION GOING ON  HERE
#    # TODO: LOGGED IN USER IN REQUEST MUST BE VERIFIED
#    # TODO: ANYONE CAN ACCESS THIS BY ENTERING THE UID IN POST
#    if request.method == 'GET':
#        try:
#            uid = request.args['uid']
#        except KeyError:
#            return jsonify(response='Malformed request'), 400
#        user = db.session.query(Users).filter(Users.id == uid).first()
#        saved_events_list = [saved_event.eid for saved_event in user.savedevents]
#        return jsonify(response=saved_events_list)
#
#    if request.method == 'POST':
#        uid = request.form['uid']
#        user = db.session.query(Users).filter(Users.id == uid).first()  # TODO: Change this to get
#        event = db.session.query(Events).filter(Events.eid == eid).first()  # TODO: Change this to get
#        event_analytic = db.session.query(EventAnalytics).filter(EventAnalytics.eid == eid).first()
#        if event:
#            if event in user.savedevents:
#                user.savedevents.remove(event)
#                event_analytic.saved_count -= 1
#                db.session.commit()
#                return jsonify(response='unsaved'), 201
#            else:
#                user.savedevents.append(event)
#                event_analytic.saved_count += 1
#                db.session.commit()
#                return jsonify(response='saved'), 201
#        else:
#            return jsonify(response='error doesn\'t exist'), 409
#
#
#@login_required
#@app.route('/users/<int:uid>/events/saved', methods=['GET'])
#class savedEvents(uid):
#    # TODO: CRITICAL CRITICAL NO ACTUAL AUTHENTICATION GOING ON  HERE
#    # TODO: LOGGED IN USER IN REQUEST MUST BE VERIFIED
#    # TODO: ANYONE CAN ACCESS THIS BY ENTERING THE UID IN URL
#    user = db.session.query(Users).filter(Users.id == uid).first()  # TODO: Change this to get
#
#    saved_events = []
#    for event in user.savedevents:
#        if event.endTime > datetime.utcnow():
#            saved_events.append(event)
#    saved_events.sort(key=lambda Events: Events.startTime)
#    saved_events = [Events.build_event_dict(event, user) for event in saved_events]
#    return jsonify(Events=saved_events)


