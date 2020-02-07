from flask import Blueprint 
from main import api 

analytics_api = Blueprint('analytics_api', __name__) 

class NewEvents():
    @jwt_required
    def get(): 
        username = get_jwt_identity()
        user = db.session.query(Users).filter(Users.email == username).first()
        events_analytics = db.session.query(EventAnalytics).filter(Events.postedBy == user)

        events_analytics_dict = [EventAnalytics.buld_analytic_dict(analytic) for analytic in events_analytics]
        return jsonify(Events=events_analytics_dict)

class EventView(eid):
    def get(eid): 
        event_analytic = db.session.query(EventAnalytics).filter(EventAnalytics.eid == eid).first()
        event_analytic.views += 1
        db.session.commit()

        return jsonify(msg='success'), 200


api.add_resource(NewEvents, '/events/analytics')
api.add_resource(EventView, '/events/<int:eid>/view')
