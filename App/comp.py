# UPDATED FLASK:
from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)
file_path = "C:/Users/Philip/my_data/Shorty/_ShortyTables_/HTML Comp.json"

@app.route('/')
def index():
    with open(file_path, 'r') as file:
        data = json.load(file)
    return render_template('index.html', data=data)

@app.route('/update', methods=['POST'])
def update():
    # Logic to update the JSON file with new data
    return jsonify({'status': 'success'})

@app.route('/save', methods=['POST'])
def save():
    # Logic to save the current state to the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
    return jsonify({'message': 'File saved successfully'})

@app.route('/save-as', methods=['POST'])
def save_as():
    # Logic to save the current state to a new JSON file
    file_name = request.json.get('file_name', file_path)
    with open(file_path, 'r') as file:
        data = json.load(file)
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)
    return jsonify({'message': f'File saved as {file_name}'})

if __name__ == '__main__':
    app.run(debug=True)
    