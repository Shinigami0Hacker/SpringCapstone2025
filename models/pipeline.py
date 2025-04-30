class Module():
    def run(self):
      raise NotImplementedError("This method should be overridden by subclasses.")

class PipeLine():
    def __init__(self):
        pipe = []

    def add_module(self, module: Module):
        self.pipe.append(module)

    def run(self, input_data):
        output = input_data
        for module in self.pipe:
            output = module.run(output)
        return output
    