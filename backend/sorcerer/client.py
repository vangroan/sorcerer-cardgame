from websockets.sync.client import connect


def hello():
    with connect("ws://localhost:8765") as websocket:
        websocket.send("Hello world!")
        message = websocket.recv()
        print(f"Received: {message}")


def hello_forever():
    with connect("ws://localhost:8765") as websocket:
        while True:
            message = websocket.recv()
            print(f"Received: {message}")
