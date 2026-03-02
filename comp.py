import os
import sys
import json as json_module
import re
import copy
import ast
import ollama
from pathlib import Path
from shell import Shell
from function_extractor import extract_functions
from litellm import completion
	
def command_syntax(data):
	if '|>' in data and '<|' not in data:
		raise SyntaxError(f'Unfinished |> command specifier in {data}')
	elif '|>' not in data and '<|' in data:
		raise SyntaxError(f'Unstarted <| command specifier in {data}')
	elif data.count('|>') != data.count('<|'):
		raise SyntaxError(f'There is a command specifier mismatch in {data}')
	elif '&F' in data and ';' in data:
		raise SyntaxError(f'Extracting functions from a variable is not a terminal command at {data}. Remove the command specifier or use the assign methods.')
	elif '&D' in data and ';' in data:
		raise SyntaxError(f'Extracting a decision from an AI model output is not a terminal command at {data}. Remove the command specifier or use the assign methods.')
	elif '->' in data or '<-' in data:
		raise SyntaxError(f'Unspecified value movement in {data}')
	else:
		return data

def data_syntax(data):
	if '<$>' in data:
		raise SyntaxError(f'The <$> symbol is reserved for passable data specifiers in {data}. If your json data contains this exact string please modify it.')
	elif '<$' in data and '>' not in data:
		raise SyntaxError(f'Unfinished passable data specifier in {data}')
	elif '<' not in data and '$' in data and '>' in data:
		raise SyntaxError(f'Unstarted passable data specifier in {data}')
	elif ('&I' in data or '&O' in data or '&D' in data or '&M' in data or '&P' in data or '&S' in data or '&F' in data or '&J' in data or '&V' in data or '&P' in data) and ';' not in data:
		raise SyntaxError(f'Storing variable references as plain json values in {data} is not currently supported.')
	elif '&D' in data and 'ˇ' not in data:
		raise SyntaxError(f"At least two options with an 'or: ˇ' statement has to be specified in {data} for execution assignment")
	elif '&' in data or '<$' in data:
		return data
		
def specifier_syntax(data):
	if '~|' in data and '|~' not in data:
		raise SyntaxError(f'Unfinished ~| command specifier in {data}')
	elif '~|' not in data and '|~' in data:
		raise SyntaxError(f'Unstarted |~ command specifier in {data}')
	elif '(~|' in data and '|~)' not in data:
		raise SyntaxError(f"Unfinished '(' parallel command specifier in {data}")
	elif '(~|' not in data and '|~)' in data:
		raise SyntaxError(f"Unstarted ')' parallel command specifier in {data}")
	elif '~|' not in data and '|~' not in data:
		return data
def assigned_command_syntax(command, assigner):
	if '$' in assigner and '<$>' not in command:
		raise RuntimeError(f'There is no variable space to be assigned in {command} from {assigner}')
	elif '<$' in command and '$>' not in command:
		raise RuntimeError(f'There is an unclosed <$ varibale space in {command}')
	elif '$' not in command and '$>' in command:
		raise RuntimeError(f'There is an unstarted $> varibale space in {command}')
	elif assigner.count('$') != command.count('<$>'):
		raise RuntimeError(f'There is a variable assignment mismatch in {command} from {assigner}')

def command_without_assignment_syntax(data):
	if '|>' not in data and '<|' not in data:
		raise RuntimeError(f"Your command doesn't have any runnable instruction at {data}")
	elif 'A&' in data:
		raise RuntimeError(f"AI variable reference cannot be used without a valid assignment at {data}")
	elif '&' in data and '&=' not in data and ' &' not in data and '& ' not in data and data.count('&') <= 1:
		raise RuntimeError(f"Custom variable reference cannot be used without a valid assignment at {data}")

def raw_value_syntax(command, assigner):
	if '&' not in assigner:
		raise RuntimeError(f"A non variable should always have a reference in the assignment in {assigner} from {command}")
	if '¤' not in assigner:
		raise RuntimeError(f"Since {command} is a simple value from you should provide a raw specificator in the assigner at {assigner}")
	elif '&#' in assigner:
		raise RuntimeError(f"No terminal output can be assigned from an instruction without a shell command in {assigner} from {command}")
	elif '&€' in assigner:
		raise RuntimeError(f"No script content can be assigned from an intruction without a file specificator in {assigner} from {command}")
	elif '¤S' not in assigner and '¤I' not in assigner and '¤L' not in assigner:
		raise RuntimeError(f"No valid assignment type (string, integer or list) was found in {assigner} from {command}. ")

