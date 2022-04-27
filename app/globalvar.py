from app.models import *

programme_time = list(range(0, 24))


def init_data():
    if not User.query.filter_by(username="root").first():
        root = User(username="root", email="root@email.com", admin=True, root=True)
        root.set_password("rootroot")
        db.session.add(root)
        db.session.commit()