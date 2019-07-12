
from downloader.functions import create_new_user, reset_user_password, NotFoundError, NotProcessedError, AlreadyExistsError, create_download_file, retrieve_iframes, update_application, create_registration_record
from flask_login import current_user, login_user, login_required, logout_user
from downloader import app, db, bcrypt, logger
from flask import session, redirect, url_for, request
from flask import render_template, send_file
from downloader.models import User, RegApplication
from datetime import datetime
import traceback
import os


@app.route("/login", methods=['GET', 'POST'])
def login():

    try:
        if not current_user.is_authenticated:

            notification = session['notification'] if 'notification' in session else None
            session['notification'] = None

            if request.method == 'POST':

                if 'login-email' in request.form:

                    email = request.form['login-email']
                    pw = request.form['login-password']

                    user = User.query.filter_by(email=email).first()

                    if user:
                        if user.verified:
                            if not user.deactivated:
                                if bcrypt.check_password_hash(user.hashed_pw, pw):

                                    login_user(user)

                                    user.login_count = user.login_count + 1
                                    user.last_signin = datetime.now()
                                    db.session.commit()

                                    logger.debug(f'LOGIN - login completed successfully for email {email}.')

                                    return redirect(url_for(('main')))

                                else:
                                    logger.debug(f'LOGIN - login failed for user {email}, incorrect password.')
                                    session['notification'] = {'status': 'error', 'content': 'Sorry, that password was incorrect.'}
                                    return redirect(url_for('login'))
                            else:
                                logger.debug(f'LOGIN - login failed for email {email}, user deactivated.')
                                session['notification'] = {'status': 'error', 'content': 'Sorry, your user account has been deactivated, please register again to regain access.'}
                                return redirect(url_for('login'))
                        else:
                            logger.debug(f'LOGIN - login failed for email {email}, user not verified.')
                            session['notification'] = {'status': 'error', 'content': 'Sorry, your user account has not yet been verified, please check your email for your verification link.'}
                            return redirect(url_for('login'))
                    else:
                        logger.debug(f'LOGIN - login failed for email {email}, no account found.')
                        session['notification'] = {'status': 'error', 'content': 'Sorry, that email was not recognized.'}
                        return redirect(url_for('login'))


                elif 'password-reset' in request.form:

                    logger.debug(f"LOGIN - User with email {request.form['password-reset']} is resetting their password.")

                    try:
                        reset_user_password(request.form['password-reset'])

                    except NotFoundError:

                        session['notification'] = {'status': 'error', 'content': 'No account was found for the email you provided.'}
                        return redirect(url_for('login'))

                    logger.debug('LOGIN - Password reset complete.')

                    session['notification'] = {'status': 'success', 'content': 'A reset code has been sent to your email.'}
                    return redirect(url_for('verify'))

        else:
            return redirect(url_for('main'))

        return render_template('user/login.html', title='Login', notification=notification)


    except Exception:
        logger.error(f'LOGIN - ERROR OCCURRED: {str(traceback.format_exc())}')
        return 'Sorry, an error occurred. Please try again later.', 500



@app.route('/', methods=['GET', 'POST'])
@app.route('/main', methods=['GET', 'POST'])
@login_required
def main():

    try:
        logger.debug(f'MAIN - User {current_user.email} has visited main.')
        notification = session['notification'] if 'notification' in session else None
        session['notification'] = None

        return render_template('user/main.html', notification=notification)

    except Exception:
        logger.error(f'MAIN - Error occurred: {str(traceback.format_exc())}')
        session['notification'] = {'status': 'error', 'content': 'Sorry an error occurred. Please try again later.'}
        return redirect(url_for('login'))



@app.route('/downloader', methods=['GET', 'POST'])
@login_required
def downloader():

    try:
        logger.debug(f'MAIN - User {current_user.email} has visited downloader.')
        notification = session['notification'] if 'notification' in session else None
        session['notification'] = None

        if request.method == 'POST':

            try:
                file_location = create_download_file(request)
            except NotFoundError:
                session['notification'] = {'status': 'error', 'content': 'No records were found for the given entity between the dates specified..'}
                return redirect(url_for('downloader'))

            current_user.total_download_size_mb = current_user.total_download_size_mb + (os.path.getsize(file_location) / (1024 * 1024.0))
            current_user.num_downloads = current_user.num_downloads + 1
            db.session.commit()

            return send_file(file_location, as_attachment=True)

        return render_template('app/downloader.html', notification=notification)

    except Exception:
        logger.error(f'DOWNLOADER - {str(traceback.format_exc())}')
        session['notification'] = {'status': 'error', 'content': 'Sorry an error occurred. Please try again later.'}
        return redirect(url_for('main'))



@app.route('/analytics', methods=['GET'])
@login_required
def analytics():

    try:
        logger.debug(f'MAIN - User {current_user.email} has visited analytics.')
        notification = session['notification'] if 'notification' in session else None
        session['notification'] = None

        iframe_mapper = retrieve_iframes()

        return render_template('app/analytics.html', iframe_mapper=iframe_mapper, notification=notification)

    except Exception:
        logger.error(f'ANALYTICS - {str(traceback.format_exc())}')
        session['notification'] = {'status': 'error', 'content': 'Sorry an error occurred. Please try again later.'}
        return redirect(url_for('main'))



