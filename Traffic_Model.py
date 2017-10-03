#This is the base class for traffic model, all the other classes will inherit from it
class Traffic_Model_class:
    # Constructor
    def __init__(self, m):
        self.model_type = m

    #Prints out the type
    def print_type(self):
        print(self.model_type)