def file_value_load_syntax(command, assigner):
	if command.count('.') > 1:
		raise RuntimeError(f"The instruction {command} doesn't have any referencable value with {assigner}")
	elif '&#' in assigner:
		raise RuntimeError(f"The instruction {command} doesn't have an assignable command output with {assigner}")
	elif '[' in assigner or ']' in assigner:
		raise RuntimeError(f"Array assignment from {command} is not possible via {assigner}")
	elif not Path(command.strip()).is_file():
		raise RuntimeError(f"The file specified in: {command} can't be found.")

def file_value_save_syntax(command, assigner):
	if '$' in assigner:
		raise RuntimeError(f"Variable reference cannot be passed to a file")
	
def command_value_syntax(command, assigner):
	if '#' not in assigner and '€' not in assigner:
		raise RuntimeError(f"Only command and content outputs can be assigned from runnable commands")
	elif '¤' in assigner:
		raise RuntimeError(f"Raw assignment of data containing command specifiers are not allowed.")
		
def json_data_value_access_syntax(command, assigner):
	command = re.sub(r'\|>|<\|', '', command, re.DOTALL)
	if command.count('&=') > 1:
		raise RuntimeError(f"Only one value access can be specified at {command} from {assigner}")
	elif '&=' in command and '.&=' not in command:
		raise SyntaxError(f"Referencing a json data value in an intruction should follow the standard json access syntax at {command} from {assigner}")
	elif '&=.' in command:
		raise RuntimeError(f"Further json access of a json data value is prohibited at {command} from {assigner}")
	elif '¤' in assigner:
		raise RuntimeError(f"Assigning raw value with a json_value reference is not supported at {command} from {assigner}")

def json_parallel_value_call_syntax(data):
	if '(' in data and ')' not in data:
		raise SyntaxError(f"Unfinished '(' parallel json data access specifier in {data}")
	elif '(' not in data and ')' in data:
		raise SyntaxError(f"Unstarted ')' parallel json data access specifier in {data}")

def json_value_variable_syntax(data):
	if '$' in data and 'ˇ' in data and '<$' not in data:
		raise SyntaxError(f"There is a sensitive syntax that has to be met when passing variable declarations from function calls")
	elif '$' in data and 'ˇ' not in data:
		raise RuntimeError(f"Passing variable to json access is not possible if json access is first instruction at {data}")

def ai_variable_syntax(variable):
	if not variable.upper():
		raise SyntaxError(f"A variable reference can only contain uppercase letters")
	elif variable.count('&') > 1:
		raise RuntimeError(f"Invalid additional & reference character in {variable}")
	elif '&F' in variable or '&J' in variable or '&V' in variable:
		raise RuntimeError(f"AI variable does not have self created variable entries at {variable}")
	elif '&M' not in variable and '&P' not in variable and '&I' not in variable and '&O' not in variable and '&D' not in variable and '&S' not in variable:
		raise RuntimeError(f"Invalid data type reference for variable at {variable}")
	elif '|>' in variable or '<|' in variable:
		raise RuntimeError(f"A variable reference can't be ran as a command in {variable}")
		
def custom_variable_syntax(variable):
	if not variable.upper():
		raise SyntaxError(f"A variable reference can only contain uppercase letters")
	elif variable.count('&') > 1:
		raise RuntimeError(f"Invalid additional & reference character in {variable}")
	elif '&M' in variable or '&I' in variable or '&O' in variable:
		raise RuntimeError(f"Self created variable does not have AI variable entries at {variable}")
	elif '&S' not in variable and '&F' not in variable and '&J' not in variable and '&V' not in variable and '&P' not in variable and '&D' not in variable:
		raise RuntimeError(f"Invalid data type reference for variable at {variable}")
	elif '|>' in variable or '<|' in variable:
		raise RuntimeError(f"A variable reference can't be ran as a command in {variable}")

def json_value_assign_syntax(command, assigner):
	if '=' not in assigner:
		raise RuntimeError(f'Assigning json_value from instruction has to contain the base symbol for json access in {assigner} with {command}')
	elif '&€' in assigner or '&#' in assigner:
		raise RuntimeError(f'Content and command output reference is not possible from a plain json access at {command} with {assigner}')

