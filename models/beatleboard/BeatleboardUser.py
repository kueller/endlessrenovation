from zlib import adler32

from endrev import db


class BeatleboardUser(db.Model):
    __tablename__ = "beatleboard_users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.Text, nullable=False)
    display_name = db.Column(db.Text, nullable=False)

    userid = db.Column(db.Text, nullable=False)

    hash = db.Column(db.Text, nullable=False)

    def __init__(self, **kwargs):
        super(BeatleboardUser, self).__init__(**kwargs)
        self.hash_userid()

    @classmethod
    def get(cls, id: int):
        return BeatleboardUser.query.filter_by(id=id).one_or_none()

    @classmethod
    def get_by_userid(cls, userid):
        return BeatleboardUser.query.filter_by(userid=userid).one_or_none()

    @classmethod
    def get_by_hash(cls, hash):
        return BeatleboardUser.query.filter_by(hash=hash).one_or_none()

    def hash_userid(self):
        self.hash = str(adler32(str.encode(self.userid)))
