from sqlalchemy import and_

from endrev import db


class BeatleboardSong(db.Model):
    __tablename__ = "beatleboard_songs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)

    name = db.Column(db.Text, nullable=False)
    album = db.Column(db.Text, nullable=False)
    artist = db.Column(db.Text, nullable=False)

    released = db.Column(db.DateTime, nullable=False)

    visible = db.Column(db.Integer, nullable=False)

    @classmethod
    def get(cls, id: int):
        return BeatleboardSong.query.filter_by(id=id).one_or_none()

    @classmethod
    def get_all_by_name(cls, songname: str, visible_only: bool = False):
        if visible_only:
            songs = BeatleboardSong.query.filter(
                and_(
                    BeatleboardSong.name.like(f"%{songname}%"),
                    BeatleboardSong.visible.is_(1),
                )
            ).all()
        else:
            songs = BeatleboardSong.query.filter(
                BeatleboardSong.album.like(f"%{songname}%")
            ).all()
        return songs

    @classmethod
    def get_all_by_album(cls, albumname: str, visible_only: bool = False):
        if visible_only:
            songs = BeatleboardSong.query.filter(
                and_(
                    BeatleboardSong.album.like(f"%{albumname}%"),
                    BeatleboardSong.visible.is_(1),
                )
            ).all()
        else:
            songs = BeatleboardSong.query.filter(
                BeatleboardSong.album.like(f"%{albumname}%")
            ).all()
        return songs

    def to_json(self):
        return {
            "song-id": self.id,
            "name": self.name,
            "album": self.album,
            "artist": self.artist,
            "released": self.released.isoformat(),
        }
