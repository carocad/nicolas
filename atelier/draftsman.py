
import networkx
import pyPeephole
from atelier import secretary

def sketch_graph(pkg_modules, builtin_modules):
	# Initialize a graph object
	graph = networkx.Graph()
	# Create the most basic node
	python = object()
	graph.add_node(id(python), type='object', name='object',
				  docstring=python.__doc__, filepath='builtin')

	# Add all the functions, classes and imports to the graph
	##  Also adds the details of each module
	for module, filepath in pkg_modules.items():
		ast_tree = pyPeephole.parse(filepath)
		if ast_tree is None: # in case of invalid syntax
			continue

		# Insert current module info
		module_info = secretary.get_module_info(module, ast_tree, filepath)
		graph.add_node(id(module), module_info)

		# Inser functions info
		for function in pyPeephole.get_functions(ast_tree):
			info = secretary.get_function_info(function, filepath)
			graph.add_node(id(function), info)
			graph.add_edge(id(module), id(function))

		# Insert classes info
		for classDef in pyPeephole.get_classes(ast_tree):
			info = secretary.get_class_info(classDef, filepath)
			graph.add_node(id(classDef), info)
			graph.add_edge(id(module), id(classDef))
			for method in pyPeephole.get_functions(classDef):
				info = secretary.get_function_info(method, filepath)
				graph.add_node(id(method), info)
				graph.add_edge(id(classDef), id(method))

		# Insert imports info
		for importDef in pyPeephole.get_imports(ast_tree):
			for alias in importDef.names:
				info = secretary.get_import_info(importDef, alias, filepath)
				graph.add_node(id(alias), info)
				graph.add_edge(id(alias), id(module))
				if info['name'] in pkg_modules:
					relation_id = secretary.get_module_id(pkg_modules, info['name'])
					graph.add_edge(id(alias), relation_id)
				elif info['name'] in builtin_modules:
					graph.add_edge(id(python), id(alias))
				else: # Unknown module
					graph.add_edge(id(python), id(alias))

		# Insert from ... import info
		for importFrom in pyPeephole.get_importsFrom(ast_tree):
			info = secretary.get_importFrom_info(importFrom, filepath)
			graph.add_node(id(importFrom), info)
			graph.add_edge(id(importFrom), id(module))
			if info['name'] in pkg_modules:
				relation_id = secretary.get_module_id(pkg_modules, info['name'])
				graph.add_edge(id(alias), relation_id)
			elif info['name'] in builtin_modules:
				graph.add_edge(id(python), id(importFrom))
			else: # Unknown module
				graph.add_edge(id(python), id(importFrom))

	return graph
