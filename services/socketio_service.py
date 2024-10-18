import socketio
from aiohttp import web
from jose import jwt
from utils.constants import socketio_logger as logger

from response_models.auth_responses import SECRET_KEY, ALGORITHM

sio = socketio.AsyncServer(cors_allowed_origins="*")
app = web.Application()
sio.attach(app)


# store sid - jwt mapping
class SocketUser:
    def __init__(self, sid):
        self.sid = sid
        self.jwt = ""
        self.user_id = ""
        self.username = ""
        self.followed_auctions = []

    def authenticate(self, token: str) -> bool:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            self.username = payload.get('sub')
            self.user_id = payload.get('id')
            return True
        except jwt.JWTError as e:
            logger.error(f"{self} authentication failed: {e}")
            return False

    async def send_message(self, message):
        await sio.emit('msg', room=self.sid, data=message)

    async def follow_auction(self, auction_id):
        if auction_id in self.followed_auctions:
            logger.trace(f"{self} already following auction {auction_id}")
            await self.send_message(f"You are already following auction {auction_id}")
            return

        if len(self.followed_auctions) > 5:
            logger.trace(f"{self} can only follow up to 5 auctions")
            await self.send_message("You can only follow up to 5 auctions")
            return

        self.followed_auctions.append(auction_id)
        await sio.enter_room(self.sid, auction_id)
        logger.info(f"{self} following auction {auction_id}")

    def __str__(self):
        return f"SocketUser(sid={self.sid}, user_id={self.user_id}, username={self.username})"


class SocketManager:
    def __init__(self):
        self.user_sessions = {}

    def add_user(self, sid: str, user: SocketUser):
        self.user_sessions[sid] = user

    def remove_user(self, sid: str):
        if sid in self.user_sessions:
            del self.user_sessions[sid]

    def get_user(self, sid: str):
        return self.user_sessions.get(sid)

    def get_user_by_id(self, user_id: str):
        for sid, user in self.user_sessions.items():
            if user.user_id == user_id:
                return user
        return None


socket_manager = SocketManager()


@sio.event
async def connect(sid, environ):
    token = environ.get('HTTP_AUTHORIZATION')

    socket_user = SocketUser(sid)
    if not socket_user.authenticate(token):
        logger.trace(f"unauthorized connection: {sid}")
        await sio.disconnect(sid)
        return False

    socket_manager.add_user(sid, socket_user)
    logger.info(f"{socket_user} connected")


@sio.event
async def disconnect(sid):
    user = socket_manager.get_user(sid)
    if user:
        logger.info(f"{user} disconnected")
        socket_manager.remove_user(sid)
    else:
        logger.trace(f"{sid} disconnected")


@sio.event
async def follow_auction(sid, data):
    socket_user: SocketUser = socket_manager.get_user(sid)
    if socket_user is None:
        logger.trace(f"unauthorized follow_auction: {sid}")
        return

    auction_id = data.get('auction_id')
    if auction_id is None:
        logger.trace(f"{socket_user} auction_id is required")
        await socket_user.send_message("Auction ID is required")
        return

    await socket_user.follow_auction(auction_id)


if __name__ == '__main__':
    web.run_app(app)
