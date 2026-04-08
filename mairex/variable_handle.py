def Save(outer, dict_var, ide, path, variable_name, variable_entry, input_value, var_type, par_id, variables):
	def custom_var_entry_find(par_id, k, input_value, key, declared_variable, entry, outer, variables):
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
		
		return found, variables
	
	def custom_var_entry_nested_check(found, entry, variable_entry, key, outer, input_value, par_id, declared_variable, k, variables):
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
		
		return found, variables
		
	def custom_var_entry_for_loop(found, key, entries, outer, variable_entry, input_value, par_id, declared_variable, k, variables):
		for entry, var_value in entries.items():
			if variable_entry in entry:
				found, variables = custom_var_entry_nested_check(found, entry, variable_entry, key, outer, input_value, par_id, declared_variable, k, variables)
		return found, variables
	
	def ai_var_nested_check(found, outer, key, k, input_value, declared_variable, par_id, entry, variables):
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
		
		return found, variables
	
	def ai_var_for_loop(found, key, ai_entries, outer, variable_entry, input_value, par_id, declared_variable, k, variables):
		for entry, var_value in ai_entries.items():
			if variable_entry in entry:
				found, variables = ai_var_nested_check(found, outer, key, k, input_value, declared_variable, par_id, entry, variables)
		return found, variables
	
	def ai_var_entry_for_loop(found, key, entries, outer, variable_entry, input_value, par_id, declared_variable, k, variables):
		for id_par, ai_entries in entries.items():
			if id_par == par_id:
				found, variables = ai_var_for_loop(found, key, ai_entries, outer, variable_entry, input_value, par_id, declared_variable, k, variables)
		return found, variables
	
	def variable_type_check(found, key, entries, outer, variable_entry, input_value, var_type, par_id, declared_variable, k, variables):
		if var_type == 'ai':
			found, variables = ai_var_entry_for_loop(found, key, entries, outer, variable_entry, input_value, par_id, declared_variable, k, variables)
		elif var_type == 'custom':
			found, variables = custom_var_entry_for_loop(found, key, entries, outer, variable_entry, input_value, par_id, declared_variable, k, variables)
		elif var_type == 'user':
			raise RuntimeError(f"Not implemented yet")
		else:
			raise AttributeError(f"Something went horribly wrong...")
		return found, variables
	
	def dict_var_check_nested_for_loops(found, key, value, outer, variable_name, variable_entry, input_value, var_type, par_id, variables):
		for k in range(len(value[1])):
			for declared_variable, entries in value[1][k].items():
				if variable_name in declared_variable:
					found, variables = variable_type_check(found, key, entries, outer, variable_entry, input_value, var_type, par_id, declared_variable, k, variables)
		return found, variables
	
	def main_dict_var_check(found, key, outer, dict_var, ide, path, variable_name, variable_entry, input_value, var_type, par_id, variables):
		for key, value in dict_var.items():
			if path[ide] in key:
				found, variables = dict_var_check_nested_for_loops(found, key, value, outer, variable_name, variable_entry, input_value, var_type, par_id, variables)
				break
		return found, key, variables
	
	def outer_update(key, outer):
		if key != outer[ide - 1]:
			outer.append(key)
		return outer
		
	
	def dict_loc_assign(route, var_type, par_id, variable_name, variable_entry, input_value):
		if var_type == 'ai':
			dict_loc = {route[0]: [{}, [{variable_name : {par_id : {variable_entry : input_value}}}]]}
		elif var_type == 'custom':
			dict_loc = {route[0]: [{}, [{variable_name : {variable_entry : input_value}}]]}
		elif var_type == 'user':
			raise RuntimeError(f"Not implemented yet")
		else:
			raise AttributeError(f"Something went horribly wrong...")
		return dict_loc
	
	def dict_var_assign(dict_var, dict_loc, route):
		for d in range(len(route) - 1):
			if d == 0:
				continue
			else:
				dict_loc = {route[d] : [dict_loc, []]}
		
		dict_var[route[-1]] = [dict_loc, []]
		return dict_var
		
	def variables_assign_edge(route, variable_name, variable_entry, input_value, par_id, variables):
		if var_type == 'ai':
			variables['json'][0][route[0]] = [{}, [{variable_name : {par_id : {variable_entry : input_value}}}]]
		elif var_type == 'custom':
			variables['json'][0][route[0]] = [{}, [{variable_name : {variable_entry : input_value}}]]
		elif var_type == 'user':
			raise RuntimeError(f"Not implemented yet")
		else:
			raise AttributeError(f"Something went horribly wrong...")
		return variables
		
	def variables_assign(variable_name, variable_entry, input_value, par_id, variables):
		if var_type == 'ai':
			variables['json'][1] = {variable_name : {par_id : {variable_entry : input_value}}}
		elif var_type == 'custom':
			variables['json'][1] = {variable_name : {variable_entry : input_value}}
		elif var_type == 'user':
			raise RuntimeError(f"Not implemented yet")
		else:
			raise AttributeError(f"Something went horribly wrong...")
		return variables
	
	def variables_assign_sec_edge(route, variable_name, variable_entry, input_value, par_id, variables, dict_loc, dict_var):
		if var_type == 'ai':
			dict_var[route[0]] = dict_loc[route[0]]
		elif var_type == 'custom':
			raise RuntimeError(f"Unkown territory might work might not")
			variables['json'][0][path[1]][0] = dict_loc
		elif var_type == 'user':
			raise RuntimeError(f"Not implemented yet")
		else:
			raise AttributeError(f"Something went horribly wrong...")
		return dict_var
	
	def route_length_check(route, dict_loc, dict_var, var_type, input_value, variables, path):
		if len(route) > 1:
			dict_var = dict_var_assign(dict_var, dict_loc, route)
		elif len(route) == 1 and len(path) == 2:
			variables = variables_assign_edge(route, variable_name, variable_entry, input_value, par_id, variables)
		elif len(route) == 1:
			dict_var = variables_assign_sec_edge(route, variable_name, variable_entry, input_value, par_id, variables, dict_loc, dict_var)
		else:
			variables = variables_assign(variable_name, variable_entry, input_value, par_id, variables)
		return variables, dict_var
	
	def path_at_key_check(path, var_type, par_id, ide, key, dict_var, variable_name, variable_entry, input_value, variables):
		route = path[path.index(path[ide]):]
		route = list(reversed(route))
		dict_loc = dict_loc_assign(route, var_type, par_id, variable_name, variable_entry, input_value)
		variables, dict_var = route_length_check(route, dict_loc, dict_var, var_type, input_value, variables, path)
		
		return variables, dict_var
		
	def par_id_to_item_check(par_id, item, variable_name, variable_entry, input_value):
		if par_id in item[variable_name]:
			item[variable_name][par_id][variable_entry] = input_value
		else:
			item[variable_name][par_id] = {variable_entry : input_value}
		return item
		
	def dict_var_for_loop(foundy, dict_var, variable_name, variable_entry, var_type, par_id, input_value, path, ide):
		for item in dict_var[path[ide]][1]:
			if var_type == 'custom' and variable_name in item:
				item[variable_name][variable_entry] = input_value
				foundy = True
				break
			elif var_type == 'ai' and variable_name in item:
				item = par_id_to_item_check(par_id, item, variable_name, variable_entry, input_value)
		return foundy
	
	
	def dict_var_type_check(foundy, dict_var, path, ide, variable_name, variable_entry, input_value):
		if var_type == 'custom' and not foundy:
			dict_var[path[ide]][1].append({variable_name : {variable_entry : input_value}})
			
		return dict_var
			
	def recursive_variable_save(outer, dict_var, ide, path, variable_name, variable_entry, input_value, var_type, par_id, variables):
		found, key = False, None
		found, key, variables = main_dict_var_check(found, key, outer, dict_var, ide, path, variable_name, variable_entry, input_value, var_type, par_id, variables)
		outer = outer_update(key, outer)
		
		if path[ide] != key:
			variables, dict_var = path_at_key_check(path, var_type, par_id, ide, key, dict_var, variable_name, variable_entry, input_value, variables)
			return variables
		
		if not found and ide + 1 >= len(path):
			foundy = False
			foundy = dict_var_for_loop(foundy, dict_var, variable_name, variable_entry, var_type, par_id, input_value, path, ide)
			dict_var = dict_var_type_check(foundy, dict_var, path, ide, variable_name, variable_entry, input_value)
			return variables
		elif not found:
			ide += 1
			variables = recursive_variable_save(outer, dict_var[outer[ide - 1]][0], ide, path, variable_name, variable_entry, input_value, var_type, par_id, variables)
		
		return variables
	
	variables = recursive_variable_save(outer, dict_var, ide, path, variable_name, variable_entry, input_value, var_type, par_id, variables)
	return variables

