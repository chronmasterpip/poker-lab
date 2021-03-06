import os
import logging
import redis
import gevent
from flask import Flask, render_template
from flask_sockets import Sockets

REDIS_URL = os.environ['REDIS_URL']
REDIS_CHAN = 'gamestate'
# set up sockets
sockets = Sockets(app)
# redis = redis.from_url(REDIS_URL)
# Run GamestateBackend
gamestate_data = GamestateBackend(REDIS_CHAN)
gamestate_data.start()

class GamestateBackend(object):
	"""Interface for registering and updating WebSocket clients."""

	def __init__(self, redis_chan):
		self.clients = list()
		self.pubsub = redis.pubsub()
		self.pubsub.subscribe(redis_chan)


	def register(self, client):
		"""Register a WebSocket connection for Redis updates."""
		self.clients.append(client)


	def send(self, client, data):
		"""Send given data to the registered client.
		Automatically discards invalid connections."""
		try:
			client.send(data)
		except Exception:
			self.clients.remove(client)


	def run(self):
		"""Listens for new messages in Redis, and sends them to clients."""
		for data in self.__iter_data():
			for client in self.clients:
				gevent.spawn(self.send, client, data)


	def start(self):
		"""Maintains Redis subscription in the background."""
		gevent.spawn(self.run)


gamestate = GamestateBackend()
gamestate.start()