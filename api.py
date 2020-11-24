from flask import Flask, jsonify, abort, make_response, request

# TESTING PLAYING ABOUT WITH FLASK AND RESTFUL API
app = Flask(__name__)

licenses = [{'id': 1,'key':'asbd918b2819basd89'}, {'id': 2,'key':'iniboniogb123bobo'}]

def genlicensesession():

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/api/v1/licenses', methods=['GET'])
def get_licenses():
    return jsonify({'licenses':licenses})

@app.route('/api/v1/licenses/<int:licenseid>', methods=['GET'])
def get_specific_license(licenseid):
    license = [license for license in licenses if license['id'] == licenseid]
    if len(license) == 0:
        abort(404)
    return jsonify({'license':license[0]})

@app.route('/api/v1/licenses', methods=['POST'])
def create_license():
    if not request.json or not 'key' in request.json:
        abort(400)
    license = {'id': licenses[-1]['id'] + 1,'key':request.json['key'] }
    licenses.append(license)
    print(licenses)
    return jsonify({'license': license}), 201

@app.route('/api/v1/licenses<int:licenseid>', methods=['DELETE'])
def delete_task(licenseid):
    license = [license for license in licenses if license['id'] == licenseid]
    if len(license) == 0:
        abort(404)
    licenses.remove(license[0])
    return jsonify({'result': True})

if __name__ == '__main__':
    app.run(debug=True)
