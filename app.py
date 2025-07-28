import streamlit as st
import ollama
import networkx as nx
import graphviz

class GoalGraph:
    def __init__(self):
        if 'graph' not in st.session_state:
            st.session_state.graph = nx.DiGraph()

    def add_goal(self, goal_name, goal_type="instrumental"):
        st.session_state.graph.add_node(goal_name, type=goal_type)

    def add_dependency(self, from_goal, to_goal):
        st.session_state.graph.add_edge(from_goal, to_goal)

    def get_goals(self):
        return list(st.session_state.graph.nodes)

    def get_dependencies(self, goal_name):
        return list(st.session_state.graph.predecessors(goal_name))

    def get_graph(self):
        return st.session_state.graph

def main():
    st.title("Goal Setting with AI")

    goal_graph = GoalGraph()

    # Sidebar for model selection
    st.sidebar.title("Model Selection")
    models = [model['name'] for model in ollama.list()['models']]
    selected_model = st.sidebar.selectbox("Choose a model", models)

    # Main chat interface
    st.header("Chat with your AI Assistant")
    user_input = st.text_input("You:", "")

    if user_input:
        response = ollama.chat(model=selected_model, messages=[
            {
                'role': 'user',
                'content': user_input,
            },
        ])
        st.text_area("AI Assistant:", value=response['message']['content'], height=200, max_chars=None, key=None)

    # File uploader for context
    st.sidebar.title("Upload Context")
    uploaded_file = st.sidebar.file_uploader("Choose a file", type=['txt'])
    if uploaded_file is not None:
        string_data = uploaded_file.getvalue().decode("utf-8")
        st.sidebar.text_area("File Content:", value=string_data, height=200)
        if st.sidebar.button("Extract Goals"):
            # Simple goal extraction (add your logic here)
            goals = [line for line in string_data.split('\n') if line.strip()]
            for goal in goals:
                goal_graph.add_goal(goal)

    # Goal management
    st.sidebar.title("Goal Management")
    new_goal = st.sidebar.text_input("Add a new goal:")
    if st.sidebar.button("Add Goal"):
        if new_goal:
            goal_graph.add_goal(new_goal)

    goals = goal_graph.get_goals()
    if goals:
        from_goal = st.sidebar.selectbox("From Goal", goals, key="from_goal")
        to_goal = st.sidebar.selectbox("To Goal", goals, key="to_goal")
        if st.sidebar.button("Add Dependency"):
            goal_graph.add_dependency(from_goal, to_goal)

    # Display graph
    st.header("Goal Graph")
    graph = goal_graph.get_graph()
    if graph.nodes:
        dot = graphviz.Digraph()
        for node in graph.nodes:
            dot.node(node)
        for edge in graph.edges:
            dot.edge(edge[0], edge[1])
        st.graphviz_chart(dot)

if __name__ == "__main__":
    main()