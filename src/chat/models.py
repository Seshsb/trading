from sqlalchemy import Column, Integer, String, BigInteger

from database import Base


class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    message = Column(String)
    client_id = Column(BigInteger)
    cnt_likes = Column(Integer, default=0)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
