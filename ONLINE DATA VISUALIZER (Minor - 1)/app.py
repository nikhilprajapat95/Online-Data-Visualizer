from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def start():
    return render_template('start.html')

@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'csv_file' not in request.files:
        return "No file part", 400

    file = request.files['csv_file']
    if file.filename == '':
        return "No selected file", 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return redirect(url_for('visualize', filename=filename))

@app.route('/visualize/<filename>', methods=['GET', 'POST'])
def visualize(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    data = pd.read_csv(filepath)
    chart_type = request.form.get('chart_type', 'line')

    if request.method == 'POST':
        plt.figure(figsize=(10, 6))
        sns.set(style="whitegrid")

        if chart_type == 'line':
            for column in data.select_dtypes(include=['number']).columns:
                sns.lineplot(data=data, x=data.index, y=column, label=column)
        elif chart_type == 'bar':
            data.sum().plot(kind='bar', color=sns.color_palette('husl', len(data.columns)))
        elif chart_type == 'histogram':
            for column in data.select_dtypes(include=['number']).columns:
                sns.histplot(data[column], kde=False, bins=20)

        # Save the chart in the static folder
        chart_path = os.path.join('static', f'chart_{chart_type}.png')
        plt.savefig(chart_path)
        plt.close()

        # Update to use static file path in render_template
        return render_template('visualize.html', filename=filename, chart_path=f'/{chart_path}', columns=data.columns, chart_type=chart_type)

    return render_template('visualize.html', filename=filename, columns=data.columns)

if __name__ == '__main__':
    app.run(debug=True)