def variable_value_access_syntax(command, assigner):
	if '&' in assigner:
		raise RuntimeError(f"The variable already contains a reference at {command} a reference can't be reference further via {assigner}")
	elif '#' in assigner or '=' in assigner:
		raise RuntimeError(f"Reference type assignments are not possbile from a variable at {command} with {assigner}")
	elif 'S' not in assigner and 'I' not in assigner and 'L' not in assigner:
		raise RuntimeError(f"Invalid data type assignment from {command} with {assigner}")
	elif '¤' in assigner:
		raise RuntimeError(f"Assigning a variable reference as a raw value is not possbile at {command} with {assigner}")

def multiple_command_syntax(command, assigner):
	if '(>' in command and '<)' not in command:
		raise SyntaxError(f"Unfinished (> multiple command specifier in {command}'")
	elif '(>' not in command and '<)' in command:
		raise SyntaxError(f"Unstarted <) multiple command specifier in {command}'")
	elif command.count('(>') > 1 or command.count('<)') > 1:
		raise RuntimeError(f"Nested multiple command specifiers are not allowed in {command}")
	elif '|>' not in command and '<|' not in command:
		raise SyntaxError(f"A command has to be specified at multiple command call at {command}")
	elif ',' not in command:
		raise SyntaxError(f"At least two command has to be separated with , in a multiple command call at {command}")
	elif 'A&' in command or '&V' in command or '&F' in command or '&S' in command or '&J' in command or '&D' in command:
		raise RuntimeError(f"Multiple command call can't contain value references at {command}")
	elif '#' not in assigner:
		raise RuntimeError(f"Only command output can assigned from multiple command call at {command} with {assigner}")

def json_variable_syntax(data):
	if 'I' not in data and 'S' not in data and 'L' not in data:
		raise SyntaxError(f"Unsupported data type at {data}")

def method_place_holder_syntax(data):
	if '&F' not in data:
		raise RuntimeError(f"Only functions can be extracted from a script entry at the moment")

def reference_variable_place_holder_syntax(data):
	if '[<$>' in data and '<$>]' not in data:
		raise SyntaxError(f"Referencing to json array position has to have the array location first in {data}")

def reference_variable_assign_type_syntax(input_value, json_value, command, assigner):
	if 'I' in json_value and not isinstance(input_value, int):
		raise RuntimeError(f"There is an integer data_type mismatch between {type(input_value)} and {int} in {command} when assigning with {assigner}")
	if 'S' in json_value and not isinstance(input_value, str):
		raise RuntimeError(f"There is a string data_type mismatch between {type(input_value)} and {str} in {command} when assigning with {assigner}")
	if 'L' in json_value and not isinstance(input_value, list):
		raise RuntimeError(f"There is a list data_type mismatch between {type(input_value)} and {list} in {command} when assigning with {assigner}")
	
def assigner_syntax(command, assigner):
	if assigner.count('$') > 1 and '[$' not in assigner and ']' not in assigner:
		raise SyntaxError(f"Separate variable references has to be declared inside an assignment list from {assigner} to {command}")
	if assigner.count('$') > 1 and '[$' in assigner and ']' not in assigner:
		raise SyntaxError(f"Unfinished [ multiple variable pass from {assigner} to {command}'")
	elif assigner.count('$') > 1 and '[$' not in assigner and ']' in assigner:
		raise SyntaxError(f"Unstarted ] multiple variable pass from {assigner} to {command}'")
	elif assigner.count('$') > 1 and assigner.count('$') <= assigner.count(','):
		raise SyntaxError(f"Separate variable references has to be separated via ',' from {assigner} to {command}")

def chain_start_command_syntax(data):
	if '<$>' in data:
		raise RuntimeError(f"First command during an execution can't contain a variable reference in {data}")

def ai_model_syntax(set_model, set_provider):
	if set_provider == 'ollama':		
		try:
			response = ollama.list()
		except:
			raise RuntimeError(f"Getting the list of available models failed when checking against {set_model}")
	
		for model in response.models:
			if set_model == model['model']:
				return
	
		raise AttributeError(f"The model to set {set_model} could not be found in the available ollama models")
	elif api_keys and set_provider not in api_keys:
		raise AttributeError(f"The provider to set {set_provider} could not be found in the supported providers")
	elif not api_keys:
		raise RuntimeError(f"The api keys hasn't been loaded so using non ollama models is not possible")

def path_strip(path):
	path = path.split('.')
	del path[0]
	path = '.'.join(path)
	return path
	
def method_value_extract(method, path):
		instruction = method.split(';')
		method_entry = instruction[0].strip()
		function_to_extract = instruction[1].strip()
		variable = method_entry.split('&')[0] + '&S'
		script = variable_value_extract(variable, path)
		function_value = extract_functions(script, function_to_extract)
		path = path_strip(path)
		save_json_value_to_path(json, path, function_value)
		
		
