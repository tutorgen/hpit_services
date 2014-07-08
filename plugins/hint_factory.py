# from client import Plugin

from bulbs.model import Node, Relationship
from bulbs.neo4jserver import Graph
from bulbs import property as prop
from bulbs.utils import current_datetime

class MDPProblemNode(Node):
    element_type = "mdp_problem"

    created = prop.DateTime(default=current_datetime, nullable=False)
    start_text = prop.String()
    goal_text = prop.String()


class MDPStateNode(Node):
    element_type = "mdp_state"

    created = prop.DateTime(default=current_datetime, nullable=False)
    reward = prop.Float(default=0.0)
    bellman_value = prop.Float(default=0.0)


class MDPAction(Relationship):
    label = "action"

    created = prop.DateTime(default=current_datetime, nullable=False)
    probability = prop.Float(default=0.0)


class MasterGraph(Graph):

    def __init__(self):
        super().__init__()
        self.add_proxy("problems", MDPProblemNode)
        self.add_proxy("states", MDPStateNode)
        self.add_proxy("actions", MDPAction)


    def create_problem(self, start_text, goal_text):

        exists = self.find_problem(start_text, goal_text)
        if exists:
            return exists

        #Create the problem
        new_problem = self.problems.create(start_text=start_text, goal_text=goal_text)

        return new_problem


    def find_problem(self, start_text, goal_text):
        nodes = self.problems.index.lookup(start_text=start_text, goal_text=goal_text)

        #Only one should exists
        return next(nodes) if nodes else None


    def perform_value_iterator(self, problem):
        pass


    def add_problem_state(self, problem, old_state, new_state):
        pass


# class HintFactoryPlugin(Plugin):

#     def __init__(self, entity_id, api_key, logger, args = None):
#         super().__init__(entity_id, api_key)
#         self.logger = logger
#         self.db = MasterGraph()


#     def post_connect(self):
#         super().post_connect()

#         self.subscribe(
#             hf_init_problem=self.init_problem_callback, 
#             hf_push_state=self.push_state_callback,
#             hf_hint_exists=self.hint_exists_callback,
#             hf_get_hint=self.get_hint_callback)

#     #Hint Factory Plugin
#     def init_problem_callback(self, message):
#         """
#             problem_text - The text of the problem
#             problem_goal_text - The goal of the problem
#         """
#         self.logger.debug("INIT PROBLEM")
#         self.logger.debug(message)

#     def push_state_callback(self, message):
#         self.logger.debug("PUSH PROBLEM STATE")
#         self.logger.debug(message)

#     def hint_exists_callback(self, message):
#         self.logger.debug("HINT EXISTS")
#         self.logger.debug(message)

#     def get_hint_callback(self, message):
#         self.logger.debug("GET HINT")
#         self.logger.debug(message)


if __name__ == '__main__':
    db = MasterGraph()
    import pdb; pdb.set_trace()
    problem = db.create_problem('4x-6=10', 'x=4')
    x = 5

