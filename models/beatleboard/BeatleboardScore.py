import datetime

from endrev import db

DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


class BeatleboardScore(db.Model):
    __tablename__ = "beatleboard_scores"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    gtr_id = db.Column(db.Integer, nullable=True)
    gtr_username = db.Column(db.Text, nullable=True)

    drums_id = db.Column(db.Integer, nullable=True)
    drums_username = db.Column(db.Text, nullable=True)

    bass_id = db.Column(db.Integer, nullable=True)
    bass_username = db.Column(db.Text, nullable=True)

    vox_id = db.Column(db.Integer, nullable=True)
    vox_username = db.Column(db.Text, nullable=True)

    harms_id = db.Column(db.Integer, nullable=True)
    harms_username = db.Column(db.Text, nullable=True)

    score = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    image_proof = db.Column(db.Text, nullable=False)
    song_id = db.Column(db.Integer, nullable=False)

    uploader_id = db.Column(db.Integer, nullable=False)

    def __init__(self, **kwargs):
        super(BeatleboardScore, self).__init__(**kwargs)
        self.date = datetime.datetime.utcnow()

    @classmethod
    def get(cls, id: int):
        return BeatleboardScore.query.filter_by(id=id).one_or_none()

    @classmethod
    def get_by_uploader_userid(cls, userid: str):
        return BeatleboardScore.query.filter_by(uploader_userid=userid).one_or_none()

    @classmethod
    def get_by_gtr_userid(cls, userid: str):
        return BeatleboardScore.query.filter_by(gtr_userid=userid).one_or_none()

    @classmethod
    def get_by_drums_userid(cls, userid: str):
        return BeatleboardScore.query.filter_by(drums_userid=userid).one_or_none()

    @classmethod
    def get_by_bass_userid(cls, userid: str):
        return BeatleboardScore.query.filter_by(bass_userid=userid).one_or_none()

    @classmethod
    def get_by_vox_userid(cls, userid: str):
        return BeatleboardScore.query.filter_by(vox_userid=userid).one_or_none()

    @classmethod
    def get_by_harms_userid(cls, userid: str):
        return BeatleboardScore.query.filter_by(harms_userid=userid).one_or_none()
