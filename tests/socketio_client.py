import asyncio
import os

import socketio
from dotenv import load_dotenv

sio = socketio.AsyncClient()


@sio.event
async def connect():
    print('connection established')


@sio.event
async def msg(data):
    print(f'SOCKETIO CLIENT: message received "{data}"')


@sio.event
async def bid_price_update(data):
    print(f'SOCKETIO CLIENT: bid price update received "{data}"')


@sio.event
async def bid_winner_update(data):
    print(f'SOCKETIO CLIENT: bid winner updated')


@sio.event
async def disconnect():
    print('disconnected from server')


async def main():
    load_dotenv()

    await sio.connect(url='https://ws.charfair.me', headers={'Authorization': os.getenv('SOCKETIO_CLINET_JWT')})
    # await sio.connect(url='http://localhost:8080', headers={'Authorization': os.getenv('SOCKETIO_CLINET_JWT')})

    await sio.emit('follow_auction', {'auction_id': 8})
    await sio.wait()


if __name__ == '__main__':
    asyncio.run(main())
