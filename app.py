from flask import Flask, render_template, request, send_file
import pandas as pd
import io
import tempfile
import re

app = Flask(__name__)
app.config['MIMETYPE_MAP'] = {}

date_regex = re.compile(r'\d{2}-\d{2}-\d{2}')


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

    with open(temp_path.name) as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines if l.strip()]


    current_row = {}

    for line in lines:

        if date_regex.search(line):

            # Append current row
            if current_row:
                data.append(current_row)

            # Reset row
            current_row = {}

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
            net_regex = r'NET:\s*([+-]?\d*)x'

            match = re.search(net_regex, line)
            if match:
                mytotal = match.group(1)
                current_row['Total'] =mytotal

    # Append the last row
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
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%y')
    df['Date'] = df['Date'].dt.strftime('%m-%d-%y')

    print("Rows 5 thorugh 15")
    print(df.iloc[5:15])

    output = io.BytesIO()

    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    df.to_excel(writer, index=False)



    writer.close()

    output.seek(0)

    return send_file(output, download_name='report.xlsx',
                     mimetype='application/xls')


if __name__ == '__main__':
    app.run(debug=True)