from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db
from sqlalchemy import create_engine
from credentials import db_string
import json
app = Flask(__name__)
CORS(app)
db = create_engine(db_string)


@app.route('/')
def hello():
    return 'Hello world'


@app.route('/oblast')
def oblast():
    answer = db.execute('SELECT oblast_id, oblast_ru FROM topo.oblast')
    return json.dumps({'result': [dict(row) for row in answer]}, ensure_ascii=False)

@app.route('/leshoz')
def leshoz():
    answer = db.execute("SELECT l.leshoz_id, CONCAT(lt.leshoztype_ru, ' ', l.leshoz_ru, ' (', l.leshoz_id, ')') AS leshoz FROM forest.leshoz l LEFT JOIN forest.leshoztype lt ON lt.leshoztype_id = l.leshoztype_id ORDER BY leshoz")
    return json.dumps({'result': [dict(row) for row in answer]}, ensure_ascii=False)

@app.route('/forestry')
def forestry():
    answer = db.execute("SELECT f.gid, CONCAT (f.forestry_num, '. ', ft.forestrytype_ru, ' ', f.forestry_ru) AS forestry FROM forest.forestry f LEFT JOIN forest.forestrytype ft ON ft.forestrytype_id = f.forestrytype_id ORDER BY forestry")
    return json.dumps({'result': [dict(row) for row in answer]}, ensure_ascii=False)

@app.route('/block')
def block():
    answer = db.execute('SELECT gid, block_num FROM forest.block')
    return json.dumps({'result': [dict(row) for row in answer]}, ensure_ascii=False, default=str)

@app.route('/purpose')
def purpose():
    answer = db.execute('SELECT purpose_id, purpose_ru FROM forest.purpose')
    return json.dumps({'result': [dict(row) for row in answer]}, ensure_ascii=False, default=str)

@app.route('/woodSpecies')
def woodSpecies():
    answer = db.execute('SELECT woodspecies_id, woodshortname FROM forest.woodspecies')
    return json.dumps({'result': [dict(row) for row in answer]}, ensure_ascii=False, default=str)

@app.route('/refineLeshoz/<id>')
def refineLeshoz(id):
    answer = db.execute("SELECT l.leshoz_id, CONCAT(lt.leshoztype_ru, ' ', l.leshoz_ru, ' (', l.leshoz_id, ')') AS leshoz FROM forest.leshoz l LEFT JOIN forest.leshoztype lt ON lt.leshoztype_id = l.leshoztype_id WHERE oblast_id = {} ORDER BY leshoz".format(int(id)))
    return json.dumps({'result': [dict(row) for row in answer]}, ensure_ascii=False)

@app.route('/refineForestry/<id>')
def refineForestry(id):
    answer = db.execute("SELECT f.gid, CONCAT (f.forestry_num, '. ', ft.forestrytype_ru, ' ', f.forestry_ru) AS forestry FROM forest.forestry f LEFT JOIN forest.forestrytype ft ON ft.forestrytype_id = f.forestrytype_id WHERE leshoz_id = {} ORDER BY forestry ".format(int(id)))
    return json.dumps({'result': [dict(row) for row in answer]}, ensure_ascii=False)

@app.route('/refineBlock/<id>')
def refineBlock(id):
    answer = db.execute('SELECT gid, block_num FROM forest.block WHERE forestry_id = {} ORDER BY block_num ASC'.format(int(id)))
    return json.dumps({'result': [dict(row) for row in answer]}, ensure_ascii=False, default=str)

@app.route('/getData/<int:blockId>/<int:cycle>')
def getData(blockId, cycle):
    answer = db.execute('SELECT stand_code FROM forest.stand WHERE block_id = {} ORDER BY block_num ASC'.format(int(blockId)))
    d, standCodes = {}, []
    preStandEstimations, standEstimations, standEstimationIds = {}, [], []
    for part in answer:
        for column, value in part.items():
            d = {**d, **{column: value}}
        standCodes.append(d)
    # for stand in standCodes:
    #     print(stand['stand_code'])
    for stand in standCodes:
        # print(stand)
        estimation = db.execute('SELECT * FROM forest.tax WHERE stand_code = {} AND cycle = {} ORDER BY stand_num'.format(stand['stand_code'], cycle))
        for part in estimation:
            for column, value in part.items():
                preStandEstimations = {**preStandEstimations, **{column: value}}
                # print(preStandEstimations.get('standestimation_id'))
                # print(preStandEstimations.items())
            standEstimations.append(preStandEstimations)
            standEstimationIds.append(preStandEstimations.get('standestimation_id'))
            # print(standEstimations[1])
    # print(standEstimationIds)
    
    # print(json.dumps({ 'result': [dict(row) for row in standEstimations] }, ensure_ascii=False, default=str))


    # return json.dumps({'result': [dict(row) for row in answer]}, ensure_ascii=False, default=str)
    return json.dumps({ 'result': [dict(row) for row in standEstimations] }, ensure_ascii=False, default=str)

