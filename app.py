from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

app = Flask(__name__)
app.secret_key = 'sdjh548SD544fsJKHdksa21354JHKj'
app.config['UPLOAD_FOLDER'] = "Resumes"

SCOPE = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
CREDENTIALS_PATH = 'onepay-371014-b3ac6b7487f3.json'
SPREADSHEET_ID = '1CJBruM7RlvXdW5VR42PBsPB8FqYVZklvdCjGVtFdYJw'
RANGE_NAME = 'Sheet1'

# Flask routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        candidateName = request.form.get('candidateName')
        jobType = request.form.get('jobType')
        technologySkills = request.form.get('technologySkills')
        totalExperience = request.form.get('totalExperience')
        relevantExperience = request.form.get('relevantExperience')
        currentCTC = request.form.get('currentCTC')
        expectedCTC = request.form.get('expectedCTC')
        currentLocation = request.form.get('currentLocation')
        preferredLocation = request.form.get('preferredLocation')
        organizationName = request.form.get('organizationName')
        officialNoticePeriod = request.form.get('officialNoticePeriod')
        servingNoticePeriod = request.form.get('servingNoticePeriod')
        phoneNumber = request.form.get('phoneNumber')
        email = request.form.get('email')
        date = request.form.get('date')
        submittedBy = request.form.get('submittedBy')

        if has_duplicate(phoneNumber, email):
            flash('User already exists with the given mobile number or email.', 'danger')
        else:
            try:
                credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, SCOPE)
                client = gspread.authorize(credentials)
                sheet = client.open_by_key(SPREADSHEET_ID).worksheet(RANGE_NAME)

                new_row = [candidateName,jobType,technologySkills,totalExperience,relevantExperience,currentCTC,expectedCTC,currentLocation,
                        preferredLocation,organizationName,officialNoticePeriod,servingNoticePeriod,phoneNumber,email,date,submittedBy]
                sheet.append_row(new_row)
                flash('Successfully added candidate details.', 'success')
            except Exception as e:
                flash('An error occurred while adding data.', 'danger')
        return redirect(url_for('index'))
    
    return render_template('index.html')

def has_duplicate(phone_number=None, email=None):
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, SCOPE)
        client = gspread.authorize(credentials)
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(RANGE_NAME)
        data = sheet.get_all_values()

        for row in data:
            if phone_number and row[12] == phone_number:
                return True
            if email and row[13] == email:
                return True
            # if row[12] == phone_number or row[13] == email:
            #     return True

        return False
    except Exception as e:
        return False
    
@app.route('/check/', methods=['GET'])
def check():
    phone_number = request.args.get('phoneNumber')
    email = request.args.get('email')
    isExist = False
    if phone_number:
        isExist = has_duplicate(phone_number=phone_number)
    if email:
        isExist = has_duplicate(email=email)
    return jsonify({"exists": isExist})


@app.route('/job', methods=['GET', 'POST'])
def job():
    if request.method == 'POST':
        candidateName = request.form.get('candidateName')
        phoneNumber = request.form.get('phoneNumber')
        email = request.form.get('email')
        currentLocation = request.form.get('currentLocation')
        technologySkills = request.form.get('technologySkills', '-')
        education = request.form.get('education')
        passedYear = request.form.get('passedYear')

        try:
          credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, SCOPE)
          client = gspread.authorize(credentials)
          sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Sheet2")

          new_row = [candidateName,phoneNumber,email, currentLocation, technologySkills,education,passedYear]
          sheet.append_row(new_row)
        except Exception as e:
          flash('An error occurred while submitting your data.', 'danger')

        if 'resume' in request.files:
            resume_file = request.files['resume']
            if resume_file.filename != '':
                passedYear_folder = os.path.join(app.config['UPLOAD_FOLDER'], passedYear)
                if not os.path.exists(passedYear_folder):
                    os.makedirs(passedYear_folder)

                resume_filename = os.path.join(passedYear_folder, resume_file.filename)
                resume_file.save(resume_filename)
        flash('Successfully submitted your details.', 'success')
        return redirect(url_for('job'))

    return render_template("job.html")


if __name__ == '__main__':
    app.run(debug=True)
