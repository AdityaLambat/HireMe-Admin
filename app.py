########## Imports ##########

from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from flask_mail import *
from random import *
from bson import ObjectId
from base64 import b64encode, b64decode
import pymongo
from datetime import datetime
import random

########## Getting Current Date ##########

current_date_time = datetime.now()

########## Flask App Configuration ##########

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


########## Database Connection ##########
client = pymongo.MongoClient('mongodb://localhost:27017/HireMe')
database = client['HireMe']
collectionAdmin = database['admin']  # admin
collectionJobs = database['jobs']  # jobs
collectionApl = database['applications']  # applications
collectionUsers = database['users']  # users
collectionResume = database['resumes']  # resumes

if not client.is_mongos:
    print("Connection To MongoDB : Successful")
else:
    print("Connection To MongoDB : Failed")


########## Mail Verification ##########
mail = Mail(app)
app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = 'mc222437@zealeducation.com'
app.config['MAIL_PASSWORD'] = 'Ad1301@anjajylmbt'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


def otpCode():
    return randint(000000, 999999)

########## TextArea Splitter Function ##########


def textAreaSplit(text):
    splitText = text.split('/')
    return splitText

########## Job ID Generator Function ##########


def jobID():
    return random.randint(100000, 999999)


########## Routing To Templates ##########

########## Login ##########

@app.route('/', methods=['GET', 'POST'])
def login():
    if session.get('user'):
        return redirect('/index')
    msg = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        query = collectionAdmin.find_one(
            {'email': email, 'password': password})	

        if query:
            session['user'] = email
            return redirect('/index')
        else:
            msg = "loginError"
    return render_template('login.html', msg=msg)

########## Forgot Password ##########


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgotPassword():
    if session.get('user'):
        return redirect('/index')
    msg = ""
    email = ""
    if request.method == 'POST':
        email = request.form['email']
        query = collectionAdmin.find_one({'email': email})
        if query:
            otp = str(otpCode())
            mailMsg = Message('HireMe Admin Email Verification ',
                              sender='mc222437@zealeducation.com', recipients=[email])
            mailMsg.body = "Verify your email with this OTP " + otp
            mail.send(mailMsg)
            return render_template('email_verification.html', otp=otp, email=email)
        else:
            msg = "fgterror"
    return render_template('forgot_password.html', msg=msg)


########## Email Verification ##########

@app.route('/forgot_password/email_verification', methods=['GET', 'POST'])
def emailVerificationFGT():
    if session.get('user'):
        return redirect('/index')
    msg = ""
    if request.method == 'POST':
        func = request.form['func']
        if func == "verify":
            otp = request.form['mailotp']
            sysOtp = request.form['sysOtp']
            email = request.form['email']
            if otp == sysOtp:
                msg = "verified"
                return render_template('email_verification.html', msg=msg, email=email)
            else:
                msg = "otperror"
                return render_template('email_verification.html', msg=msg, email=email)
        elif func == "resend":
            otp = str(otpCode())
            email = request.form['resendemail']
            mailMsg = Message('HireMe Admin Email Verification ',
                              sender='mc222437@zealeducation.com', recipients=[email])
            mailMsg.body = "Verify your email with this OTP " + otp
            mail.send(mailMsg)
            msg = "resendotp"
            return render_template('email_verification.html', otp=otp, email=email, msg=msg)


########## Reset Password ##########
@app.route('/reset_password', methods=['GET', 'POST'])
def resetPassword():
    if session.get('user'):
        return redirect('/index')
    msg = ""
    return render_template('reset_password.html')


########## Index ##########

@app.route('/index')
def index():
    if not session.get('user'):
        return redirect('/')
    email = session['user']
    msg = ""
    name = ""
    query = collectionAdmin.find_one(
        {'email': email})
    name = query['fname'] + " " + query['lname']
    return render_template('index.html', name=name)

########## Users ##########


@app.route('/users')
def users():
    if not session.get('user'):
        return redirect('/')
    msg = ""
    users = ""
    query = collectionUsers.find()
    if query:
        users = query
    else:
        msg = "nousers"
    return render_template('users.html', users=users, msg=msg)


########## Applications ##########

@app.route('/applications')
def applications():
    if not session.get('user'):
        return redirect('/')
    apl = ""
    msg = ""
    query = collectionApl.find()
    if query:
        apl = query
    else:
        msg = "notdata"
    return render_template('applications.html', apl=apl, msg=msg)

########## Application Details ##########


@app.route('/application/details', methods=['GET', 'POST'])
def applicationDetails():
    if not session.get('user'):
        return redirect('/')
    msg = ""
    if request.method == 'POST':
        if  request.form['func'] == 'update':
            status = request.form['status']
            aplid = request.form['aplid']
            query = {"aplid": aplid}
            update = {"$set": {"aplstatus": status}}
            result = collectionApl.update_one(query, update)
            if result.modified_count:
                msg = "updated"
            else:
                msg = "error"
        aplid = request.form['aplid']
        jid = request.form['jid']
        email = request.form['email']
        userDetails = collectionUsers.find_one({'email': email})
        aplDetails = collectionApl.find_one({'aplid': aplid})
        jobDetails = collectionJobs.find_one({'jid': jid})
        role = jobDetails['jrole']
        qualif = jobDetails['jqualif']
        skill = jobDetails['jskills'].split(",")
    return render_template('application_details.html', aplDetails=aplDetails, jobDetails=jobDetails, userDetails=userDetails, current_date_time=current_date_time, role=role, qualif=qualif, skill=skill, msg=msg)


