extends Control

var header
var timeline_actions = {}
var timestamps
var positions


func _on_pick_csv_button_pressed():
	%CsvFileDialog.popup()


func _on_csv_file_dialog_dir_selected(dir):
	read_csv(dir.path_join("timeline.csv"))
	read_timestamp(dir.path_join("timestamps.json"))
	read_positions(dir.path_join("positions.json"))


func read_csv(path):
	var file = FileAccess.open(path, FileAccess.READ)
	
	# Header
	header = file.get_csv_line()
	for c in header:
		timeline_actions[c] = []
	%ActionsHeader.clear()
	%ActionsHeader.max_columns = header.size()
	%ActionsItems.clear()
	%ActionsItems.max_columns = header.size()
	
	# Data
	while file.get_position() < file.get_length():
		var line = file.get_csv_line()
		for c in line.size():
			timeline_actions[header[c]].append(line[c])
	
	for h in header:
		%ActionsHeader.add_item(h)
	for i in range(timeline_actions[header[0]].size()):
		for h in header:
			%ActionsItems.add_item(timeline_actions[h][i])

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
	#var text = ""
	#for h in header:
		#text += " " + timeline_actions[h][value]
	#%CurrentAction.text = text
	print(value)

	if value == timestamps.size() - 1:
		%Timestamps.text = str(timestamps[value]) + " - END"
	else:
		%Timestamps.text = str(timestamps[value]) + " - " + str(timestamps[value+1])
	%Positions.text = str(positions[value])