def Load(variables, variable_name, variable_entry, path, dict_var, ide, var_type):
	
	def ai_var_check_basic(variables, variable_name, variable_entry, path):
		if variable_entry in variables[path[0]][1][0][variable_name][int(path[-1])]:
			json_value = variables[path[0]][1][0][variable_name][int(path[-1])][variable_entry]
		else:
			json_value = variables[path[0]][1][0][variable_name][variable_entry]
	
		return json_value

	def ai_path_check_basic(variables, variable_name, variable_entry, path, dict_var, ide):
		json_value = None
		if ide + 1 >= len(path) and int(path[-1]) in variables[path[0]][1][0][variable_name]:
			json_value = ai_var_check_basic(variables, variable_name, variable_entry, path)
		elif ide + 1 >= len(path):
			json_value = variables[path[0]][1][0][variable_name][variable_entry]
	
		return json_value

	def var_check_nested_for_loop(to_value, variable_name, variable_entry):
		for key in [variable_name, variable_entry]:
			if isinstance(to_value, dict) and key in to_value:
				to_value = to_value[key]
			else:
				to_value = False
				break
		return to_value
	

	def custom_var_check(variables, variable_name, variable_entry, path, dict_var, ide):
		json_value = None
		for elements in variables[path[0]][1]:
			to_value = elements.copy()
			to_value = var_check_nested_for_loop(to_value, variable_name, variable_entry)
			if to_value:
				json_value = to_value
				return json_value
			return json_value
		return json_value
		
	def basic_lookup(variables, variable_name, variable_entry, path, dict_var, ide, var_type):
		if var_type == 'ai':
			json_value = ai_path_check_basic(variables, variable_name, variable_entry, path, dict_var, 	ide)
		elif var_type == 'custom':
			json_value = custom_var_check(variables, variable_name, variable_entry, path, dict_var, ide)
		elif var_type == 'user':
			raise RuntimeError(f"Not implemented yet")
		else:
			raise AttributeError(f"Something went horribly wrong...")
		
		return json_value

	def ai_var_check_advanced(variables, variable_name, variable_entry, path, ide):
		if variable_entry in variables[path[0]][1][0][variable_name][int(path[-1])]:
			json_value = variables[path[0]][1][0][variable_name][int(path[-1])][variable_entry]
		else:
			json_value = variables[path[0]][1][0][variable_name][variable_entry]
		
		return json_value
	
	def loop_if_elif_check(var_type, variable_name, variable_entry, path):
		if var_type == 'ai':
			to_path = [variable_name, int(path[-1]), variable_entry]
		elif var_type == 'custom':
			to_path = [variable_name, variable_entry]
		elif var_type == 'user':
			raise RuntimeError(f"Not implemented yet")
		else:
			raise AttributeError(f"Something went horribly wrong...")
		return to_path
	
	def recursive_nested_for_loop(to_path, to_value):
		for key in to_path:
			if isinstance(to_value, dict) and key in to_value:                                                        
				to_value = to_value[key]                                                                            
			else:  
				to_value = False                                                                                      
				break
		return to_value
	
	def recursion(variables, json_value, variable_name, variable_entry, path, dict_var, ide, var_type):
		if not json_value:
			ide += 1
			json_value = recursive_variable_lookup(variables, variable_name, variable_entry, path, dict_var[path[ide-1]][0], ide, var_type)
		return json_value
	
	def recursive_nested_if(to_value, json_value):
		if to_value:
			json_value = to_value
		return json_value
			
	def recursive_extract(variables, variable_name, variable_entry, path, dict_var, ide, var_type):
		json_value = None
		if path[ide] in dict_var:
			for elements in dict_var[path[ide]][1]:
				to_value = elements.copy()
				to_path = loop_if_elif_check(var_type, variable_name, variable_entry, path)
				to_value = recursive_nested_for_loop(to_path, to_value)
				json_value = recursive_nested_if(to_value, json_value)
			json_value = recursion(variables, json_value, variable_name, variable_entry, path, dict_var, ide, var_type)
		return json_value
	
	def ai_path_check_advanced(variables, variable_name, variable_entry, path, ide):
		if int(path[-1]) in variables[path[0]][1][0][variable_name]:
			json_value = ai_var_check_advanced(variables, variable_name, variable_entry, path, ide)
		else:
			json_value = variables[path[0]][1][0][variable_name][variable_entry]
		return json_value	
			
			
	def advanced_lookup(variables, variable_name, variable_entry, path, dict_var, ide, var_type):
		json_value = recursive_extract(variables, variable_name, variable_entry, path, dict_var, ide, var_type)
		if var_type == 'ai' and not json_value:
			json_value = ai_path_check_advanced(variables, variable_name, variable_entry, path, ide)
		return json_value
			
	def recursive_variable_lookup(variables, variable_name, variable_entry, path, dict_var, ide, var_type):
		json_value = basic_lookup(variables, variable_name, variable_entry, path, dict_var, ide, var_type)
		if not json_value:
			json_value = advanced_lookup(variables, variable_name, variable_entry, path, dict_var, ide, var_type)
		return json_value
	
	json_value = recursive_variable_lookup(variables, variable_name, variable_entry, path, dict_var, ide, var_type)
	
	return json_value