def reference_variable_place_holder_assign(command, assigner, input_value):
	if '<$>]' in command and '[<$>]' not in command:
		input_value = value_convert(input_value, assigner)
		basic_command = command.replace('<$>', '')
		json_value = json_data_value_extract(basic_command)
		reference_variable_assign_type_syntax(input_value, json_value, command, assigner)
		json_data_value_save(basic_command, input_value)
		command = basic_command
		return command
		
	else:
		input_value = value_convert(input_value, assigner)
		command = command.replace('<$>', str(input_value))
		return command

def json_data_value_access_multiple_commands(commands, assigner, json_values):
	for command in commands:
		if '&=' in command:
			json_data_value_access_syntax(command, assigner)
			json_value = json_data_value_extract(command)
			json_values.append(json_value)
	return json_values

def multiple_command_extract(command):
	command = command.strip().removeprefix("(>").removesuffix("<)")
	commands = command.strip().split(',')
	return commands

def recursive_variable_save(outer, dict_var, ide, path, variable_name, variable_entry, input_value, ai, par_id):
	found, key = False, None
	for key, value in dict_var.items():
		if path[ide] in key:
			for k in range(len(value[1])):
				for declared_variable, entries in value[1][k].items():
					if variable_name in declared_variable:
						if not ai:
							for entry, var_value in entries.items():
								if variable_entry in entry:
									found = True
									access = []
									for val in outer:
										access.append(val)
										access.append(0)
									if key == 'json':
										access = [key, 1, k, declared_variable, entry]	
									else:
										access = access + [key, 1, k, declared_variable, entry]
									data = variables
									for accessor in access[:-1]:
										data = data[accessor]
									data[access[-1]] = input_value
						else:
							for id_par, ai_entries in entries.items():
								if id_par == par_id:
									for entry, var_value in ai_entries.items():
										if variable_entry in entry:
											found = True
											access = []
											for val in outer:
												access.append(val)
												access.append(0)
											if key == 'json':
												access = [key, 1, k, declared_variable, par_id, entry]	
											else:
												access = access + [key, 1, k, declared_variable, par_id, entry]
											data = variables
											for accessor in access[:-1]:
												data = data[accessor]
											data[access[-1]] = input_value
										
								else:
									pass
			break
	
	if key != outer[ide - 1]:
		outer.append(key)
	
	if path[ide] != key:
		route = path[path.index(path[ide]):]
		route = list(reversed(route))
		if not ai:
			dict_loc = {route[0]: [{}, [{variable_name : {variable_entry : input_value}}]]}
		else:
			dict_loc = {route[0]: [{}, [{variable_name : {par_id : {variable_entry : input_value}}}]]}
		
		if len(route) > 1:
			for d in range(len(route) - 1):
				if d == 0:
					continue
				else:
					dict_loc = {route[d] : [dict_loc, []]}
		
			dict_var[route[-1]] = [dict_loc, []]
		elif len(route) == 1 and not ai:
			variables['json'][0][route[0]] = [{}, [{variable_name : {variable_entry : input_value}}]]
		
		elif len(route) == 1 and ai:
			variables['json'][0][route[0]] = [{}, [{variable_name : {par_id : {variable_entry : input_value}}}]]
		
		elif not ai:
			variables['json'][1] = {variable_name : {variable_entry : input_value}}
		
		else:
			variables['json'][1] = {variable_name : {par_id : {variable_entry : input_value}}}
		
		return None
	
	if not found and ide + 1 >= len(path):
		foundy = False
		for item in dict_var[path[ide]][1]:
			if variable_name in item and not ai:
				item[variable_name][variable_entry] = input_value
				foundy = True
				break
			elif variable_name in item and ai:
				if par_id in item[variable_name]:
					item[variable_name][par_id][variable_entry] = input_value
				else:
					item[variable_name][par_id] = {variable_entry : input_value}
		if not foundy and not ai:
			dict_var[path[ide]][1].append({variable_name : {variable_entry : input_value}})
		
		return None
	
	elif not found:
		ide += 1
		recursive_variable_save(outer, dict_var[outer[ide - 1]][0], ide, path, variable_name, variable_entry, input_value, ai, par_id)
		
