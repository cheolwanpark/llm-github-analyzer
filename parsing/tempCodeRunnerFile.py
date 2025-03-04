    name = node.child_by_field_name("name").text.decode()
                if current_class:
                    results["classes"][current_class].append(name)  # Add under class
                else:
                    results["functions"].append(name)  # Top-level function