from flask import Flask, render_template, request, send_file, flash
import pandas as pd
import io
import os
import secrets
import tempfile
import re
import javascript

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe()
app.config['MIMETYPE_MAP'] = {}

date_regex = re.compile(r'\d{2,4}[-/]\d{1,2}[-/]\d{1,2}')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    # Save uploaded file
    temp_path = tempfile.NamedTemporaryFile(delete=False)
    file.save(temp_path.name)

    data = []

    recordfailed= False
    failedrecords = ""


    with open(temp_path.name) as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines if l.strip()]

    counter = -1

    current_row = {
        'Date': None,
        'Time': None,
        'Flow': None,
        'Total': None
    }



    for line in lines:
        counter=counter+1


        try:
            if date_regex.search(line):

                # Append current row
                if current_row and line:
                    recordfailed = False
                    data.append(current_row)
                    current_row = {
                        'Date': None,
                        'Time': None,
                        'Flow': None,
                        'Total': None
                    }


                # Set new date/time
                date, time = line.split()
                current_row['Date'] = date
                current_row['Time'] = time

            elif line.startswith('FLOW'):
                # Add to current row
                flow = line.split(':')[1].rstrip(' g/m')
                current_row['Flow'] = flow

            elif line.startswith('NET'):
                # Add to current row
                net_regex = r'NET:\s*([+-]?\d*)x(\d*)Gal'

                match = re.search(net_regex, line)
                if match:
                    mytotal = match.group(1)
                    print("original:  " + line)
                    mytotal = float(match.group(2)) / 1000 * float(match.group(1))
                    print("final:  " + str(mytotal))
                    current_row['Total'] =mytotal
            #if(counter<20):
                #print("counter is : " + str(counter))
                #print(current_row)
        except Exception as ex:
            recordfailed = True
            failedrecords = failedrecords + "\n\n\nCounter: " + str(counter) + "\nException:  " + str(ex) + "\nRecord Failed:  " + line

    # Append the last row
    if current_row and line:
        data.append(current_row)




    df = pd.DataFrame(data)

    df.columns = [
        'Date',
        'Time',

        'Flow (g/m)',

        'Total (x 1000 Gal)'
    ]

    df['Flow (g/m)'] = pd.to_numeric(df['Flow (g/m)'])
    df['Total (x 1000 Gal)'] = pd.to_numeric(df['Total (x 1000 Gal)'])
    df['Date'] = pd.to_datetime(df['Date'], format='%y-%m-%d')
    df['Date'] = df['Date'].dt.strftime('%m-%d-%y')

    print("Rows 5 thorugh 15")
    print(df.iloc[0:15])

    output = io.BytesIO()

    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    df.to_excel(writer, index=False)

    workbook = writer.book
    worksheet = workbook.add_worksheet("Failed Records")

    # Write failed records to sheet
    row = 0
    for record in failedrecords.split("\n\n"):
        worksheet.write(row, 0, record)
        row += 1


    writer.close()

    output.seek(0)

    return send_file(output, download_name=file.filename + '_decoded.xlsx',
                     mimetype='application/xls')


if __name__ == '__main__':
    app.run(debug=True)