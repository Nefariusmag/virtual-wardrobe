from wardrobe import db


def import_default_clothe_types(approot, datafile='default_clothe_types.csv'):
    datafile = '{}/static/{}'.format(approot, datafile)
    with open(datafile) as f:
        for data in f:
            data = data.split(',')
            desc = data[0].rstrip('\n')
            pos = data[1].rstrip('\n')
            if not Clothes.Types.query.filter(Clothes.Types.desc == desc).filter(Clothes.Types.pos == pos).all():
                db.session.add(Clothes.Types(desc, pos))
                db.session.commit()


class Clothes(db.Model):
    __tablename__ = 'clothes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(128))
    clth_type = db.Column(db.Integer, db.ForeignKey('clth_type.id'))
    temperature_min = db.Column(db.Integer)
    temperature_max = db.Column(db.Integer)
    file_path = db.Column(db.String(128))

    def __init__(self, user_id, name, clth_type, temperature_min, temperature_max, file_path):
        self.user_id = user_id
        self.name = name
        self.clth_type = clth_type
        self.temperature_min = temperature_min
        self.temperature_max = temperature_max
        self.file_path = file_path

    class Types(db.Model):
        __tablename__ = 'clth_type'
        id = db.Column(db.Integer, primary_key=True)
        desc = db.Column(db.String(64))
        pos = db.Column(db.String(64))

        def __init__(self, desc, pos):
            self.desc = desc
            self.pos = pos