def recursive_variable_lookup(variable_name, variable_entry, path, dict_var, ide, ai):
	json_value = None
	if ide + 1 >= len(path) and ai and int(path[-1]) in variables[path[0]][1][0][variable_name]:
		if variable_entry in variables[path[0]][1][0][variable_name][int(path[-1])]:
			json_value = variables[path[0]][1][0][variable_name][int(path[-1])][variable_entry]
			return json_value
		else:
			json_value = variables[path[0]][1][0][variable_name][variable_entry]
			return json_value
		
		return json_value
	
	elif ide + 1 >= len(path) and ai:
		json_value = variables[path[0]][1][0][variable_name][variable_entry]
		return json_value
	elif ide + 1 >= len(path):
		
		for elements in variables[path[0]][1]:
			to_value = elements.copy()
			for key in [variable_name, variable_entry]:
				if isinstance(to_value, dict) and key in to_value:
					to_value = to_value[key]
				else:
					to_value = False
					break
			if to_value:
				json_value = to_value
				return json_value
		return json_value
		
	if path[ide] in dict_var:
		for elements in dict_var[path[ide]][1]:
			to_value = elements.copy()
			if ai:
				to_path = [variable_name, int(path[-1]), variable_entry]
			else:
				to_path = [variable_name, variable_entry]
			
			for key in to_path:
				if isinstance(to_value, dict) and key in to_value:                                                        
					to_value = to_value[key]                                                                            
				else:  
					to_value = False                                                                                      
					break                                            
				
			if to_value:
				json_value = to_value
				return json_value
		ide += 1
		json_value = recursive_variable_lookup(variable_name, variable_entry, path, dict_var[path[ide-1]][0], ide, ai)
		return json_value
			
	elif ai and int(path[-1]) in variables[path[0]][1][0][variable_name]:
		if variable_entry in variables[path[0]][1][0][variable_name][int(path[-1])]:
			json_value = variables[path[0]][1][0][variable_name][int(path[-1])][variable_entry]
			return json_value
		else:
			json_value = variables[path[0]][1][0][variable_name][variable_entry]
			return json_value
	elif ai:
		json_value = variables[path[0]][1][0][variable_name][variable_entry]
		return json_value
	
	else:
		return json_value

def custom_variable_assign(variable, path, input_value):
	ai, par_id = False, None
	path = path.split('.')[:-2]
	variable_name = variable.split('&')[0].strip()
	variable_entry = variable.split('&')[1].strip()
	recursive_variable_save(['json'], variables, 0, path, variable_name, variable_entry, input_value, ai, par_id)

def ai_variable_assign(variable, path, input_value):
	ai = True
	par_id = int(path.split('.')[-1])
	path = path.split('.')[:-2]
	variable_name = variable.split('&')[0].strip()
	variable_entry = variable.split('&')[1].strip()
	recursive_variable_save(['json'], variables, 0, path, variable_name, variable_entry, input_value, ai, par_id)

def ai_variable_value_extract(variable, path):
	ai = True
	original_path = path
	path = path.split('.')
	variable_name = variable.split('&')[0].strip()
	variable_entry = variable.split('&')[1].strip()
	del path[-2]
	
	if 'O' not in variable and 'D' not in variable:
		ai_var_value = recursive_variable_lookup(variable_name, variable_entry, path, variables, 0, ai)
		return ai_var_value
		
	else:
		variable_entries = ['M', 'I', 'P', 'S']
		ai_call_values = {}
		for entry in variable_entries:
			ai_call_values[entry] = recursive_variable_lookup(variable_name, entry, path, variables, 0, ai)
		ai_output = AI_Call(ai_call_values, original_path)
		ai_var_value = ai_output[variable_entry]
		return ai_var_value
	
	

def variable_value_extract(variable, path):
	ai = False
	path = path.split('.')
	variable_name = variable.split('&')[0].strip()
	variable_entry = variable.split('&')[1].strip()
	del path[-2]
	var_value = recursive_variable_lookup(variable_name, variable_entry, path, variables, 0, ai)
	return var_value

def json_parallel_value_call_extract(data):
	json_values = []
	parallel = data[data.find("(") + 1:data.find(")")]
	base = data.replace('(' + parallel + ')', '')
	for sub in parallel.split(','):
		for c in [' ', "'", '"']:
			sub = sub.strip(c)
		json_values.append(base + sub)
	return json_values

def shell_command_combiner(command, json_value):
	shell_commands = re.findall(r'\|>(.*?)<\|', command, re.DOTALL)
	if '&=' in shell_commands:
		shell_commands[shell_commands.index('&=')] = json_value
	shell_command = ' '.join(map(str, (shell_commands)))
	return shell_command

def shell_commands_extract(command, commands):
	commands_with_reference = []
	for command in commands:
		if '&=' in command:
			commands_with_reference.append(command)
	return commands_with_reference

