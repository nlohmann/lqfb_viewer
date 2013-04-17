from app import db

class Member(db.Model):
    member_id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.Text)
    api_key = db.Column(db.Text)
    active = db.Boolean()

    def __repr__(self):
        return '<Member %r>' % (self.member_id)
