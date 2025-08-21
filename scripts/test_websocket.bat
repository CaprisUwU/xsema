@echo off
echo Testing WebSocket connection to ws://localhost:8001/ws...
echo.
python -c "import asyncio, websockets, json; asyncio.get_event_loop().run_until_complete((lambda: (ws := __import__('websockets').connect('ws://localhost:8001/ws'), print('Connected!'), ws.__aenter__())[2] and (await ws.send(json.dumps({'message': 'Hello from test client!'}))) and print(f'Sent: {{"message": "Hello from test client!"}}') and (response := await ws.recv()) and print(f'Received: {response}') and (await ws.close()) and print('Connection closed.') or None)())()"

echo.
echo Test complete.
pause