def shell_commands_list(commands, commands_with_reference, json_values):
	shell_commands, ide = [], 0
	for i in range(len(commands_with_reference)):
			shell_commands.append(shell_command_combiner(commands_with_reference[i], json_values[i]))
	for i in range(len(commands)):
		if ide < len(commands_with_reference) and commands[i] in commands_with_reference[ide]:
			commands[i] = shell_commands[ide]
			ide += 1
		else:
			commands[i] = re.findall(r'\|>(.*?)<\|', commands[i], re.DOTALL)[0].strip()
	return commands

def shell_runtime_check(shell, shell_command, sid):
	if shell.proc.poll() is not None:
		raise RuntimeError(f"Shell died! Exit code: {shell.proc.poll()}, The command that caused it: {shell_command}, Shell id: {sid}")	
	
def command_value_run(command, json_value, path, commands, json_values):
	if not commands:
		shell_command = shell_command_combiner(command, json_value)
	else:
		commands_with_reference = shell_commands_extract(command, commands)
		commands = shell_commands_list(commands, commands_with_reference, json_values)
		shell_command = ' '.join(map(str, (commands)))
	sid = path.split('.')[-1]
	if sid not in shells:
			shells[sid] = Shell()
	shell = shells[sid]
	shell_runtime_check(shell, shell_command, sid)
	command_output = shell.run(shell_command)
	print(command_output)
	return command_output

def value_convert(data, assigner):
	if not data:
		return data
		
	if 'S' in assigner:
		for c in [' ', "'", '"']:
			data = data.strip(c)
		data = str(data)
		return data
		
	if 'I' in assigner and not isinstance(data, int):
		for c in [' ', "'", '"']:
			data = data.strip(c)
		data = int(data)
		return data
		
	if 'L' in assigner and not isinstance(data, list):
		for c in [' ', "'", '"']:
			data = data.strip(c)
		data = ast.literal_eval(data)
		return data
	
	if 'S' not in assigner and 'I' not in assigner and 'L' not in assigner:
		raise AttributeError(f'Something went horribly wrong as an invalid data_type specifier {assigner} has been passed to this function')
	
	return data

def file_value_convert(data):
	try:
		with open(data.strip(), 'r') as file:
			file_content = file.read()
			return file_content
	except:
		raise RuntimeError(f'There was an error reading the {data} file content.')
		
def file_value_save(file_name, content):
	for c in [' ', "'", '"']:
		file_name = file_name.strip(c)	
	file_name = str(file_name)
	
	try:
		with open(file_name, "w") as file:
    			file.write(content)
	except:
		raise RuntimeError(f'There was an error saving the {content} to file {file_name}.')

def json_data_value_extract(data):
	data = data.strip()
	data = re.sub(r'\|>|<\|', '', data, re.DOTALL)
	data = data.replace('.&=', '')
	json_value_variable_syntax(data)
	json_value_access = data
	if json_value_access:
		json_value = get_json_value_from_path(json, json_value_access)
		return json_value
	else:
		raise AttributeError(f'Something went horribly wrong as an invalid json_value_access has been extracted in this function')

def json_data_value_save(data, new_value):
	data = data.strip()
	data = re.sub(r'\|>|<\|', '', data, re.DOTALL)
	data = data.replace('.&=', '')
	json_value_access = data
	if json_value_access:
		save_json_value_to_path(json, json_value_access, new_value)
	else:
		raise AttributeError(f'Something went horribly wrong as an invalid json_value_access has been extracted in this function')

def command_exec(command, assigner, path, json_value, json_values, commands):
	if '(>' in command or '<)' in command:
		multiple_command_syntax(command, assigner)
		commands = multiple_command_extract(command)
	if '&=' in command and not commands:
		json_data_value_access_syntax(command, assigner)
		json_value = json_data_value_extract(command)
	elif '&=' in command:
		json_values = json_data_value_access_multiple_commands(commands, assigner, json_values)
	if '|>' in command and '<|' in command:
		command_value_syntax(command, assigner)
		command_output = command_value_run(command, json_value, path, commands, json_values)
		return command_output
	else:
		raise AttributeError(f'Something went horribly wrong at {command} with {assigner} which was passed as an invalid instruction to this function')
	
