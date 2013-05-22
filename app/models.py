from app import db

class Member(db.Model):
    member_id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.Text)
    api_key = db.Column(db.Text)
    active = db.Boolean()

    def __repr__(self):
        return '<Member %r>' % (self.member_id)


class APIData(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    endpoint = db.Column(db.Text, primary_key = True)
    payload = db.Column(db.Text)
    
    def __repr__(self):
        return '<APIData %r %s>' % (self.id, self.endpoint)


class Timestamp(db.Model):
    endpoint = db.Column(db.Text, primary_key = True)
    id = db.Column(db.Integer)

    def __repr__(self):
        return '<Timestamp %s %r>' % (self.endpoint, self.id)
