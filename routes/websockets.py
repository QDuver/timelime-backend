import time
from flask_socketio import emit
import config as c
from utils.images import generate_image


def register_socket_events(socketio):

    @socketio.on('generate-image')
    def handle_generate_image(timeline_id):
        events = c.db.get('events', where=('tid', '==', timeline_id))        
        to_generate = [event for event in events if event.get('imageGenerating', False) == True]
        time.sleep(4)
        for event in to_generate:
            print(event)
            url = generate_image('ai', event)
            print(url)
            emit('generate-image', {'id': event['id'], 'url': url})

