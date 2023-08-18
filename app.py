from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.secret_key = 'sdjh548SD544fsJKHdksa21354JHKj'

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


if __name__ == '__main__':
    app.run(debug=True)