import asyncio

import socketio

sio = socketio.AsyncClient()


@sio.event
async def connect():
    print('connection established')


@sio.event
async def msg(data):
    print(f'SOCKETIO CLIENT: message received "{data}"')


@sio.event
async def disconnect():
    print('disconnected from server')


async def main():
    sio.connection_headers = {'HTTP_AUTHORIZATION': 'Bearer TestToken'}
    await sio.connect(url='http://localhost:8080', headers={
        'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJrYXNwZWsiLCJpZCI6Niwicm9sZSI6InVzZXIiLCJleHAiOjE3Mjk1MjkwMzJ9.7ctnbpunellotveBfGyFD94YaR0GEyZAZLAIU31L7d0'})

    await sio.emit('follow_auction', {'auction_id': 8})
    await sio.emit('follow_auction', {'auction_id': 8})
    await sio.wait()


if __name__ == '__main__':
    asyncio.run(main())
