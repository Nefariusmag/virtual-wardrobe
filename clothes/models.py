from wardrobe import db


class Clothes(db.Model):
    __tablename__ = 'clothes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(128))
    clth_type = db.Column(db.String(128))
    # top = db.Column(db.Boolean)
    # bottom = db.Column(db.Boolean)
    # upper = db.Column(db.Boolean)
    # lower = db.Column(db.Boolean)
    temperature_min = db.Column(db.Integer)
    temperature_max = db.Column(db.Integer)

    def __init__(self, user_id, name, clth_type,
                 # top, bottom, upper, lower,
                 temperature_min, temperature_max):
        self.user_id = user_id
        self.name = name
        self.clth_type = clth_type
        # self.top = top
        # self.bottom = bottom
        # self.upper = upper
        # self.lower = lower
        self.temperature_min = temperature_min
        self.temperature_max = temperature_max
