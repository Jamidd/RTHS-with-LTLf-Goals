def extract_best_state(original_h, h, open_list):
    s = open_list.pop_task()
    return s, open_list
