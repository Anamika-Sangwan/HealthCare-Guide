from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

notes = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_note', methods=['POST'])
@app.route('/save_note', methods=['POST'])
def save_note():
    data = request.get_json()
    note = data['note']
    with open('notes.txt', 'a') as f:
        f.write(note + '\n---\n')  # separates notes with dashes
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(debug=True)