@app.route('/getForestUse/<int:blockId>/<int:cycle>')
def getForestUse(blockId, cycle):
    answer = db.execute('SELECT stand_code FROM forest.stand WHERE block_id = {} ORDER BY block_num ASC'.format(int(blockId)))
    d, standCodes = {}, []
    preStandEstimations, standEstimations, standEstimationIds = {}, [], []
    for part in answer:
        for column, value in part.items():
            d = {**d, **{column: value}}
        standCodes.append(d)
    for stand in standCodes:
        estimation = db.execute('SELECT * FROM forest.tax WHERE stand_code = {} AND cycle = {} ORDER BY stand_num'.format(stand['stand_code'], cycle))
        for part in estimation:
            for column, value in part.items():
                preStandEstimations = {**preStandEstimations, **{column: value}}
            standEstimations.append(preStandEstimations)
            standEstimationIds.append(preStandEstimations.get('standestimation_id'))
    standForestUseResult = []
    for id in standEstimationIds:
        c, preStandForestUseResult = {}, []
        standForestUse = db.execute('SELECT standforestuse_id, standestimation_id, forestusetype_id, plan_fact from forest.standforestuse WHERE standestimation_id = {}'.format(id))
        for part in standForestUse:
            for column, value in part.items():
                c = {**c, **{column: value}}
            preStandForestUseResult.append(c)
        standForestUseResult.append(preStandForestUseResult)
    return(json.dumps(standForestUseResult, ensure_ascii=False, default=str))

@app.route('/getForestComposition/<int:blockId>/<int:cycle>')
def getForestComposition(blockId, cycle):
    answer = db.execute('SELECT stand_code FROM forest.stand WHERE block_id = {} ORDER BY block_num ASC'.format(int(blockId)))
    d, standCodes = {}, []
    preStandEstimations, standEstimations, standEstimationIds = {}, [], []
    for part in answer:
        for column, value in part.items():
            d = {**d, **{column: value}}
        standCodes.append(d)
    for stand in standCodes:
        estimation = db.execute('SELECT * FROM forest.tax WHERE stand_code = {} AND cycle = {} ORDER BY stand_num'.format(stand['stand_code'], cycle))
        for part in estimation:
            for column, value in part.items():
                preStandEstimations = {**preStandEstimations, **{column: value}}
            standEstimations.append(preStandEstimations)
            standEstimationIds.append(preStandEstimations.get('standestimation_id'))
    standForestComposeResult = []
    for id in standEstimationIds:
        c, preStandForestComposeResult = {}, []
        standForestCompose = db.execute('SELECT woodspecies_id, standestimation_id, species_percent, plan_fact from forest.forestcomposition WHERE standestimation_id = {}'.format(id))
        for part in standForestCompose:
            for column, value in part.items():
                c = {**c, **{column: value}}
            preStandForestComposeResult.append(c)
        standForestComposeResult.append(preStandForestComposeResult)
    return(json.dumps(standForestComposeResult, ensure_ascii=False, default=str))

@app.route('/getActions/<int:blockId>/<int:cycle>')
def getActions(blockId, cycle):
    answer = db.execute('SELECT stand_code FROM forest.stand WHERE block_id = {} ORDER BY block_num ASC'.format(int(blockId)))
    d, standCodes = {}, []
    preStandEstimations, standEstimations, standEstimationIds = {}, [], []
    for part in answer:
        for column, value in part.items():
            d = {**d, **{column: value}}
        standCodes.append(d)
    for stand in standCodes:
        estimation = db.execute('SELECT * FROM forest.tax WHERE stand_code = {} AND cycle = {} ORDER BY stand_num'.format(stand['stand_code'], cycle))
        for part in estimation:
            for column, value in part.items():
                preStandEstimations = {**preStandEstimations, **{column: value}}
            standEstimations.append(preStandEstimations)
            standEstimationIds.append(preStandEstimations.get('standestimation_id'))
    actionsResult = []
    for id in standEstimationIds:
        c, preActionsResult = {}, []
        action = db.execute('SELECT action_id, standestimation_id, actiontype_id, actionurgency_id from forest.action WHERE standestimation_id = {}'.format(id))
        for part in action:
            for column, value in part.items():
                c = {**c, **{column: value}}
            preActionsResult.append(c)
        actionsResult.append(preActionsResult)
    print(standEstimationIds)    
    return(json.dumps(actionsResult, ensure_ascii=False, default=str))

@app.route('/getTillage')
def getTillage():
    answer = db.execute("SELECT actiontype_id FROM forest.actiontype WHERE f_type = 'f31'")
    return json.dumps({'result': [dict(row) for row in answer]}, ensure_ascii=False, default=str)

@app.route('/getCreationType')
def getCreationType():
    answer = db.execute("SELECT actiontype_id FROM forest.actiontype WHERE f_type = 'f32'")
    return json.dumps({'result': [dict(row) for row in answer]}, ensure_ascii=False, default=str)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')