from flask import Flask, Response, request
from flask.json import dumps
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import ModelSchema
from datetime import datetime
from requests import get
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.secret_key = 'example'
app.config.from_object("config")
db = SQLAlchemy()



class Stb(db.Model):

  id = db.Column(db.Integer, primary_key = True)
  epay = db.Column(db.Integer, index = True, nullable = False)
  mac = db.Column(db.String(255), index = True, nullable = False)
  key = db.Column(db.String(255), nullable = False)
  blocked = db.Column(db.Boolean, index = True, nullable = False)
  deleted = db.Column(db.Boolean, index = True, nullable = False)
  createTime = db.Column(db.DateTime, nullable = False)
  blockTime = db.Column(db.DateTime, nullable = False)
  unblockTime = db.Column(db.DateTime, nullable = False)
  updateTime = db.Column(db.DateTime, nullable = False)

  def __init__(self, epay, mac, key):
    self.epay = epay
    self.setMac(mac)
    self.key = key
    self.blocked = False
    self.deleted = False
    self.createTime = datetime.now()
    self.blockTime = datetime.now()
    self.unblockTime = datetime.now()
    self.updateTime = datetime.now()

  def getKey(self):
    return self.key

  def setEpay(self, epay):
    if epay < 0:
      raise RuntimeError("EPAY не валиден")
    self.epay = epay

  def setUpdateTime(self, time):
    self.updateTime = time

  def setMac(self, mac):
    self.mac = mac.strip().lower()

  def setKey(self, key):
    self.key = key.strip()

  def setDeletedStatus(self):
    self.deleted = True




class StbSchema(ModelSchema):
  class Meta:
    model = Stb






stbSchema = StbSchema()
stbsSchema = StbSchema(many = True)






@app.route("/stb/")
# /stb/?mac=udp://@225.1.1.22:1234&m=a8:f9:4b:29:0d:2f
# http://eltex.example.ru:4444/stb/?url=udp://@225.1.1.22:1234&m=a8:f9:4b:29:0a:ea
def getStbByMac():
  app.logger.info("Пришла приставка c ip %s" % request.remote_addr)
  if "m" in request.args:
    stb = Stb.query.filter_by(mac = request.args["m"], deleted = False).one_or_none()
    if stb:
      return app.config["KEY"]
  return ""



@app.route("/eltex.xspf")
def eltex():
  # GET /eltex.xspf?mac=A8%3AF9%3A4B%3A2B%3A2B%3AEB&serial=SB28008317&device=NV501
  # GET http://iptv.example.ru/eltex.xspf?type=m3u&mac=a8:f9:4b:29:0a:ea
  xrealip = request.headers.get("X-Real-IP", "default")
  ip = xrealip if xrealip != "default" else request.remote_addr
  app.logger.info("Пришла приставка c ip %s" % ip)
  typeFile = request.args.get("type", None)
  if "mac" in request.args:
    stb = Stb.query.filter_by(mac = request.args["mac"], deleted = False).one_or_none()
    if stb:
      if typeFile and typeFile == "m3u":
        url = "http://iptv.example.ru/update8231257/vermax_jhjehe.m3u"
      else:
        url = "http://iptv.example.ru/update8231257/iptv.xspf"

      r = get(url)
      return r.content
  app.logger.info("Браконьеры c ip %s" % ip)
  r = get("http://iptv.example.ru/update8231257/free.xspf")
  return r.content



@app.route("/data/stb/")
def getStbs():
  stbs = Stb.query.filter_by(deleted = False).all()
  response = stbsSchema.dump(stbs).data
  return Response(dumps(response),  mimetype = 'application/json')



@app.route("/data/stb/<int:id>")
def getStb(id):
  stb = Stb.query.get(id)
  response = stbSchema.dump(stb).data
  return Response(dumps(response),  mimetype = 'application/json')



@app.route("/data/stb/<int:id>", methods = ["put"])
def updateStb(id):
  args = request.get_json()
  stb = Stb.query.get(args["id"])
  stb.setKey(args["key"])
  stb.setMac(args["mac"])
  stb.setUpdateTime(datetime.now())
  db.session.commit()
  response = stbSchema.dump(stb).data
  return Response(dumps(response),  mimetype = 'application/json')



@app.route("/data/stb/<int:id>", methods = ["delete"])
def deleteStb(id):
  stb = Stb.query.get(id)
  stb.setDeletedStatus()
  stb.setUpdateTime(datetime.now())
  db.session.commit()
  response = stbSchema.dump(stb).data
  return Response(dumps(response),  mimetype = 'application/json')



@app.route("/data/stb/", methods = ["post"])
def createStb():
  args = request.get_json()
  existStb = Stb.query.filter_by(mac = args["mac"], deleted = False).one_or_none()
  if existStb:
    raise RuntimeError("Приставка с этим mac уже существует")
  stb = Stb(args["epay"], args["mac"], args["key"])
  db.session.add(stb)
  db.session.commit()
  response = stbSchema.dump(stb).data
  return Response(dumps(response),  mimetype = 'application/json')



if __name__ == "__main__":
  db.init_app(app)
  app.run(debug = True, host = "0.0.0.0", port = 8089)