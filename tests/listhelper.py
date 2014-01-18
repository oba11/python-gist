def header_list_to_dict(headers_as_nested_list):
    keys = [x for x,y in headers_as_nested_list]    
    values = [y for x,y in headers_as_nested_list]
    return dict(zip(keys,values))