from datetime import datetime

from app.extensions import db


class Media(db.Model):
    __tablename__ = "media"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    file_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    post = db.relationship("Post", back_populates="media")

    def __repr__(self):
        return f"<Media {self.id}>"
