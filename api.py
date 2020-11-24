from flask import Flask, jsonify

# TESTING PLAYING ABOUT WITH FLASK AND RESTFUL API
app = Flask(__name__)

licenses = [{'id': 1}, {'id': 2}]


@app.route('/api/v1/licenses', methods=['GET'])
def get_licenses():
    return jsonify({'licenses':licenses})

@app.route('/api/v1/licenses/<int:licenseid>', method=['GET'])
def get_specific_license(licenseid):
    license = [license for license in licenses if license['id'] == licenseid]
    return jsonify({'license':license[0]})


if __name__ == '__main__':
    app.run(debug=True)
