from flask import Blueprint 
from main import api 

auth_api = Blueprint('auth_api', __name__) 

class Register():
    def post(): 
        new_user = Users.create_user(request.form)
        token = generate_confirmation_token(new_user.email)

        # TODO: URL SAVED IN VARIABLE
        confirm_url = 'https://wocpr.com/confirm/token/' + token
        html = render_template('confirmationEmail.html', confirm_url=confirm_url)
        subject = "What's On Campus - Confirm your email"
        send_email(new_user.email, subject, html)

        access_token = create_access_token(identity=request.form['email'], expires_delta=False)
        return jsonify(access_token=access_token, displayname=request.form['displayname']), 201
    
    #TODO: Maybe needs to be removed
    def get(): 
        return jsonify(response="Error has occured"), 500

class Login():
    def post(): 
        email = request.form['email']
        password = request.form['password']
        user = Users.get_user_by_email(email)
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            access_token = create_access_token(identity=email, expires_delta=False)
            ranks = [rank.rank for rank in user.rank]
            return jsonify(access_token=access_token, displayname=user.displayname, Rank=ranks), 201
        else:
            return jsonify(response="Invalid email or password"), 400

class ChangePassword():
    @jwt_required
    def post(): 
        currentPassword = request.form['currentPassword']
        newPassword = request.form['newPassword']
        confirmPassword = request.form['confirmPassword']

        username = get_jwt_identity()
        user = Users.get_user_by_email(username)

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

class ConfirmEmail():
    def get(token): 
        try:
            email = confirm_token(token)
        except:
            return jsonify(response="The confirmation link is invalid or has expired", success=False), 404

        user = db.session.query(Users).filter_by(email=email).first_or_404()
        if user.activated:
            return jsonify(response="Account already activated. Please login", success=False), 400
        else:
            user.activated = True
            db.session.commit()
            return jsonify(response='You have confirmed your account. Thanks!', success=True), 200

class ResetPassword():
    def post(token = None): 
        if token:
            try:
                email = confirm_token(token)
                new_password = request.form['newPassword']
                confirm_password = request.form['confirmPassword']

                user = db.session.query(Users).filter_by(email=email).first()

                if new_password == confirm_password:
                    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    user.password = hashed_password
                    db.session.commit()
                    return jsonify(success=True, response="Successfully changed password!"), 201
                else:
                    return jsonify(success=False, response="Confirm password doesn't match new password"), 400
            except:
                return jsonify(response="The reset link is invalid or has expired", success=False), 201


        else:
            email = request.form['email']
            user = db.session.query(Users).filter_by(email=email).first()

            if user:
                token = generate_confirmation_token(user.email)

                confirm_url = 'https://wocpr.com/resetpassword/' + token
                html = render_template('resetPasswordEmail.html', confirm_url=confirm_url)
                subject = "What's On Campus - Reset your password"
                send_email(user.email, subject, html)
                return jsonify(success=True, response="Reset password email sent!"), 201
            else:
                return jsonify(success=False, response="Email doesn't exists"), 400

        # Person inputs their email
        # A confirmation code is sent to email with random code for confirmation
        # If code hasn't expired.
        # Person inputs new password. Password gets updated
        return jsonify(msg="reset pass")

api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(ChangePassword, '/changepassword')
api.add_resource(ConfirmEmail, '/confirm/<token>')
api.add_resource(ResetPassword, '/resetpassword/')
api.add_resource(ResetPassword, '/resetpassword/<token>')

#TODO: DELETE THIS 
#class Register():
#    def post(): 
#        formDisplayname = request.form['displayname']
#        formEmail = request.form['email']
#        formFName = request.form['firstname']
#        formLName = request.form['lastname']
#        hashed_password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
#        newUser = Users(
#            displayname=formDisplayname,
#            email=formEmail,
#            password=hashed_password,
#            firstName=formFName,
#            lastName=formLName,
#            activated=0,
#            dateOfBirth=None,
#            dateCreated=datetime.utcnow()
#        )
#
#        # check if user exists
#        # TODO: THIS HAS TO BE HANDLED BY THE DBMS
#        checkUser = db.session.query(Users).filter(Users.email == formEmail).first()
#        checkEmail = db.session.query(Users).filter(Users.display_name == formDisplayname).first()
#        if checkUser or checkEmail: #            return jsonify(success=False, response="User already exists"), 409
#        else:
#            db.session.add(newUser)
#            db.session.commit()
#            login_user(newUser)
#            return jsonify(success=True, User=newUser.build_user_dict()), 201
#    def get():  
#        return jsonify(success=False, response="Error has occured"), 500
#
#class login():
#    email = request.form['email']
#    password = request.form['password']
#    user = db.session.query(Users).filter(Users.email == email).first()  # TODO: Change this to get
#    passw = bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8'))
#    if user and passw:
#        logged = login_user(user)
#        ranks = [rank.rank for rank in user.rank]
#        return jsonify(success=logged, User=user.build_user_dict(), Ranks=ranks), 201
#    else:
#        return jsonify(success=False, response="Wrong email or password"), 400
