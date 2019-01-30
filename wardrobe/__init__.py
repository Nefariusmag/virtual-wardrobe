from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


class InitDefaults(object):

    def __init__(self, *args):
        self.args = args

    def __call__(self):
        for arg in self.args:
            run_func = getattr(self, arg[0], 0)
            if run_func:
                # todo: validate arguments consistency
                run_func(*arg[1:])

    def import_default_clothe_types(self, approot, datafile='default_clothe_types.csv'):
        from clothes.models import Clothes
        datafile = '{}/static/{}'.format(approot, datafile)
        with open(datafile) as f:
            for data in f:
                data = data.split(',')
                desc = data[0].rstrip('\n')
                pos = data[1].rstrip('\n')
                if not Clothes.Types.query.filter(Clothes.Types.desc == desc).filter(Clothes.Types.pos == pos).all():
                    db.session.add(Clothes.Types(desc, pos))
                    db.session.commit()

    def import_default_user_roles(self, roles):
        from users.models import UserRole
        for role in roles:
            if not UserRole.query.filter(UserRole.role == role).all():
                db.session.add(UserRole(role=role))
                db.session.commit()
