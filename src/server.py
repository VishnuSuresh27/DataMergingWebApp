from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import pandas as pd
from io import BytesIO

app = Flask(__name__)
CORS(app)

@app.route('/merge', methods=['POST'])
def merge_files():
    try:
        row2df = {}
        files = request.files.getlist('files')
        
        for file in files:
            extension = file.filename.split('.')[-1]
            if extension in ['csv']:
                df = pd.read_csv(file)
            elif extension in ['xls', 'xlsx']:
                df = pd.read_excel(file)
            else:
                continue
            row2df[df.shape[0]] = df

        row2df = {k: row2df[k] for k in sorted(row2df)}
        values_list = list(row2df.values())
        sensor = values_list[0]
        sensorhf = values_list[1]
        percentref = pd.read_csv('Percent_reference.csv')

        sensor_merged = pd.merge(sensor, sensorhf, on='timestamp', how='outer').sort_values(by='timestamp')
        sensor_merged['Percent'] = pd.to_numeric(sensor_merged['Percent'], errors='coerce').fillna(999)
        percentref = percentref.sort_values(['Percent Min', 'Percent Max'])

        def find_matching_rows(row):
            matching_rows = percentref[
                (percentref['Percent Min'] <= row['Percent']) & 
                (percentref['Percent Max'] >= row['Percent'])
            ]
            return matching_rows.iloc[0] if not matching_rows.empty else pd.Series([None]*len(percentref.columns), index=percentref.columns)

        matched_rows = sensor_merged.apply(find_matching_rows, axis=1)
        sensor_merged_extended = pd.concat([sensor_merged, matched_rows], axis=1)
        sensor_merged_extended = sensor_merged_extended[['Period Code', 'Cycle ID', 'timestamp', 'Good/Bad', 'B_2', 'B_3', 'B_4', 'B_5', 'B_9', 'B_10', 'B_14', 'B_15', 'B_16', 'B_17', 'B_18', 'B_19', 'B_20', 'B_21', 'B_22', 'B_23', 'B_24',	'B_25', 'B_6', 'B_7', 'B_8','B_11',	'B_12'	,'B_13'	,'Percent',	'Percent Min', 'Percent Max', 'Rotation_SPEED_SETUP', 'rolling_SETUP', 'Coolant_SETUP',	'Airflow_SETUP', 'UW_SETUP', 'RW_SETUP']]
        # To return a file response
        output = BytesIO()
        sensor_merged_extended.to_csv(output, index=False)
        output.seek(0)
        
        response = make_response(send_file(output, mimetype='text/csv'))
        response.headers["Content-Disposition"] = "attachment; filename=sensor_merged.csv"
        return response

    except Exception as e:
       print("Error during merging:", e)
       return jsonify({"error": "Error merging files"}), 500

if __name__ == '__main__':
    app.run(debug=True)
