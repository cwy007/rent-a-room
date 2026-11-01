from sqlmodel import Field, SQLModel


# 基础模型类，用于定义房间的公共属性
class RoomBase(SQLModel):
    name: str = Field()
    price_per_night: int = Field()
    bedrooms: float = Field(multiple_of=0.5)
    bathrooms: float = Field(multiple_of=0.5)


# 房间表模型 - 对应数据库中的房间表
class Room(RoomBase, table=True):
    __tablename__: str = "rooms"

    id: int | None = Field(default=None, primary_key=True)


# 房间响应模型 - 用于返回给客户端的房间信息
class RoomPublic(RoomBase):
    id: int


# 房间更新模型 - 用于更新房间信息
class RoomUpdate(SQLModel):
    name: str | None = None
    price_per_night: int | None = None
    bedrooms: float | None = None
    bathrooms: float | None = None
