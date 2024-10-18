import socketio
from aiohttp import web
from jose import jwt

from response_models.auth_responses import SECRET_KEY, ALGORITHM
from utils.constants import socketio_logger as logger, WebSocketAction

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
            logger.trace(f"{self} authentication failed: {e}")
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

        await self.send_message(f"Following auction {auction_id}")
        logger.trace(f"{self} following auction {auction_id}")

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

    def get_user(self, sid: str) -> SocketUser | None:
        return self.user_sessions.get(sid)

    def get_user_by_user_id(self, user_id: str) -> SocketUser | None:
        for sid, user in self.user_sessions.items():
            if user.user_id == user_id:
                return user
        return None

    async def send_action_to_user(self, user_id: str, data: str):
        user = self.get_user_by_user_id(user_id)
        if user:
            await sio.emit('action', data=data, room=user.sid)
            logger.trace(f"Sent {data} to {user}")

    @staticmethod
    async def send_action_to_auction(auction_id: int, data: str):
        await sio.emit('action', data=data, room=auction_id)
        logger.trace(f"Sent {data} to auction {auction_id}")

    @staticmethod
    async def bid_price_update_action(auction_id: int, new_bid_value: float):
        await sio.emit(WebSocketAction.BID_PRICE_UPDATE, data={"price": new_bid_value}, room=auction_id)

    def bid_winner_update_action(self, user_id: str):
        user = self.get_user_by_user_id(user_id)
        if not user:
            logger.error(f"Failed to send bid_winner_update to {user_id}")
            return

        sio.emit(WebSocketAction.BID_WINNER_UPDATE, data={}, room=user.sid)


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