def commander_exec(command, assigner, path):
	json_value, json_values, commands = None, [], []
	if 'A&' in command:
		variable_value_access_syntax(command, assigner)
		output_value = ai_variable_value_extract(command, path)
		return output_value
	elif '&' in command and 'A&' not in command and '&=' not in command and ' &' not in command and '& ' not in command and command.count('&') <= 1:
		variable_value_access_syntax(command, assigner)
		output_value = variable_value_extract(command, path)
		return output_value
	elif '&=' in command and '|>' not in command and '<|' not in command:
		json_value_assign_syntax(command, assigner)
		output_value = json_value
		return output_value	
	elif '€' in assigner and '¤' not in assigner and command.count('.') == 1 and "'" not in command and '"' not in command and '. ' not in command and ' .' not in command:
		file_value_load_syntax(command, assigner)
		output_value = file_value_convert(command)
		return output_value
	elif '¤' in assigner:
		raw_value_syntax(command, assigner)
		output_value = value_convert(command, assigner)
		return output_value
	else:
		output_value = command_exec(command, assigner, path, json_value, json_values, commands)
		return output_value
	
def commanded_exec(command, assigner, input_value, path):
	json_value, json_values, commands = None, [], []
	if 'A&' in command:
		ai_variable_syntax(command)
		ai_variable_assign(command, path, input_value)
	if '&' in command and 'A&' not in command and '&=' not in command:
		custom_variable_syntax(command)
		custom_variable_assign(command, path, input_value)
	if '<$>' in command and '&=' in command:
		reference_variable_place_holder_syntax(command)
		command = reference_variable_place_holder_assign(command, assigner, input_value)
		command_exec(command, '#', path, json_value, json_values, commands)
	elif '<$>' in command:
		command = reference_variable_place_holder_assign(command, assigner, input_value)
		command_exec(command, '#', path, json_value, json_values, commands)
	
	elif '€' in assigner and '&' not in command and command.count('.') == 1 and "'" not in command and '"' not in command and '. ' not in command and ' .' not in command:
		 file_value_save_syntax(command, assigner)
		 file_value_save(command, input_value)
	
	return command

def command_line_stripper(data):
	commands = []
	if '(~|' in data and '|~)' in data:
		sub_commands = re.findall(r'~\|(.*?)\|~', data, re.DOTALL)
		for sub_command in sub_commands:
			commands.append(sub_command.strip())
	elif '~|' in data and '|~' in data:
		sub_command = data.removesuffix('|~')
		sub_command = sub_command.removeprefix('~|')
		commands.append(sub_command.strip())
	else:
		return None
	return commands

def data_stripper(data, key):
	if '<$' in data and '>' in data:
		json_variable_syntax(data)
	elif '&' in data and ';' in data:
		method_place_holder_syntax(data)
		method_value_extract(data, key)
	else:
		raise AttributeError(f'Something went horribly wrong at {data} which was passed as an invalid instruction to this function')

def command_stripper(command, path):
	json_value, commands, json_values = None, [], []
	assigners = re.findall(r'-(?:\[[^\]]*\]|[^|>\s\[]+)>|<(?!\|)[^<|\s-]+-', command, re.DOTALL)
	assign_from_right  = any(a.startswith('<') for a in assigners)                                                                  
	assign_from_left = any(a.endswith('>') for a in assigners)
	
	if assign_from_left and assign_from_right:
		raise SyntaxError(f"You can't assign at opposite directions in {data}. Only chained assignments are allowed.")
	
	elif assign_from_left:
		parts = re.split('|'.join(map(re.escape, assigners)), command, re.DOTALL)
		for i in range(len(assigners)):
			chain_start_command_syntax(parts[0])
			input_value = commander_exec(parts[i], assigners[i], path)
			assigner_syntax(parts[i + 1], assigners[i])
			assigned_command_syntax(parts[i + 1], assigners[i])
			parts[i + 1] = commanded_exec(parts[i + 1], assigners[i], input_value, path)
	
	elif assign_from_right:
		parts = re.split('|'.join(map(re.escape, assigners)), command, re.DOTALL)
		parts = parts[::-1]
		assigners = assigners[::-1]
		for i in range(len(assigners)):
			chain_start_command_syntax(parts[0])
			input_value = commander_exec(parts[i], assigners[i], path)
			assigner_syntax(parts[i + 1], assigners[i])
			assigned_command_syntax(parts[i + 1], assigners[i])
			parts[i + 1] = commanded_exec(parts[i + 1], assigners[i], input_value, path)
	else:
		command_without_assignment_syntax(command)
		command_exec(command, '#', path, json_value, json_values, commands)

def json_data_remover(data):
	not_command = specifier_syntax(data)
	if not_command:
		special_value = data_syntax(not_command)
		return special_value
	else:
		command_syntax(data)
		return data

