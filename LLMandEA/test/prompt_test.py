import requests

url = "https://openai.api2d.net/v1/chat/completions"

headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer fk-YOUR_FORWARD_KEY_HERE' # <-- 把 fkxxxxx 替换成你自己的 Forward Key，注意前面的 Bearer 要保留，并且和 Key 中间有一个空格。
}

prompt = "Task: Given a set of nodes with their coordinates, you need to\
find the shortest route that visits each node once and returns to\
the starting node. The task can be solved step-by-step by starting\
from the current node and iteratively choosing the next node.\
You should create a totally new strategy for me (different from\
the heuristics in the literature) to select the next node in each step,\
using information including the current node, destination node,\
unvisited nodes, and distances between them.\
Provide a brief description of the new algorithm and its\
corresponding code. The description must start with ‘<start_des>’ and\
end with ‘<end_des>’. The code function must called\
'select_next_node' that takes inputs 'current_node',\
'destination_node', 'unvisited_nodes', and 'distance_matrix', and\
outputs the 'next_node', where 'current_node', 'destination_node',\
'next_node', and 'unvisited_nodes' are node id.\
The code function must start with '<start_code>' and end with '<end_code>'\
Be creative and do not give additional explanation."


data = {
  "model": "gpt-3.5-turbo",
  "messages": [{"role": "user", "content": prompt}]
}

response = requests.post(url, headers=headers, json=data)

print("Status Code", response.status_code)
print("JSON Response ", response.json())

js = response.json()
print(js['choices'][0]['message']['content'])