extends Control

var header
var timeline
var agents
var timestamps
var positions


func _on_pick_csv_button_pressed():
	%CsvFileDialog.popup()


func _on_csv_file_dialog_dir_selected(dir):
	read_timeline(dir.path_join("timeline.json"))
	read_timestamp(dir.path_join("timestamps.json"))
	read_positions(dir.path_join("positions.json"))
	load_agents_data(dir.path_join("agents_data.json"))


func read_timeline(path):
	var temp = FileAccess.get_file_as_string(path)
	timeline = JSON.parse_string(temp)
	%CurrentActions.columns = timeline[0].size()

func load_agents_data(path):
	var temp = FileAccess.get_file_as_string(path)
	agents = JSON.parse_string(temp)
	print(agents[str(0)])

func read_timestamp(path):
	var temp = FileAccess.get_file_as_string(path)
	timestamps = JSON.parse_string(temp)
	%Timeline.max_value = timestamps.size() - 1
	%Timestamps.text = str(timestamps[0]) + " - " + str(timestamps[1])


func read_positions(path):
	var temp = FileAccess.get_file_as_string(path)
	positions = JSON.parse_string(temp)
	print(positions[0])

func _on_timeline_value_changed(value):
	# Actions & timestamps
	var actions = %CurrentActions.get_children()
	if actions:
		for n in actions:
			%CurrentActions.remove_child(n)
			n.queue_free()
	if value == timestamps.size() - 1:
		%Timestamps.text = str(timestamps[value]) + " - END"
	else:
		%Timestamps.text = str(timestamps[value]) + " - " + str(timestamps[value+1])
		for action in timeline:
			if timestamps[value] <= action["decision_time"] and action["decision_time"] < timestamps[value+1]:
				for k in action:
					var action_attribute = Label.new()
					action_attribute.text = str(action[k])
					var color = agents[str(action["id"])]["color"]
					action_attribute.modulate = Color(color[0]/255, color[1]/255, color[2]/255)
					%CurrentActions.add_child(action_attribute)
	
	# Map
	var population = %Map/Population.get_children()
	if population:
		for n in population:
			%Map/Population.remove_child(n)
			n.queue_free()
	
	for id in positions[value]:
		draw_agent(positions[value][id], agents[id]["color"])

func draw_agent(pos, color):
	const AGENT = preload("res://agent.tscn")
	var new_agent = AGENT.instantiate()
	new_agent.position = Vector2(pos[1], pos[0]) * 16
	new_agent.modulate = Color(color[0]/255, color[1]/255, color[2]/255)
	%Map/Population.add_child(new_agent)
	