@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():

    try:
        logger.debug(f'MAIN - User {current_user.email} has visited admin.')

        if current_user.admin:

            notification = session['notification'] if 'notification' in session else None
            session['notification'] = None

            users = User.query.all()
            applications = RegApplication.query.filter(RegApplication.application_processed != True).all()

            if request.method == 'POST':

                if 'add-user' in request.form:

                    try:
                        create_new_user(request.form['add-user'])

                    except AlreadyExistsError:
                        session['notification'] = {'status': 'error', 'content': 'The user you are attempting to add already has an active account.'}
                        return redirect(url_for('admin'))

                    except NotProcessedError:
                        session['notification'] = {'status': 'error', 'content': 'An outstanding application exists for this user in the application section.'}
                        return redirect(url_for('admin'))

                    session['notification'] = {'status': 'success', 'content': 'User added successfully, a verification link has been sent to their email.'}
                    return redirect(url_for('admin'))

                elif 'deactivate-user' in request.form:

                    user = User.query.filter_by(id=request.form.get('deactivate-user')).first()
                    user.deactivated = True
                    user.deactivated_date = datetime.now()

                    db.session.commit()

                    session['notification'] = {'status': 'success', 'content': 'User deleted successfully.'}
                    return redirect(url_for('admin'))

                elif 'application-email' in request.form:

                    if request.form['application-action'] == 'approve':

                        update_application(request)
                        create_new_user(request.form['application-email'])

                    elif request.form['application-action'] == 'reject':

                        update_application(request)

                    session['notification'] = {'status': 'success', 'content': 'Action processed successfully, the user has been notified.'}
                    return redirect(url_for('admin'))

            return render_template('app/admin.html', users=users, applications=applications, notification=notification)

        else:
            session['notification'] = {'status': 'error', 'content': 'You do not have the necessary permissions to view this page.'}
            return redirect(url_for('main'))

    except Exception:
        logger.error(f'ADMIN - {str(traceback.format_exc())}')
        session['notification'] = {'status': 'error', 'content': 'Sorry an error occurred. Please try again later.'}
        return redirect(url_for('main'))



@app.route('/verify', methods=['GET', 'POST'])
def verify():

    try:

        notification = session['notification'] if 'notification' in session else None
        session['notification'] = None

        if request.method == 'POST':

            email = request.form['verify-email']
            code = request.form['verification-code']
            pword = bcrypt.generate_password_hash(request.form['new-password']).decode('utf-8')
            pword_conf = request.form['confirm-password']

            user = User.query.filter_by(email=email).first()

            if user:
                if not user.verified:
                    if user.verification_code == code:
                        if bcrypt.check_password_hash(pword, pword_conf):

                            user.verified = True
                            user.hashed_pw = pword

                            db.session.commit()

                            session['notification'] = {'status': 'success', 'content': 'Account verified successfully..'}
                            return redirect(url_for('login'))

                        else:
                            session['notification'] = {'status': 'error', 'content': 'Your passwords did not match.'}
                            return redirect(url_for('verify'))
                    else:
                        session['notification'] = {'status': 'error', 'content': 'Your verification code was incorrect.'}
                        return redirect(url_for('verify'))
                else:
                    session['notification'] = {'status': 'error', 'content': 'Your account has already been verified.'}
                    return redirect(url_for('main'))
            else:
                session['notification'] = {'status': 'error', 'content': 'No account was found with that email.'}
                return redirect(url_for('verify'))

        return render_template('user/verify.html', notification=notification)


    except Exception:
        logger.error(f'VERIFY - {str(traceback.format_exc())}')
        session['notification'] = {'status': 'error', 'content': 'Sorry an error occurred. Please try again later.'}
        return redirect(url_for('login'))



@app.route('/registration', methods=['GET', 'POST'])
def register_guide():

    if current_user.is_authenticated:

        if request.method == 'POST':

            if request.form.get('terms-checkbox') == 'on':

                session['register'] = True
                return redirect(url_for('register'))

            else:
                session['notification'] = {'status': 'error', 'content': 'You did not tick the agree to terms checkbox.'}
                return redirect(url_for('register'))
    else:
        return redirect(url_for('main'))

    return render_template('user/guidelines.html')



@app.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:

        if 'register' in session and session['register']:

            if request.method == 'POST':

                try:
                    create_registration_record(request)
                except AlreadyExistsError:
                    session['notification'] = {'status': 'error', 'content': 'An active user with your provided email already exists.'}
                    return redirect(url_for('login'))

                session['notification'] = {'status': 'success', 'content': 'Your application has been submitted. Please wait for approval from an OpenAPS admin, which you will be notified of via your provided email.'}
                return redirect(url_for('login'))

        else:
            return redirect(url_for('register_guide'))
    else:
        return redirect(url_for('main'))

    return render_template('user/register.html')


@app.route("/logout")
@login_required
def logout():

    try:
        if current_user.is_authenticated:

            logger.debug(f'LOGOUT - Logging out email {current_user.email}')

            logout_user()
            return redirect(url_for('login'))

    except Exception:
        logger.error(f'LOGOUT - {str(traceback.format_exc())}')
        session['notification'] = {'status': 'error', 'content': 'Sorry an error occurred. Please try again later.'}
        return redirect(url_for('login'))