def get_json_value_from_path(data, path):
	path = path.replace('[', '.').replace(']', '')
	for part in path.split('.'):
		if part.isdigit():
			data = data[int(part)]
		else:
			data = data[part]
	return data

def save_json_value_to_path(data, path, value):
	path = path.replace('[', '.').replace(']', '')                                                                                                                                                                                      
	for part in path.split('.')[:-1]:                                                                                             
		if part.isdigit():                                                                                              
			data = data[int(part)]                                                                                
		else:                                                                                                           
			data = data[part]                                                                                     
                                                                                                                                                                                                                                                                                                                    
	if path.split('.')[-1].isdigit():                                                                                             
		data[int(path.split('.')[-1])] = value                                                                             
	else:                                                                                                               
		data[path.split('.')[-1]] = value

def API_Key_load(key_file):
	try:
		with open(key_file, 'r') as file:
			api_values = json_module.load(file)
	except:
		print(f'Message: Failed to load {key_file} file, only ollama models will be available for this session')
		return None
	return api_values	

def AI_Call(settings, path):
	Input, Prompt, Model, Service = settings['I'], settings['P'], settings['M'], settings['S']
	ai_model_syntax(Model, Service)
	
	if api_keys:
		key_entries = [["openai", "anthropic", "gemini", "xai"] ,{"openai" : "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "gemini": "GEMINI_API_KEY", "xai": "XAI_API_KEY"}]
		for api in key_entries[0]:
			os.environ[key_entries[1][api]] = api_keys[api]
	
	service_model = Service + "/" + Model
	call_parameters = [{'role': 'user', 'content': f'Input: {Input} | Prompt: {Prompt}'}]
	response = completion(model=service_model, messages=call_parameters)
	
	ai_response_variables = {}
	ai_response_variables['O'] = response['choices'][0]['message']['content']
	ai_response_variables['D'] = "Decision derive from output is not currently supported yet"
	
	for variable_entry in ai_response_variables:
		variable = str('A&' + variable_entry)
		input_value = ai_response_variables[variable_entry]
		ai_variable_assign(variable, path, input_value)
	
	return ai_response_variables
	
def Script_Load(arg):
	if len(arg) < 2:
		raise IndexError("You must provide an input jsom script.")
	elif not arg[1].endswith(".jsom"):
		raise ValueError("The input script must be a jsom file.")
	jsom_path = Path(arg[1])
	if not jsom_path.is_file():
		raise ValueError(f'The input: {jsom_path} file can not be found.')
	with open(jsom_path, 'r') as file:
		try:
			jsom_file = json_module.load(file)
		except:
			raise SyntaxError(f'Seems like that the {jsom_path} file is not a valid json. Make sure that it follows the basic json syntax.')
	return jsom_file	
	
def Instruction_Extract(data):
	for dictionary in data:
		for key, value in dictionary.items():
			commands = command_line_stripper(value)
			if commands:
				for command in commands:
					command_stripper(command, key)
			else:
				data_stripper(value, key)
	
def Jsom_Parse(data, lev):
	instructions = []
	if isinstance(data, dict):
		for i, (key, value) in enumerate(data.items()):
			instructions_node = Jsom_Parse(value, lev + [key])
			if instructions_node:
				instructions = instructions + instructions_node
	elif isinstance(data, list):
		nested = []
		instructions_leaf = []                                                                                        
		for k in range(len(data)):                                                                                          
			if isinstance(data[k], (dict, list)):                                                                    
				nested.append(data[k])
			elif data[k] is not None:
				instruction = json_data_remover(data[k])
				if instruction:
					path = ".".join(map(str, lev)) + '.' + str(k)
					instructions_leaf.append({path: instruction})
		if nested:
			for j in range(len(nested)):
				Jsom_Parse(nested[j], lev + [j])
		if instructions_leaf:
			return instructions_leaf
	else:
		raise SyntaxError(f'jsom data format is invalid. Every value should be contained inside arrays (even single ones).')
	if instructions:
		return instructions

def Main():
	global api_keys, json, instructions, variables, shells
	api_keys = API_Key_load('API_keys.json')
	json = Script_Load(sys.argv)
	instructions, variables, shells = Jsom_Parse(json, ['json']), {'json': [{}, [{'A': {'I': 'AI_input', 'O': 'AI_output', 'D': 'AI_decision', 'P': 'AI_prompt', 'M': 'llama3:latest', 'S': 'ollama'}}]]}, {}
	Instruction_Extract(instructions)

if __name__ == "__main__":
    Main()
