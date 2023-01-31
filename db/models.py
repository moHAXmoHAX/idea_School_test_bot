from db import session, Users


async def create_user(name: str, username: str, rand_num: int):
    with session(future=True) as sess:
        user = Users(name=name,
                     username=username,
                     rand_num=rand_num)
        sess.add(user)
        sess.commit()


async def user_exist(user_id: int = None, username: str = None, name: str = None) -> bool:
    with session(future=True) as sess:
        if username:
            return sess.query(Users.id).filter(Users.username == username).first() is not None
        elif name:
            return sess.query(Users.id).filter(Users.name == name).first() is not None
        elif user_id:
            return sess.query(Users.id).filter(Users.id == user_id).first() is not None
        else:
            return False


async def update_user(name: str, new_name: str):
    with session(future=True) as sess:
        user = sess.query(Users).filter(Users.name == name).first()
        user.name = new_name
        sess.commit()


async def user_delete(name: str):
    with session(future=True) as sess:
        sess.query(Users).filter(Users.name == name).delete()
        sess.commit()


async def get_users_count() -> int:
    with session(future=True) as sess:
        users = sess.query(Users).count()
    return users


async def get_user(user_id: int) -> int:
    with session(future=True) as sess:
        rand_num = sess.query(Users.rand_num).filter(Users.id == user_id).first()
    return rand_num[0]