########## Application Update Status ##########
@app.route('/update/status', methods=['GET', 'POST'])
def updateStatus():
    if not session.get('user'):
        return redirect('/')
    status = request.form['status']
    aplid = request.form['aplid']
    msg = ""
    if request.method == 'POST':
        query = {"aplid": aplid}
        update = {"$set": {"aplstatus": status}}
        result = collectionApl.update_one(query, update)
        if result:
            return render_template('application_details.html')

########## Job Details ##########


@app.route('/job/details', methods=['GET', 'POST'])
def jobDetails():
    if not session.get('user'):
        return redirect('/')
    jid = request.form['jid']
    jobDetails = collectionJobs.find_one({'jid': jid})
    role = jobDetails['jrole'] 
    qualif = jobDetails['jqualif']
    skill = jobDetails['jskills'].split(",")
    return render_template('job_details.html', jobDetails=jobDetails, current_date_time=current_date_time, role=role, qualif=qualif, skill=skill)

########## View Resume ##########


@app.route('/application/details/resume', methods=['GET', 'POST'])
def resume():
    if not session.get('user'):
        return redirect('/')
    rid = request.form['resume']
    object_id = ObjectId(rid)
    resume = collectionResume.find_one({'_id': object_id})
    encoded_content = b64encode(resume['content']).decode('utf-8')
    return render_template('view_resume.html', resume=resume, encoded_content=encoded_content)


########## Post Jobs ##########


@app.route('/post_jobs', methods=['GET', 'POST'])
def postJobs():
    if not session.get('user'):
        return redirect('/')
    msg = ""
    if request.method == 'POST':
        jtitle = request.form['jtitle']
        jtype = request.form['jtype']
        jd = request.form['jd']
        jstate = request.form['state']
        jdistrict = request.form['district']
        jctg = request.form['jctg']
        jshift = request.form['jshift']

        jrole = request.form['jrole']
        jqualif = request.form['jqualif']
        jskills = request.form['jskills']
        jsal = request.form['jsal']

        jdead = datetime.strptime(request.form['jdead'], "%Y-%m-%d")
        cname = request.form['cname']
        cemail = request.form['cemail']
        cweb = request.form['cweb']

        jidOri = "JID" + str(jobID())
        jid = ""
        findQuery = collectionJobs.find_one({'jid': jid})
        if findQuery is not None:
            jidCopy = "JID" + str(jobID())
            while jidCopy == jidOri:
                jidCopy = "JID" + str(jobID())
            jid = jidCopy
        else:
            jid = jidOri

        insertQuery = {
            'jid': jid,
            'jtitle': jtitle,
            'jtype': jtype,
            'jd': jd,
            'jstate': jstate,
            'jdistrict': jdistrict,
            'jctg': jctg,
            'jshift': jshift,
            'jrole': jrole,
            'jqualif': jqualif,
            'jskills': jskills,
            'jsal': jsal,
            'jdead': jdead,
            'cname': cname,
            'cemail': cemail,
            'cweb': cweb,
            'jpost': current_date_time
        }

        insertOne = collectionJobs.insert_one(insertQuery)
        if insertOne.acknowledged:
            msg = "inserted"
        else:
            msg = "inserterror"

    return render_template('post_jobs.html', msg=msg)


########## View Jobs ##########
@app.route('/view_jobs', methods=['GET', 'POST'])
def viewJobs():
    if not session.get('user'):
        return redirect('/')
    jobs = ""
    msg = ""
    query = collectionJobs.find()
    if query:
        jobs = query
    else:
        msg = "notdata"
    return render_template('view_jobs.html', jobs=jobs, msg=msg, current_date_time=current_date_time)

########## Application Reports ##########


@app.route('/reports/application', methods=['GET', 'POST'])
def reportApplication():
    if not session.get('user'):
        return redirect('/')
    msg = ""
    if request.method == 'POST':
        status = request.form['filter']
        fromDate = datetime.strptime(request.form['from'], "%Y-%m-%d")
        toDate = datetime.strptime(request.form['to'], "%Y-%m-%d")

        query = {
            'aplstatus': status,
            'apldate': {
                '$gte': fromDate,
                '$lte': toDate
            }
        }
        result = collectionApl.find(query)
        if result:
            msg = "found"
            return render_template('report_application.html', result=result, msg=msg, fromDate=fromDate, toDate=toDate, status=status)
    msg = "error"
    return render_template('report_application.html', msg=msg)

########## Job Reports ##########


@app.route('/reports/job', methods=['GET', 'POST'])
def reportJob():
    if not session.get('user'):
        return redirect('/')
    msg = ""
    if request.method == 'POST':
        status = request.form['filter']
        fromDate = datetime.strptime(request.form['from'], "%Y-%m-%d")
        toDate = datetime.strptime(request.form['to'], "%Y-%m-%d")
        query = ""
        s = ""
        if status == 'Active':
            query = {
                '$and': [
                    {'jpost': {'$lt': current_date_time}},
                    {'jpost': {'$gte': fromDate, '$lte': toDate}}
                ]
            }
            s = "Active"
        elif status == 'Expired':
            query = {
                '$and': [
                    {'jpost': {'$gt': current_date_time}},
                    {'jpost': {'$gte': fromDate, '$lte': toDate}}
                ]
            }
            s = "Expired"
        result = collectionJobs.find(query)
        if result:
            msg = "found"
            return render_template('report_job.html', result=result, msg=msg, fromDate=fromDate, toDate=toDate, status=status)
    msg = "error"
    return render_template('report_job.html', msg=msg)

########## LogOut ##########


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user', None)
    return render_template('login.html')

########## Privacy Policy ##########

@app.route('/privacy_policy')
def privacyPolicy():
    if not session.get('user'):
        return redirect('/')
    return render_template('policy.html')
########## App Run ##########


if __name__ == '__main__':
    app.run(debug=True, port=3001)
